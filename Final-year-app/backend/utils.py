import numpy as np
from PIL import Image


def preprocess_image(image: Image.Image, size=(128, 128)) -> np.ndarray:
    # Resize exactly like training
    image = image.resize(size)
    # Convert to numpy
    image = np.array(image).astype("float32")
    # Normalize to [-1, 1]
    image = image / 127.5 - 1.0
    # Add batch dimension
    image = np.expand_dims(image, axis=0)

    return image

def preprocess_color_image(image: Image.Image) -> np.ndarray:
    return preprocess_image(image) 

def postprocess_image(pred: np.ndarray) -> Image.Image:
    # Remove batch dimension
    pred = pred[0]

    # Convert from [-1, 1] → [0, 255]
    pred = (pred + 1) * 127.5
    pred = np.clip(pred, 0, 255).astype("uint8")

    return Image.fromarray(pred)
