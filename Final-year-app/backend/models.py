import tensorflow as tf

MODEL_PATH = "C:/Mahika/Projects/Imagintix/IMAGINTIX_Group-77/Final-year-app/backend/generator_final.keras"
generator = tf.keras.models.load_model(MODEL_PATH, compile=False)

COLOR_MODEL_PATH = "C:/Mahika/Projects/Imagintix/IMAGINTIX_Group-77/Final-year-app/backend\generator (1).keras"
color_generator = tf.keras.models.load_model(COLOR_MODEL_PATH, compile=False)


def run_inference(image_array):
    prediction = generator.predict(image_array)
    return prediction

def run_color_inference(image_array):
    return color_generator.predict(image_array)
