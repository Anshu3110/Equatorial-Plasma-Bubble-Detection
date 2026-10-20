import os
import requests
import argparse
from datetime import datetime, timedelta
import netCDF4 as nc
import numpy as np

# Configuration
import re

# Configuration
GOLD_DATA_URL = "https://cdaweb.gsfc.nasa.gov/sp_phys/data/gold/level2/nmax"
OUTPUT_DIR = "data/raw/gold_netcdf"

def download_specific_file(filename, output_dir=OUTPUT_DIR):
    """Download a specific file from NASA GOLD server given the filename"""
    # Filename format: gold_l2_nmax_YYYY_DOY_...
    try:
        parts = filename.split('_')
        year = parts[3]
        
        file_url = f"{GOLD_DATA_URL}/{year}/{filename}"
        output_path = os.path.join(output_dir, filename)
        
        os.makedirs(output_dir, exist_ok=True)
        
        if download_file(file_url, output_path):
            return output_path
        return None
    except Exception as e:
        print(f"Error downloading specific file {filename}: {e}")
        return None

def download_file(url, output_path):
    """Download file from URL to output path"""
    if os.path.exists(output_path):
        print(f"Skipping (already exists): {output_path}")
        return True
        
    try:
        print(f"Downloading {url}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✓ Downloaded: {output_path}")
            return True
        else:
            print(f"✗ Failed to download (Status {response.status_code}): {url}")
            return False
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False

def get_file_list(year):
    """Fetch list of .nc files for a given year directory"""
    year_url = f"{GOLD_DATA_URL}/{year}/"
    try:
        response = requests.get(year_url)
        if response.status_code != 200:
            print(f"Warning: Could not access {year_url}")
            return []
        
        # Simple regex to find .nc links
        # Pattern: href="gold_l2_nmax_2019_001_v05_r01_c01.nc"
        pattern = r'href="(gold_l2_nmax_\d{4}_\d{3}_.*\.nc)"'
        files = re.findall(pattern, response.text)
        
        # Remove duplicates
        return sorted(list(set(files)))
    except Exception as e:
        print(f"Error fetching file list for {year}: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Download NASA GOLD Data")
    parser.add_argument("--start", type=str, default="2025-09-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default="2025-09-30", help="End date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")
    
    print(f"Starting download from {args.start} to {args.end}")
    
    current_date = start_date
    processed_years = set()
    year_files = {} # year -> list of files
    
    while current_date <= end_date:
        year = current_date.year
        doy = int(current_date.strftime("%j"))
        
        # Print scanning message (User requested "add back the date")
        print(f"Scanning for data on {current_date.strftime('%Y-%m-%d')} (DOY {doy:03d})...")
        
        # Fetch file list for year if not already done
        if year not in processed_years:
            print(f"Fetching file list for {year}...")
            year_files[year] = get_file_list(year)
            processed_years.add(year)
        
        # Find files matching the DOY
        # Filename format: gold_l2_nmax_YYYY_DOY_...
        doy_str = f"{doy:03d}"
        prefix = f"gold_l2_nmax_{year}_{doy_str}"
        
        matching_files = [f for f in year_files[year] if prefix in f]
        
        if not matching_files:
            print(f"No files found for {current_date.strftime('%Y-%m-%d')} (DOY {doy_str})")
        
        for filename in matching_files:
            file_url = f"{GOLD_DATA_URL}/{year}/{filename}"
            output_path = os.path.join(OUTPUT_DIR, filename)
            download_file(file_url, output_path)
            
        current_date += timedelta(days=1)

if __name__ == "__main__":
    main()
