import os
import glob
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
from model import build_autoencoder
from inference_utils import predict_anomaly
from gnss_utils import parse_ionex, calculate_roti
import tensorflow as tf

# Configuration
MODEL_PATH = "models/autoencoder_epb_final.h5"
DATA_DIR = "data/processed/images_224x224"
GNSS_DIR = "data/raw/tec_ionex"
OUTPUT_FILE = "results/validation_results.csv"

def extract_metadata(filename):
    # gold_l2_nmax_2025_244_v05_r01_c02_t13.png
    parts = filename.split('_')
    year = int(parts[3])
    doy = int(parts[4])
    
    # Approximate hour from 't13' (this is an index, not hour, but we'll use it to grab a day file)
    # Ideally should map t-index to UT time from NetCDF, 
    # but for this Proof of Concept we just need the Date to find the IONEX file.
    
    return year, doy

def main():
    if not os.path.exists(MODEL_PATH):
        print("Model not found. Run src/train.py first.")
        return

    print("Loading model...")
    model = tf.keras.models.load_model(MODEL_PATH)
    
    image_files = glob.glob(os.path.join(DATA_DIR, "*.png"))
    print(f"Validating on ALL {len(image_files)} images...")
    
    results = []
    
    # Cache parsed IONEX maps to save time
    ionex_cache = {} 
    
    # Thresholds
    MSE_THRESHOLD = 0.028  # Lowered from 0.035 to improve Recall
    GNSS_ROTI_THRESHOLD = 5.0
    
    for i, img_path in enumerate(image_files):
        filename = os.path.basename(img_path)
        year, doy = extract_metadata(filename)
        
        # 1. AI Prediction
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None: continue
        img = cv2.resize(img, (224, 224))
        img_norm = img.astype('float32') / 255.0
        img_norm = np.expand_dims(img_norm, axis=-1)
        
        pred = predict_anomaly(model, img_norm)
        mse = pred['mse']
        
        # AI Label
        ai_label = 1 if mse > MSE_THRESHOLD else 0
        
        # 2. GNSS Ground Truth Check
        gnss_pattern = f"COD0OPSFIN_{year}{doy:03d}*.gz"
        gnss_files = glob.glob(os.path.join(GNSS_DIR, gnss_pattern))
        
        roti_level = 0.0
        gnss_label = -1 # Unknown
        
        if gnss_files:
            g_file = gnss_files[0]
            if g_file not in ionex_cache:
                print(f"Parsing GNSS file: {g_file}...")
                ionex_cache[g_file] = parse_ionex(g_file)
            
            max_roti = 0
            for dt, tec_map in ionex_cache[g_file].items():
                if len(tec_map) > 0:
                    curr_std = np.std(tec_map)
                    if curr_std > max_roti:
                        max_roti = curr_std
            
            roti_level = max_roti
            # GNSS Label
            gnss_label = 1 if roti_level > GNSS_ROTI_THRESHOLD else 0
            
        print(f"[{i+1}/{len(image_files)}] {filename} -> AI: {ai_label} (MSE:{mse:.4f}) | GNSS: {gnss_label} (ROTI:{roti_level:.2f})")
        
        results.append({
            'filename': filename,
            'mse': mse,
            'gnss_max_roti': roti_level,
            'prediction_ai': ai_label,
            'ground_truth_gnss': gnss_label
        })
        
    # Save results
    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Validation complete. Results saved to {OUTPUT_FILE}")
    print("Check the CSV to see if High MSE correlates with High GNSS Activity!")

if __name__ == "__main__":
    main()
