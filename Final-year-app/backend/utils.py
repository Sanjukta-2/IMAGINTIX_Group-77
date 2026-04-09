
# ============================================================
#  utils.py  — fixed for generator_refined.keras
# ============================================================

import numpy as np
from PIL import Image
import tensorflow as tf

# ── Register custom layer BEFORE loading model ───────────────
@tf.keras.utils.register_keras_serializable()
class ResidualBlock(tf.keras.layers.Layer):
    def __init__(self, filters=64, **kwargs):
        super().__init__(**kwargs)
        self.filters = filters
        self.conv1 = tf.keras.layers.Conv2D(filters, 3, padding='same', use_bias=False)
        self.conv2 = tf.keras.layers.Conv2D(filters, 3, padding='same', use_bias=False)
        self.norm1 = tf.keras.layers.LayerNormalization(axis=[1, 2])
        self.norm2 = tf.keras.layers.LayerNormalization(axis=[1, 2])
        self.relu  = tf.keras.layers.ReLU()
        self.add   = tf.keras.layers.Add()

    def call(self, x):
        skip = x
        x = self.relu(self.norm1(self.conv1(x)))
        x = self.norm2(self.conv2(x))
        return self.add([x, skip])

    def get_config(self):
        config = super().get_config()
        config.update({"filters": self.filters})
        return config


IMG_SIZE = 256   # must match training — do not change


def preprocess_image_cloud(image: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns (gen_input, cloud_mask) where:
      gen_input  shape [1, 256, 256, 4]  — RGB + mask channel
      cloud_mask shape [256, 256, 1]     — for compositing later
    """
    # Resize to training resolution
    image = image.resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
    img   = np.array(image).astype("float32")

    # Normalize to [-1, 1]
    img = img / 127.5 - 1.0                          # [256, 256, 3]

    # Cloud mask: bright pixels are likely clouds
    # (same heuristic used at inference time during training)
    gray      = np.mean(img, axis=-1, keepdims=True)  # [256, 256, 1]
    cloud_mask = (gray > 0.6).astype("float32")       # 1 = cloud, 0 = clear

    # Concatenate mask as 4th channel
    gen_input = np.concatenate([img, cloud_mask], axis=-1)  # [256, 256, 4]
    gen_input = np.expand_dims(gen_input, axis=0)           # [1, 256, 256, 4]

    return gen_input, cloud_mask


def postprocess_image_cloud(pred: np.ndarray) -> Image.Image:
    """Converts model output [1, 256, 256, 3] back to a PIL image."""
    pred = pred[0]                              # remove batch dim → [256, 256, 3]
    pred = (pred + 1.0) * 127.5                # [-1,1] → [0,255]
    pred = np.clip(pred, 0, 255).astype("uint8")
    return Image.fromarray(pred)


def composite_output(
    original: np.ndarray,
    prediction: np.ndarray,
    cloud_mask: np.ndarray,
    blend_px: int = 5
) -> np.ndarray:
    """
    Replaces only cloudy pixels with the model prediction.
    Clear pixels are taken directly from the original — pixel-perfect.

    original   : [256, 256, 3]  float32 in [-1, 1]
    prediction : [256, 256, 3]  float32 in [-1, 1]
    cloud_mask : [256, 256, 1]  float32 0/1
    """
    if blend_px > 0:
        # Soften mask edges to avoid hard seams at cloud boundaries
        kernel     = np.ones((blend_px, blend_px), np.float32) / (blend_px ** 2)
        from scipy.ndimage import convolve
        soft_mask  = convolve(cloud_mask[:, :, 0], kernel)[:, :, np.newaxis]
        soft_mask  = np.clip(soft_mask, 0.0, 1.0)
    else:
        soft_mask = cloud_mask

    return original * (1.0 - soft_mask) + prediction * soft_mask


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
