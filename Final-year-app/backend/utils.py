
# ============================================================
#  utils.py  — fixed for generator_refined.keras
# ============================================================

import numpy as np
from PIL import Image
import tensorflow as tf
import numpy as np
from scipy.ndimage import convolve
import logging

logger = logging.getLogger(__name__)
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
    image = image.resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
    img   = np.array(image).astype("float32")   # [256,256,3] in [0,255]

    r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]

    # ── Cue 1: brightness (catches thick white clouds) ───────
    brightness   = (r + g + b) / 3.0
    bright_mask  = brightness > 160.0           # lowered from 180

    # ── Cue 2: low saturation (grey/white haze) ──────────────
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    sat   = np.where(max_c > 1e-5, (max_c - min_c) / max_c, 0.0)
    low_sat_mask = sat < 0.30                   # raised from 0.25

    # ── Cue 3: blue-green dominance ──────────────────────────
    # Thin clouds over vegetation look greenish-white.
    # Their blue and green channels are both elevated vs red.
    blue_green_dominant = ((b > r * 0.85) & (g > r * 0.80) & (brightness > 130.0))

    # ── Cue 4: whiteness ratio ────────────────────────────────
    # True clouds have R≈G≈B. Measure how close to grey.
    mean_rgb  = (r + g + b) / 3.0
    deviation = (np.abs(r - mean_rgb) +
                 np.abs(g - mean_rgb) +
                 np.abs(b - mean_rgb)) / (mean_rgb + 1e-5)
    whiteness_mask = (deviation < 0.18) & (brightness > 120.0)

    # ── Cue 5: relative brightness vs local neighbourhood ────
    # Clouds are locally brighter than surrounding pixels.
    # Use a blurred version as "local average" and find pixels
    # significantly brighter than their surroundings.
    from scipy.ndimage import uniform_filter, gaussian_filter
    local_avg      = gaussian_filter(brightness, sigma=12)
    local_contrast = brightness - local_avg
    local_bright   = local_contrast > 12.0      # 12 DN above local avg

    # ── Combine all cues ──────────────────────────────────────
    # Strategy: be inclusive — catch anything that looks cloud-like
    cloud_mask = (
        (bright_mask & low_sat_mask)        |   # thick white clouds
        (whiteness_mask & local_bright)     |   # thin haze, locally bright
        (blue_green_dominant & local_bright)|   # semi-transparent clouds
        (bright_mask & whiteness_mask)          # bright + white regardless of contrast
    ).astype("float32")

    # ── Morphological operations ──────────────────────────────
    from scipy.ndimage import binary_dilation, binary_erosion, binary_fill_holes

    # Fill small holes inside detected cloud regions
    cloud_bool = cloud_mask.astype(bool)
    cloud_bool = binary_fill_holes(cloud_bool)

    # Erode slightly to remove noise specks (single bright pixels)
    cloud_bool = binary_erosion(cloud_bool,
                                structure=np.ones((2, 2)))

    # Dilate to grow cloud edges — clouds have soft gradual boundaries
    cloud_bool = binary_dilation(cloud_bool,
                                 structure=np.ones((9, 9)))

    cloud_mask = cloud_bool.astype("float32")

    # ── Diagnostic ───────────────────────────────────────────
    coverage = cloud_mask.mean() * 100
    logger.info(
        f"Cloud coverage: {coverage:.1f}%  |  "
        f"bright+lowsat: {(bright_mask & low_sat_mask).mean()*100:.1f}%  |  "
        f"whiteness+local: {(whiteness_mask & local_bright).mean()*100:.1f}%  |  "
        f"bg_dominant: {(blue_green_dominant & local_bright).mean()*100:.1f}%"
    )

    if coverage < 1.0:
        logger.warning("Mask still nearly empty — image may be cloud-free "
                       "or thresholds need further lowering.")

    # ── Normalize and build 4-channel input ──────────────────
    img_norm      = img / 127.5 - 1.0
    cloud_mask_ch = cloud_mask[:, :, np.newaxis]          # [256,256,1]
    gen_input     = np.concatenate([img_norm, cloud_mask_ch], axis=-1)
    gen_input     = np.expand_dims(gen_input, axis=0)     # [1,256,256,4]

    return gen_input, cloud_mask_ch

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
