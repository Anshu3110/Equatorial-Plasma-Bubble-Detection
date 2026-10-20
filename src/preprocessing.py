import os
import netCDF4 as nc
import numpy as np
import cv2
import glob
from skimage import exposure

# Configuration
INPUT_DIR = "data/raw/gold_netcdf"
OUTPUT_DIR = "data/processed/images_224x224"

import sys
# Fix for HDF5 file locking
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'

def process_netcdf(filepath):
    """Convert NetCDF file to processed PNG image. Returns list of generated image paths."""
    output_paths = []
    try:
        print(f"DEBUG: Processing {filepath}", file=sys.stderr)
        print(f"DEBUG: CWD: {os.getcwd()}", file=sys.stderr)
        abs_path = os.path.abspath(filepath)
        print(f"DEBUG: Absolute Path: {abs_path}", file=sys.stderr)
        
        if os.path.exists(filepath):
            print(f"DEBUG: File exists. Size: {os.path.getsize(filepath)} bytes", file=sys.stderr)
            # Try to read header
            with open(filepath, 'rb') as f:
                header = f.read(4)
                print(f"DEBUG: Header: {header}", file=sys.stderr)
        else:
            print(f"DEBUG: File DOES NOT exist at {filepath}", file=sys.stderr)
            
        # Load GOLD data
        ds = nc.Dataset(filepath)
        
        # Check if variables exist
        if 'nmax' not in ds.variables:
            print(f"DEBUG: Skipping {filepath}: Missing nmax", file=sys.stderr)
            ds.close()
            return []
            
        emission_rate_all = ds.variables['nmax'][:]
        quality_flag_all = ds.variables['nmax_dqi'][:]
        
        print(f"DEBUG: Processing {os.path.basename(filepath)} - Shape: {emission_rate_all.shape}", file=sys.stderr)
        
        # Determine number of frames
        # Shape could be (time, lat, lon) or just (lat, lon)
        if len(emission_rate_all.shape) == 3:
            num_frames = emission_rate_all.shape[0]
        else:
            num_frames = 1
            # Add dimension for uniform handling
            emission_rate_all = np.expand_dims(emission_rate_all, axis=0)
            quality_flag_all = np.expand_dims(quality_flag_all, axis=0)
        
        saved_count = 0
        best_frame_idx = -1
        best_valid_count = 0
        
        for i in range(num_frames):
            emission_rate = emission_rate_all[i]
            quality_flag = quality_flag_all[i]
            
            # Filter bad data
            valid_mask = (quality_flag == 0) & (emission_rate > 0) & (~np.isnan(emission_rate))
            valid_count = np.sum(valid_mask)
            total_count = valid_mask.size

            # Track best frame for fallback
            if valid_count > best_valid_count:
                best_valid_count = valid_count
                best_frame_idx = i
            
            # If too much missing data, skip (lowered from 10% to 1%)
            if valid_count < 0.01 * total_count:
                 if i == 0:
                     print(f"DEBUG: Frame {i}: Poor quality ({valid_count}/{total_count})", file=sys.stderr)
                 continue
    
            # Replace invalid with 0 or NaN
            emission_rate_clean = np.where(valid_mask, emission_rate, 0)
            
            # Normalize to 0-255
            img_normalized = exposure.rescale_intensity(
                emission_rate_clean, 
                out_range=(0, 255)
            ).astype(np.uint8)
            
            # Histogram Equalization
            img_equalized = cv2.equalizeHist(img_normalized)
            
            # Resize
            img_resized = cv2.resize(img_equalized, (224, 224), interpolation=cv2.INTER_CUBIC)
            
            # Save
            filename_base = os.path.basename(filepath).replace('.nc', '')
            output_filename = f"{filename_base}_t{i:02d}.png"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            cv2.imwrite(output_path, img_resized)
            output_paths.append(output_path)
            saved_count += 1
        
        # Fallback: if no frames passed quality, use the best available frame
        if saved_count == 0 and best_frame_idx >= 0 and best_valid_count > 0:
            print(f"DEBUG: Fallback - using best frame {best_frame_idx} ({best_valid_count}/{total_count} valid)", file=sys.stderr)
            emission_rate = emission_rate_all[best_frame_idx]
            quality_flag = quality_flag_all[best_frame_idx]
            valid_mask = (quality_flag == 0) & (emission_rate > 0) & (~np.isnan(emission_rate))
            emission_rate_clean = np.where(valid_mask, emission_rate, 0)
            
            img_normalized = exposure.rescale_intensity(
                emission_rate_clean, out_range=(0, 255)
            ).astype(np.uint8)
            img_equalized = cv2.equalizeHist(img_normalized)
            img_resized = cv2.resize(img_equalized, (224, 224), interpolation=cv2.INTER_CUBIC)
            
            filename_base = os.path.basename(filepath).replace('.nc', '')
            output_filename = f"{filename_base}_t{best_frame_idx:02d}.png"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            cv2.imwrite(output_path, img_resized)
            output_paths.append(output_path)
            saved_count = 1
            
        print(f"  Saved {saved_count}/{num_frames} frames from {os.path.basename(filepath)}")
        
        ds.close()
        return output_paths
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    files = glob.glob(os.path.join(INPUT_DIR, "*.nc"))
    print(f"Found {len(files)} NetCDF files.")
    
    for filepath in files:
        process_netcdf(filepath)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to single NetCDF file to process")
    args = parser.parse_args()

    if args.file:
        try:
            # Silence stdout for process_netcdf to avoid pollution
            # actually we moved prints to stderr, so it should be fine.
            images = process_netcdf(args.file)
            import json
            # Print JSON output for the caller to parse
            print("JSON_OUTPUT_START")
            print(json.dumps(images))
            print("JSON_OUTPUT_END")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        main()
