import os
import glob
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from model import build_autoencoder

# Configuration
DATA_DIR = "data/processed/images_224x224"
MODEL_DIR = "models"
RESULTS_DIR = "results/reconstructions"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 50

def load_data():
    """Load all images from processed directory (Unsupervised - No Labels)"""
    files = glob.glob(os.path.join(DATA_DIR, "*.png"))
    print(f"Found {len(files)} images.")
    
    if len(files) == 0:
        print("No images found! Run data_loader.py and preprocessing.py first.")
        return np.array([])
        
    images = []
    for f in files:
        # Read as grayscale
        img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        # Resize if needed (should already be 224x224)
        if img.shape != IMG_SIZE:
             img = cv2.resize(img, IMG_SIZE)
        images.append(img)
        
    # Normalize to 0-1
    X = np.array(images).astype('float32') / 255.0
    # Add channel dimension (N, 224, 224, 1)
    X = np.expand_dims(X, axis=-1)
    
    return X

def train():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    print("Loading data...")
    X_data = load_data()
    
    if len(X_data) == 0:
        return
        
    # Split for validation (to check overfitting)
    X_train, X_val = train_test_split(X_data, test_size=0.2, random_state=42)
    print(f"Training on {len(X_train)} images, Validating on {len(X_val)} images.")
    
    autoencoder = build_autoencoder()
    
    # Callbacks
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1),
        ModelCheckpoint(
            os.path.join(MODEL_DIR, 'autoencoder_epb_best.h5'),
            monitor='val_loss',
            save_best_only=True,
            mode='min',
            verbose=1
        ),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6, verbose=1)
    ]
    
    # Train
    # Input = X_train, Target = X_train (Reconstruction)
    print("Starting training...")
    history = autoencoder.fit(
        X_train, X_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        shuffle=True,
        validation_data=(X_val, X_val),
        callbacks=callbacks,
        verbose=1
    )
    
    # Save Final
    autoencoder.save(os.path.join(MODEL_DIR, 'autoencoder_epb_final.h5'))
    
    # Visualization: Check Reconstructions
    print("Generating sample reconstructions...")
    decoded_imgs = autoencoder.predict(X_val[:5])
    
    n = 5
    plt.figure(figsize=(20, 6))
    for i in range(n):
        # Original
        ax = plt.subplot(3, n, i + 1)
        plt.imshow(X_val[i].reshape(224, 224), cmap='gray')
        plt.title("Original")
        plt.axis("off")
        
        # Reconstruction
        ax = plt.subplot(3, n, i + 1 + n)
        plt.imshow(decoded_imgs[i].reshape(224, 224), cmap='gray')
        plt.title("Reconstructed")
        plt.axis("off")
        
        # Difference (Anomaly Map)
        diff = np.abs(X_val[i] - decoded_imgs[i])
        ax = plt.subplot(3, n, i + 1 + 2 * n)
        plt.imshow(diff.reshape(224, 224), cmap='inferno')
        plt.title("Difference (Anomaly)")
        plt.axis("off")
        
    plt.savefig(os.path.join(RESULTS_DIR, 'validation_samples.png'))
    print(f"Saved reconstruction samples to {RESULTS_DIR}/validation_samples.png")
    
    # Calculate Threshold Stats
    # Get mean MSE on validation set (assuming val set is mostly 'normal')
    val_loss = history.history['val_loss'][-1]
    print(f"Final Validation MSE: {val_loss:.6f}")
    
    # Ideally, we compute error per image to set dynamic threshold
    # For now, saving one global metric is a good start.

if __name__ == "__main__":
    train()
