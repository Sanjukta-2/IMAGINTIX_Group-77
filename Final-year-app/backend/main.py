import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
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


@app.post("/api/color-processing")
async def color_processing(
    file: UploadFile = File(...),
    # color_mode: str = Form(...)
):
    file_ext = file.filename.split(".")[-1]
    input_name = f"{uuid.uuid4()}.{file_ext}"
    input_path = os.path.join(UPLOAD_DIR, input_name)

    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Open image
    image = Image.open(input_path).convert("RGB")

    # Preprocess
    image_array = preprocess_image(image, size=(256,256))

    # 👇 Use GAN instead of manual processing
    prediction = run_color_inference(image_array)

    # Postprocess
    output_image = postprocess_image(prediction)

    # Save output
    output_name = f"color_{input_name}.png"
    output_path = os.path.join(OUTPUT_DIR, output_name)
    output_image.save(output_path)

    return {
        "image_url": f"http://localhost:8000/api/image/{output_name}"
    }

    
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
