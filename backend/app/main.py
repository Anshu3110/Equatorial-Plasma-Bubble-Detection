import os
# Fix for HDF5 file locking on Docker volumes
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI(title="EPB Detection API", version="1.0.0")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import tensorflow as tf
import cv2
import numpy as np
from io import BytesIO
from datetime import datetime
import pickle
import pandas as pd
import os


# Import shared modules
import sys
# Add /app to python path to access src
sys.path.append('/app')
try:
    from src.data_loader import get_file_list, download_specific_file
    from src.preprocessing import process_netcdf
except ImportError:
    # Fallback for local testing if not in docker
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.data_loader import get_file_list, download_specific_file
    from src.preprocessing import process_netcdf

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
model = None
training_history = None

@app.on_event("startup")
async def load_model():
    """Load model and training history on startup"""
    global model, training_history
    
    try:
        model_path = os.getenv('MODEL_PATH', '../models/autoencoder_epb_final.h5')
        print(f"DEBUG: Attempting to load model from: {model_path}")
        print(f"DEBUG: Current working directory: {os.getcwd()}")
        if os.path.exists("/app/models"):
             print(f"DEBUG: Contents of /app/models: {os.listdir('/app/models')}")
        else:
             print("DEBUG: /app/models does not exist")

        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
            print(f"✓ Model loaded successfully from {model_path}")
        else:
            print(f"⚠ Model not found at {model_path}. Running in mock mode.")
        
        # Load training history
        history_path = '../results/metrics/training_history.pkl'
        if os.path.exists(history_path):
            with open(history_path, 'rb') as f:
                training_history = pickle.load(f)
            print("✓ Training history loaded")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        # Don't raise, allowing server to start for dev/testing
        # raise

