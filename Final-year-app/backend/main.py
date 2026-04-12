import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
import os
import uuid
import io
from PIL import Image
import tensorflow as tf
from utils import (
    ResidualBlock,          # import triggers @register decorator
    preprocess_image,
    postprocess_image,
    composite_output,
    preprocess_image_cloud,
    postprocess_image_cloud,
    IMG_SIZE,
)
from models import run_inference, run_color_inference

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/api/debug-mask")
async def debug_mask(file: UploadFile = File(...)):
    contents = await file.read()
    image    = Image.open(io.BytesIO(contents)).convert("RGB")

    gen_input, cloud_mask = preprocess_image_cloud(image)
    orig_256 = image.resize((256, 256))
    orig_arr = np.array(orig_256).astype("float32")

    r, g, b    = orig_arr[:,:,0], orig_arr[:,:,1], orig_arr[:,:,2]
    brightness = (r + g + b) / 3.0
    max_c      = np.maximum(np.maximum(r, g), b)
    min_c      = np.minimum(np.minimum(r, g), b)
    sat        = np.where(max_c > 1e-5, (max_c - min_c) / max_c, 0.0)
    mean_rgb   = brightness
    deviation  = (np.abs(r-mean_rgb)+np.abs(g-mean_rgb)+np.abs(b-mean_rgb))/(mean_rgb+1e-5)

    from scipy.ndimage import gaussian_filter
    local_avg      = gaussian_filter(brightness, sigma=12)
    local_contrast = brightness - local_avg

    # Individual cue visualizations
    panels = {
        "Original":       orig_arr,
        "Final mask":     np.stack([cloud_mask[:,:,0]*255]*3, axis=-1),
        "Brightness":     np.stack([np.clip(brightness,0,255)]*3, axis=-1),
        "Saturation":     np.stack([np.clip(sat*255,0,255)]*3, axis=-1),
        "Whiteness dev":  np.stack([np.clip(deviation*255,0,255)]*3, axis=-1),
        "Local contrast": np.stack([np.clip((local_contrast+30)*4,0,255)]*3, axis=-1),
    }

    # Red overlay on final mask
    overlay = orig_arr.copy()
    m = cloud_mask[:,:,0]
    overlay[:,:,0] = np.clip(orig_arr[:,:,0] + m * 90, 0, 255)
    overlay[:,:,1] = np.clip(orig_arr[:,:,1] - m * 50, 0, 255)
    overlay[:,:,2] = np.clip(orig_arr[:,:,2] - m * 50, 0, 255)
    panels["Overlay"] = overlay

    keys   = list(panels.keys())
    n      = len(keys)
    combined = Image.new("RGB", (256 * n, 300))   # extra 44px for labels

    from PIL import ImageDraw
    draw = ImageDraw.Draw(combined)

    for i, key in enumerate(keys):
        arr = panels[key].astype("uint8")
        combined.paste(Image.fromarray(arr), (256 * i, 44))
        draw.text((256 * i + 4, 4), key, fill=(200, 200, 200))
        cov = (panels[key][:,:,0] > 127).mean() * 100 if key != "Original" else 0
        if key not in ("Original", "Overlay"):
            draw.text((256 * i + 4, 22), f"{cov:.1f}%", fill=(150,150,150))

    coverage = float(cloud_mask.mean() * 100)
    buf = io.BytesIO()
    combined.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type = "image/png",
        headers    = {"X-Cloud-Coverage": f"{coverage:.1f}%"}
    )
    
@app.post("/api/cloud-removal")
async def cloud_removal(file: UploadFile = File(...)):
    # Save uploaded image
    file_ext = file.filename.split(".")[-1]
    input_name = f"{uuid.uuid4()}.{file_ext}"
    input_path = os.path.join(UPLOAD_DIR, input_name)

    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Open image
    image = Image.open(input_path).convert("RGB")

    # Remember original size to restore after inference
    original_size = image.size   # (width, height)

    gen_input, cloud_mask = preprocess_image_cloud(image)   # [1,256,256,4], [256,256,1]

    # ── Inference ────────────────────────────────────────────
    prediction = run_inference(gen_input)              # [1,256,256,3]

    # ── Composite: replace only cloud pixels ─────────────────
    original_rgb = gen_input[0, :, :, :3]             # [256,256,3] in [-1,1]
    composited   = composite_output(
        original   = original_rgb,
        prediction = prediction[0],
        cloud_mask = cloud_mask,
        blend_px   = 5
    )                                                  # [256,256,3] in [-1,1]

    # ── Postprocess ──────────────────────────────────────────
    output_image = postprocess_image_cloud(composited[np.newaxis])  # PIL Image at 256×256

    # Restore to original uploaded resolution
    if original_size != (IMG_SIZE, IMG_SIZE):
        output_image = output_image.resize(original_size, Image.BILINEAR)

    # # Preprocess → GAN → Postprocess
    # image_array = preprocess_image(image,size=(128,128))
    # prediction = run_inference(image_array)
    # output_image = postprocess_image(prediction)

    # Save output
    output_name = f"processed_{input_name}.png"
    output_path = os.path.join(OUTPUT_DIR, output_name)
    output_image.save(output_path)

    return {
        "image_url": f"http://localhost:8000/api/image/{output_name}"
    }


@app.get("/api/image/{filename}")
def get_image(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    return FileResponse(path)
