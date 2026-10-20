
import os
import sys
import glob

# Add /app to python path
sys.path.append("/app")

try:
    from src.preprocessing import process_netcdf
except ImportError:
    sys.path.append(".")
    from src.preprocessing import process_netcdf

# Find the file in /tmp
files = glob.glob('/tmp/*_gold_*.nc')
if not files:
    print("No file found in /tmp")
    sys.exit(1)

nc_path = files[0]
print(f"Testing with file: {nc_path}")

try:
    images = process_netcdf(nc_path)
    print(f"Result: {images}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
