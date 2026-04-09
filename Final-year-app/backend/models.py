import tensorflow as tf
from utils import ResidualBlock
import numpy as np
MODEL_PATH = "C:/Mahika/Projects/Imagintix/IMAGINTIX_Group-77/Final-year-app/backend/generator_refined.keras"
#generator = tf.keras.models.load_model(MODEL_PATH, compile=False)
generator = tf.keras.models.load_model(
    MODEL_PATH,
    custom_objects = {"ResidualBlock": ResidualBlock},
    compile        = False
)

COLOR_MODEL_PATH = "C:/Mahika/Projects/Imagintix/IMAGINTIX_Group-77/Final-year-app/backend\generator (1).keras"
color_generator = tf.keras.models.load_model(COLOR_MODEL_PATH, compile=False)

def run_inference(gen_input: np.ndarray) -> np.ndarray:
    """Runs TTA (8-way) inference and returns averaged prediction."""
    preds = []
    x = tf.constant(gen_input)   # [1, 256, 256, 4]

    for flip_lr in [False, True]:
        for flip_ud in [False, True]:
            aug = x
            if flip_lr: aug = tf.image.flip_left_right(aug)
            if flip_ud: aug = tf.image.flip_up_down(aug)

            pred = generator(aug, training=False).numpy()

            if flip_ud: pred = pred[:, ::-1, :, :]
            if flip_lr: pred = pred[:, :, ::-1, :]

            preds.append(pred)

    return np.mean(preds, axis=0)   # [1, 256, 256, 3]

# def run_inference(image_array):
# prediction = generator.predict(image_array)
# return prediction

def run_color_inference(image_array):
    return color_generator.predict(image_array)
