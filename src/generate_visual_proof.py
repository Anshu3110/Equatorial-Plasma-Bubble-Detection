import os
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import glob
from src.inference_utils import predict_anomaly

# Configuration
MODEL_PATH = "models/autoencoder_epb_final.h5"
DATA_DIR = "data/processed/images_224x224"
OUTPUT_DIR = "results/metrics"

def generate_visual_proof():
    if not os.path.exists(MODEL_PATH):
        print("Model not found.")
        return

    model = tf.keras.models.load_model(MODEL_PATH)
    image_files = glob.glob(os.path.join(DATA_DIR, "*.png"))
    
    if not image_files:
        print("No images found.")
        return

    # Find the image with the highest error (Best example of a detection)
    highest_mse = 0
    best_img_path = ""
    
    print("Scanning for the best anomaly example...")
    # Scan a subset for speed, or all if feasible. Let's do first 100 or until we find a good one.
    # Actually, let's just pick one we know is high from previous logs or random
    # Better: Scan all to find the MAX anomaly
    
    for img_path in image_files:
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None: continue
        img = cv2.resize(img, (224, 224))
        img_norm = img.astype('float32') / 255.0
        img_batch = np.expand_dims(img_norm, axis=0) # Add batch dim
        img_batch = np.expand_dims(img_batch, axis=-1) # Add channel dim
        
        # Fast predict
        mse = model.evaluate(img_batch, img_batch, verbose=0)
        if mse > highest_mse:
            highest_mse = mse
            best_img_path = img_path
            
    print(f"Selected Example: {os.path.basename(best_img_path)} (MSE: {highest_mse:.4f})")
    
    # Process the best example for visualization
    orig_img = cv2.imread(best_img_path, cv2.IMREAD_GRAYSCALE)
    orig_img = cv2.resize(orig_img, (224, 224))
    img_norm = orig_img.astype('float32') / 255.0
    img_batch = np.expand_dims(img_norm, axis=0)
    img_batch = np.expand_dims(img_batch, axis=-1)
    
    # Get Reconstruction
    reconstruction = model.predict(img_batch, verbose=0)
    reconstruction = np.squeeze(reconstruction) * 255.0
    reconstruction = reconstruction.astype('uint8')
    
    # Get Difference
    diff = cv2.absdiff(orig_img, reconstruction)
    # Enhance contrast of difference for visibility
    diff_enhanced = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
    
    # Plot
    plt.figure(figsize=(12, 4))
    
    # 1. Original
    plt.subplot(1, 3, 1)
    plt.imshow(orig_img, cmap='inferno')
    plt.title(f"Original Input\n(Satellite Scan)")
    plt.axis('off')
    
    # 2. Reconstruction
    plt.subplot(1, 3, 2)
    plt.imshow(reconstruction, cmap='inferno')
    plt.title(f"AI Reconstruction\n(Learned 'Normal' Pattern)")
    plt.axis('off')
    
    # 3. Difference (Anomaly)
    plt.subplot(1, 3, 3)
    plt.imshow(diff, cmap='magma')
    plt.title(f"Residual Map\n(The Detected Plasma Bubble)")
    plt.axis('off')
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_path = os.path.join(OUTPUT_DIR, "visual_proof.png")
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Visual proof saved to {save_path}")

if __name__ == "__main__":
    generate_visual_proof()
