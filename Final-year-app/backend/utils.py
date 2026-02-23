import numpy as np
from PIL import Image

IMG_SIZE = (128, 128)

def preprocess_image(image: Image.Image) -> np.ndarray:
    # Resize exactly like training
    image = image.resize(IMG_SIZE)

    # Convert to numpy
    image = np.array(image).astype("float32")

    # Normalize to [-1, 1]
    image = image / 127.5 - 1.0

    # Add batch dimension
    image = np.expand_dims(image, axis=0)

    return image


def postprocess_image(pred: np.ndarray) -> Image.Image:
    # Remove batch dimension
    pred = pred[0]

    # Convert from [-1, 1] → [0, 255]
    pred = (pred + 1) * 127.5
    pred = np.clip(pred, 0, 255).astype("uint8")

    return Image.fromarray(pred)
