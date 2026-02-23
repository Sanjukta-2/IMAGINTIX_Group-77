from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
from PIL import Image

from utils import preprocess_image, postprocess_image
from models import run_inference

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

    # Preprocess → GAN → Postprocess
    image_array = preprocess_image(image)
    prediction = run_inference(image_array)
    output_image = postprocess_image(prediction)

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
