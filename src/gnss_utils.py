import gzip
import re
import numpy as np
from datetime import datetime

def parse_ionex(file_path):
    """
    Parse IONEX file to extract TEC maps.
    Returns a dictionary: {datetime: tec_map_2d_array}
    """
    tec_maps = {}
    current_date = None
    current_map = []
    reading_map = False
    
    # Open file (handle .gz or plain text)
    if file_path.endswith('.gz'):
        f = gzip.open(file_path, 'rt', encoding='utf-8')
    else:
        f = open(file_path, 'r', encoding='utf-8')
        
    try:
        lines = f.readlines()
        
        lat_range = np.arange(87.5, -87.6, -2.5) # Standard IONEX resolution
        lon_range = np.arange(-180, 181, 5)
        
        for line in lines:
            if "EPOCH OF CURRENT MAP" in line:
                # Format: 2025     9     1     0     0     0                        EPOCH OF CURRENT MAP
                parts = line.split()
                year, month, day, hour = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                current_date = datetime(year, month, day, hour)
                current_map = []
                reading_map = True
                continue
                
            if "END OF TEC MAP" in line:
                reading_map = False
                if current_date and current_map:
                    # Convert list to array (Lat x Lon)
                    # IONEX usually gives data in grid format
                    # This simple parser assumes standard grid size for simplicity
                    # For production, strictly parse 'LAT/LON1/LON2/DLON/H' header
                    tec_maps[current_date] = np.array(current_map)
                continue
                
            if reading_map and "LAT/LON1/LON2/DLON/H" not in line:
                # Read TEC values
                # Format is usually blocks of integers
                try:
                    # Filter out non-numeric lines just in case
                    vals = [float(x) for x in line.split()]
                    current_map.extend(vals)
                except ValueError:
                    pass
                    
    finally:
        f.close()
        
    return tec_maps

def calculate_roti(tec_map, window_size=5):
    """
    Calculate ROTI (Standard Deviation of ROT) over a spatial window.
    Proxy implementation since we have snapshots, not continuous time series per station.
    We'll use Spatial Gradient as a proxy for 'Irregularity'.
    """
    # Gradient in Longitude direction (West-East)
    grad_lon = np.gradient(tec_map, axis=1)
    
    # Calculate variation (Standard Deviation) in the local window
    # This highlights sharp changes (bubbles)
    roti_proxy = np.zeros_like(tec_map)
    
    # Simple moving standard deviation
    from scipy.ndimage import generic_filter
    roti_proxy = generic_filter(grad_lon, np.std, size=window_size)
    
    return roti_proxy

if __name__ == "__main__":
    # Test with the file we know exists
    import glob
    files = glob.glob("data/raw/tec_ionex/*.gz")
    if files:
        print(f"Testing parser on {files[0]}")
        maps = parse_ionex(files[0])
        print(f"Found {len(maps)} time snapshots.")
        if len(maps) > 0:
            first_key = list(maps.keys())[0]
            print(f"Map shape at {first_key}: {len(maps[first_key])} (Flattened)")
    else:
        print("No .gz files found in data/raw/tec_ionex")