def generate_scan_id():
    """Generate unique scan ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = np.random.randint(1000, 9999)
    return f"GOLD-2024-{random_suffix}"

def preprocess_image(file_bytes):
    """Preprocess uploaded image for model inference"""
    # Decode image
    # Decode image as Grayscale (for Autoencoder)
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise ValueError("Invalid image file")
    
    # Resize to model input size (224, 224)
    img_resized = cv2.resize(img, (224, 224))
    
    # Normalize
    img_normalized = img_resized.astype('float32') / 255.0
    
    # Add batch and channel dimension (1, 224, 224, 1)
    img_batch = np.expand_dims(img_normalized, axis=0)
    img_batch = np.expand_dims(img_batch, axis=-1)
    
    return img_batch

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "EPB Detection API",
        "model_loaded": model is not None
    }

@app.post("/api/predict")
async def predict_epb(file: UploadFile = File(...)):
    """
    Endpoint for EPB detection
    """
    # Mock prediction if model not loaded
    if model is None:
        scan_id = generate_scan_id()
        is_epb = bool(np.random.choice([True, False]))
        confidence = float(np.random.uniform(0.8, 0.99))
        mock_mse = float(np.random.uniform(0.01, 0.05))
        
        return {
            "scan_id": scan_id,
            "epb_detected": is_epb,
            "confidence": round(confidence * 100, 2),
            "mse_score": mock_mse,
            "threshold": 0.028,
            "status": "DETECTED" if is_epb else "CLEAR",
            "timestamp": datetime.now().isoformat(),
            "image_url": "",
            "metadata": {
                "model_version": "Mock Model (No .h5 found)",
                "preprocessing": "Simulated",
                "tec_validation": "N/A"
            }
        }
    
    try:
        # Read image
        contents = await file.read()
        
        # Preprocess
        img_batch = preprocess_image(contents)
        
        # Predict (Reconstruct)
        reconstruction = model.predict(img_batch, verbose=0)
        
        # Calculate MSE (Anomaly Score)
        difference = np.abs(img_batch - reconstruction)
        mse = np.mean(np.square(difference))
        
        # Determine status (Threshold based on validation results)
        THRESHOLD = 0.028
        epb_detected = bool(mse > THRESHOLD)
        
        # Calculate mock confidence based on how far we are from threshold
        # Far above threshold = High Confidence EPB
        # Far below threshold = High Confidence Clear
        deviation = abs(mse - THRESHOLD)
        confidence = min(1.0, deviation / 0.01) # Cap at 100% if 0.01 away
        
        # Format response
        result = {
            "scan_id": generate_scan_id(),
            "epb_detected": bool(epb_detected),
            "confidence": round(float(confidence) * 100, 2),
            "mse_score": round(float(mse), 6),
            "threshold": float(THRESHOLD),
            "status": "DETECTED" if epb_detected else "CLEAR",
            "timestamp": datetime.now().isoformat(),
            "image_url": "",
            "metadata": {
                "model_version": "Convolutional Autoencoder v1",
                "preprocessing": "Grayscale 224x224, Normalized",
                "tec_validation": "GNSS ROTI Correlation"
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/stats")
async def get_system_stats():
    """
    Return system statistics from actual validation results
    """
    try:
        results_path = '../results/validation_results.csv'
        if os.path.exists(results_path):
            df = pd.read_csv(results_path)
            total = len(df)
            detections = int(df['prediction_ai'].sum())
            
            # accuracy (if ground truth is available and not all -1/NaN)
            # Assuming ground_truth_gnss is 0 or 1.
            if 'ground_truth_gnss' in df.columns:
                 correct = df[df['prediction_ai'] == df['ground_truth_gnss']]
                 accuracy = round(len(correct) / total * 100, 1) if total > 0 else 0
            else:
                 accuracy = 0

            return {
                "total_scans": total,
                "epb_detections": detections,
                "accuracy": accuracy,
                "active_alerts": detections  # Just using detections as alerts for now
            }
        else:
             return {
                "total_scans": 0,
                "epb_detections": 0,
                "accuracy": 0,
                "active_alerts": 0
            }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {"total_scans": 0, "epb_detections": 0, "accuracy": 0, "active_alerts": 0}

@app.get("/api/dataset")
async def get_dataset():
    """
    Return labeled dataset from validation results
    """
    try:
        results_path = '../results/validation_results.csv'
        dataset = []
        
        if os.path.exists(results_path):
            df = pd.read_csv(results_path)
            # Limit to 100 for performance if needed, or paginate later
            for idx, row in df.head(100).iterrows(): 
                # Create a pseudo-ID if not present
                scan_date = "Unknown"
                try:
                    # filename format: gold_l2_nmax_2025_254_...
                    parts = row['filename'].split('_')
                    year = parts[3]
                    doy = parts[4]
                    scan_date = f"{year}-DOY{doy}"
                except:
                    pass

                dataset.append({
                    "id": f"GOLD-{idx:04d}",
                    "filename": row['filename'],
                    "epb_detected": bool(row['prediction_ai']),
                    "confidence": round(float(row['mse']) * 1000, 2), # Visualization proxy
                    "mse": float(row['mse']),
                    "threshold": float(row.get('threshold', 0.028)),
                    "date": scan_date,
                    "region": "Global", # Metadata not currently in filename
                    "image_url": f"/api/images/{row['filename']}"
                })
            return dataset
        else:
            return []
            
    except Exception as e:
        print(f"Error serving dataset: {e}")
        return []

@app.get("/api/gold/recent")
async def get_recent_gold_data():
    """
    Get list of recent available files from NASA GOLD server
    """
    try:
        # Get current year and previous year to be safe
        now = datetime.now()
        files = []
        
        # Fetch for current year
        print(f"Fetching NASA GOLD file list for {now.year}...")
        files_year = get_file_list(now.year)
        
        # Fallback to previous year if current year has no data (e.g. early Jan)
        if not files_year:
             print(f"No data for {now.year}, trying {now.year - 1}...")
             files_year = get_file_list(now.year - 1)
             
        files.extend(files_year)
        
        # Format for frontend
        archive_data = []
        for f in files[-50:]: # Return last 50
             # Extract date from filename: gold_l2_nmax_YYYY_DOY_...
             try:
                 parts = f.split('_')
                 year = int(parts[3])
                 doy = int(parts[4])
                 date_obj = datetime(year, 1, 1) + timedelta(days=doy - 1)
                 date_str = date_obj.strftime("%Y-%m-%d")
             except:
                 date_str = "Unknown"

             archive_data.append({
                 "id": f.replace(".nc", ""),
                 "filename": f,
                 "date": date_str,
                 "status": "Available on NASA Server",
                 "action": "Download"
             })
             
        # Sort by filename descending (newest first)
        archive_data.sort(key=lambda x: x['filename'], reverse=True)
        return archive_data

        return archive_data

    except Exception as e:
        print(f"Error fetching NASA data: {e}")
        return []

@app.post("/api/analyze/nasa")
def analyze_nasa_file(payload: dict):
    """
    Download, Process, and Analyze a specific file from NASA Archive
    Payload: {"filename": "gold_l2_nmax_..."}
    """
    import shutil
    import uuid
    import subprocess
    import json as json_mod
    
    filename = payload.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename required")
        
    print(f"[ANALYZE] Step 0: Request for {filename}", file=sys.stderr, flush=True)
    
    try:
        # Step 1: Download
        print(f"[ANALYZE] Step 1: Downloading...", file=sys.stderr, flush=True)
        nc_path = download_specific_file(filename, output_dir="data/raw/gold_netcdf")
        if not nc_path:
             raise HTTPException(status_code=404, detail="Failed to download file from NASA")
        
        if not os.path.exists(nc_path):
             raise HTTPException(status_code=500, detail=f"Downloaded but file missing: {nc_path}")
        
        file_size = os.path.getsize(nc_path)
        print(f"[ANALYZE] Step 1 OK: {nc_path} ({file_size} bytes)", file=sys.stderr, flush=True)

        # Step 2: Copy to /tmp
        print(f"[ANALYZE] Step 2: Copying to /tmp...", file=sys.stderr, flush=True)
        tmp_path = f"/tmp/{uuid.uuid4()}_{filename}"
        shutil.copy2(nc_path, tmp_path)
        print(f"[ANALYZE] Step 2 OK: copied to {tmp_path}", file=sys.stderr, flush=True)
        
        # Step 3: Process via Subprocess
        print(f"[ANALYZE] Step 3: Running subprocess...", file=sys.stderr, flush=True)
        cmd = [sys.executable, "src/preprocessing.py", "--file", tmp_path]
        proc_result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print(f"[ANALYZE] Step 3: returncode={proc_result.returncode}", file=sys.stderr, flush=True)
        if proc_result.stderr:
            print(f"[ANALYZE] Step 3 stderr: {proc_result.stderr[:500]}", file=sys.stderr, flush=True)
        if proc_result.stdout:
            print(f"[ANALYZE] Step 3 stdout: {proc_result.stdout[:500]}", file=sys.stderr, flush=True)
        
        if proc_result.returncode != 0:
            raise Exception(f"Preprocessing failed (rc={proc_result.returncode}): {proc_result.stderr[:200]}")
        
        # Parse JSON output from subprocess
        stdout = proc_result.stdout
        start_marker = "JSON_OUTPUT_START"
        end_marker = "JSON_OUTPUT_END"
        si = stdout.find(start_marker)
        ei = stdout.find(end_marker)
        
        if si == -1 or ei == -1:
            raise Exception(f"No JSON markers in subprocess output: {stdout[:200]}")
        
        json_str = stdout[si + len(start_marker):ei].strip()
        output_images = json_mod.loads(json_str)
        print(f"[ANALYZE] Step 3 OK: {len(output_images)} images generated", file=sys.stderr, flush=True)
        
        # Cleanup tmp
        try:
            os.remove(tmp_path)
        except:
            pass

        if not output_images:
             raise HTTPException(status_code=500, detail="No images produced from NetCDF file")
             
        # Step 4: Read first image
        image_path = output_images[0]
        print(f"[ANALYZE] Step 4: Reading image {image_path}", file=sys.stderr, flush=True)
        
        if not os.path.exists(image_path):
            raise Exception(f"Processed image not found: {image_path}")
        
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        print(f"[ANALYZE] Step 4 OK: {len(image_bytes)} bytes", file=sys.stderr, flush=True)
             
        # Step 5: Model prediction
        print(f"[ANALYZE] Step 5: Model prediction...", file=sys.stderr, flush=True)
        if model is None:
             raise HTTPException(status_code=503, detail="Model not loaded")
             
        img_batch = preprocess_image(image_bytes)
        reconstruction = model.predict(img_batch, verbose=0)
        difference = np.abs(img_batch - reconstruction)
        mse_val = float(np.mean(np.square(difference)))
        
        THRESHOLD = 0.028
        epb_detected = bool(mse_val > THRESHOLD)
        deviation = float(abs(mse_val - THRESHOLD))
        confidence_val = float(min(1.0, deviation / 0.01))
        
        print(f"[ANALYZE] Step 5 OK: mse={mse_val:.6f}, epb={epb_detected}", file=sys.stderr, flush=True)

        # Step 6: Build response (all native Python types)
        response = {
            "scan_id": generate_scan_id(),
            "filename": str(filename),
            "epb_detected": bool(epb_detected),
            "confidence": round(confidence_val * 100, 2),
            "mse_score": round(mse_val, 6),
            "threshold": float(THRESHOLD),
            "status": "DETECTED" if epb_detected else "CLEAR",
            "timestamp": datetime.now().isoformat(),
            "image_url": f"/api/images/{os.path.basename(image_path)}",
            "metadata": {
                "source": "NASA Archive (Live)",
                "model_type": "Autoencoder"
            }
        }
        
        print(f"[ANALYZE] Step 6 OK: Returning response", file=sys.stderr, flush=True)
        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ANALYZE] EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_model_metrics():
    """
    Return training metrics for Reports page.
    Computes real metrics from validation_results.csv.
    """
    # Compute real metrics from validation results
    results_path = "../results/validation_results.csv"
    real_metrics = {
        "accuracy": 0.0,
        "precision": 0.0,
        "recall": 0.0,
        "f1_score": 0.0,
        "mse": 0.025
    }
    confusion = [[0, 0], [0, 0]]
    
    if os.path.exists(results_path):
        try:
            df = pd.read_csv(results_path)
            if 'prediction_ai' in df.columns and 'ground_truth_gnss' in df.columns:
                y_pred = df['prediction_ai'].values
                y_true = df['ground_truth_gnss'].values
                
                # Confusion matrix: [[TN, FP], [FN, TP]]
                tn = int(np.sum((y_pred == 0) & (y_true == 0)))
                fp = int(np.sum((y_pred == 1) & (y_true == 0)))
                fn = int(np.sum((y_pred == 0) & (y_true == 1)))
                tp = int(np.sum((y_pred == 1) & (y_true == 1)))
                confusion = [[tn, fp], [fn, tp]]
                
                total = tn + fp + fn + tp
                real_metrics["accuracy"] = float((tp + tn) / total) if total > 0 else 0.0
                real_metrics["precision"] = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
                real_metrics["recall"] = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
                p = real_metrics["precision"]
                r = real_metrics["recall"]
                real_metrics["f1_score"] = float(2 * p * r / (p + r)) if (p + r) > 0 else 0.0
                
            if 'mse' in df.columns:
                real_metrics["mse"] = float(df['mse'].mean())
        except Exception as e:
            print(f"Error computing metrics: {e}", flush=True)
    
    # Training history
    if training_history is not None:
        epochs = list(range(len(training_history['loss'])))
        t_loss = [float(v) for v in training_history['loss']]
        v_loss = [float(v) for v in training_history['val_loss']]
        real_metrics["mse"] = float(training_history['val_loss'][-1])
    else:
        # Simulated loss curve
        epochs = list(range(50))
        t_loss = [float(0.1 * (0.9 ** i)) for i in epochs]
        v_loss = [float(0.11 * (0.9 ** i) + 0.005) for i in epochs]
    
    return {
        "training_loss": t_loss,
        "validation_loss": v_loss,
        "epochs": epochs,
        "confusion_matrix": confusion,
        "final_metrics": {
            "accuracy": round(real_metrics["accuracy"] * 100, 2),
            "precision": round(real_metrics["precision"] * 100, 2),
            "recall": round(real_metrics["recall"] * 100, 2),
            "f1_score": round(real_metrics["f1_score"] * 100, 2),
            "mse": round(real_metrics["mse"], 6)
        }
    }

@app.get("/api/images/{filename}")
async def get_image(filename: str):
    """
    Serve processed images
    """
    # Path where preprocessing.py saves images
    image_path = f"../data/processed/images_224x224/{filename}"
    
    if os.path.exists(image_path):
        return FileResponse(image_path)
    
    # Check raw/other paths if needed
    raise HTTPException(status_code=404, detail=f"Image {filename} not found")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }
