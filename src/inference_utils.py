import numpy as np
import cv2
import tensorflow as tf

def load_autoencoder(model_path):
    """Load the trained autoencoder"""
    return tf.keras.models.load_model(model_path)

def predict_anomaly(model, img_array, threshold=None):
    """
    Predict if image contains EPB (Anomaly)
    
    Args:
        model: Trained autoencoder
        img_array: Preprocessed image (224, 224, 1) or batch
        threshold: MSE threshold for classification (Optional)
        
    Returns:
        dict: {
            'is_anomaly': bool (if threshold provided),
            'mse': float (Reconstruction Error),
            'reconstruction': np.array,
            'difference': np.array (The 'Difference Image')
        }
    """
    # Ensure batch dimension
    if len(img_array.shape) == 3:
        img_batch = np.expand_dims(img_array, axis=0) # (1, 224, 224, 1)
    else:
        img_batch = img_array
        
    # Reconstruct
    reconstruction = model.predict(img_batch, verbose=0)
    
    # Calculate Difference (Residual)
    difference = np.abs(img_batch - reconstruction)
    
    # Calculate MSE (Mean Squared Error) per image
    mse = np.mean(np.square(difference), axis=(1, 2, 3))
    
    result = {
        'mse': float(mse[0]),
        'reconstruction': reconstruction[0],
        'difference': difference[0]
    }
    
    if threshold is not None:
        result['is_anomaly'] = bool(mse[0] > threshold)
        
    return result

def visualize_anomaly(original, result, save_path=None):
    """Helper to plot the Anomaly Detection triplet"""
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.imshow(original.reshape(224, 224), cmap='gray')
    plt.title("Original Scan")
    plt.axis("off")
    
    plt.subplot(1, 3, 2)
    plt.imshow(result['reconstruction'].reshape(224, 224), cmap='gray')
    plt.title("Reconstructed (Normal)")
    plt.axis("off")
    
    plt.subplot(1, 3, 3)
    # Use hot colormap for difference to highlight the "Bubble"
    plt.imshow(result['difference'].reshape(224, 224), cmap='inferno')
    plt.title(f"Difference Image (MSE: {result['mse']:.5f})")
    plt.axis("off")
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()
