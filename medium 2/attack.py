import tensorflow as tf
import numpy as np
from PIL import Image
import os

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'fashion_classifier.h5')
IMAGE_PATH = os.path.join(BASE_DIR, 'extracted_assets/images/class_0_img_19.png') # Placeholder image
CLASS_NAMES_PATH = os.path.join(BASE_DIR, 'class_names.txt')
OUTPUT_IMAGE_PATH = os.path.join(BASE_DIR, 'adversarial_image.png')

def load_class_names(path):
    with open(path, 'r') as f:
        class_names = [line.strip() for line in f.readlines()]
    return class_names

def load_and_preprocess_image(path):
    img = Image.open(path).convert('L') # Convert to grayscale
    img = img.resize((28, 28))
    img_array = np.array(img)
    img_array = img_array / 255.0 # Normalize to [0, 1]
    img_array = img_array.reshape(1, 28, 28, 1)
    return img_array

def create_adversarial_pattern(input_image, input_label, model):
    loss_object = tf.keras.losses.SparseCategoricalCrossentropy()

    with tf.GradientTape() as tape:
        tape.watch(input_image)
        prediction = model(input_image)
        loss = loss_object(input_label, prediction)

    gradient = tape.gradient(loss, input_image)
    signed_grad = tf.sign(gradient)
    return signed_grad

def main():
    # 1. Load Model
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}")
        return
    
    try:
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        print("Model loaded successfully.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error loading model: {e}")
        return

    # 2. Load Class Names
    if os.path.exists(CLASS_NAMES_PATH):
        class_names = load_class_names(CLASS_NAMES_PATH)
    else:
        print("Warning: class_names.txt not found. Using default indices.")
        class_names = [str(i) for i in range(10)]

    # 3. Load Image
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image file not found at {IMAGE_PATH}")
        return
    
    image = load_and_preprocess_image(IMAGE_PATH)
    image_tensor = tf.convert_to_tensor(image, dtype=tf.float32)

    # 4. Get Initial Prediction
    predictions = model.predict(image_tensor)
    initial_class_idx = np.argmax(predictions[0])
    initial_class_name = class_names[initial_class_idx] if initial_class_idx < len(class_names) else str(initial_class_idx)
    print(f"Initial Prediction: {initial_class_name} (Confidence: {predictions[0][initial_class_idx]:.2f})")

    # 5. Perform FGSM Attack
    # Get the label for the image (using the model's prediction as truth for the attack if no label provided)
    label = tf.constant([initial_class_idx])
    
    perturbations = create_adversarial_pattern(image_tensor, label, model)
    
    # Epsilon is the magnitude of the perturbation
    epsilon = 0.05 
    adv_x = image_tensor + epsilon * perturbations
    adv_x = tf.clip_by_value(adv_x, 0, 1)

    # 6. Check Adversarial Prediction
    adv_predictions = model.predict(adv_x)
    adv_class_idx = np.argmax(adv_predictions[0])
    adv_class_name = class_names[adv_class_idx] if adv_class_idx < len(class_names) else str(adv_class_idx)
    
    print(f"Adversarial Prediction: {adv_class_name} (Confidence: {adv_predictions[0][adv_class_idx]:.2f})")

    if initial_class_idx != adv_class_idx:
        print("SUCCESS: Model fooled!")
    else:
        print("FAILED: Model not fooled. Try increasing epsilon.")

    # 7. Save Adversarial Image
    adv_img_array = adv_x.numpy().reshape(28, 28)
    adv_img_array = (adv_img_array * 255).astype(np.uint8)
    adv_img = Image.fromarray(adv_img_array)
    adv_img.save(OUTPUT_IMAGE_PATH)
    print(f"Adversarial image saved to {OUTPUT_IMAGE_PATH}")

if __name__ == "__main__":
    main()
