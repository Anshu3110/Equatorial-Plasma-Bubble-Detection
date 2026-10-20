
import os
import shutil
import uuid
import sys

# Append /app to path
sys.path.append("/app")

try:
    from src.preprocessing import process_netcdf
except ImportError:
    # try .src
    sys.path.append(".")
    from src.preprocessing import process_netcdf

nc_path = "data/raw/gold_netcdf/gold_l2_nmax_2025_273_v05_r01_c02.nc"

print(f"Testing with file: {nc_path}")
if not os.path.exists(nc_path):
    print("File does not exist!")
    sys.exit(1)

tmp_path = f"/tmp/{uuid.uuid4()}_debug_test.nc"
print(f"Copying to {tmp_path}")

try:
    shutil.copy2(nc_path, tmp_path)
    print("Copy success")
except Exception as e:
    print(f"Copy failed: {e}")
    sys.exit(1)

print("Calling process_netcdf...")
try:
    images = process_netcdf(tmp_path)
    print(f"Validation Result: {images}")
except Exception as e:
    print(f"Validation Exception: {e}")
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
