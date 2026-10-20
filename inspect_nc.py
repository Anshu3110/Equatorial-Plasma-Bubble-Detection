import netCDF4 as nc
import sys
import glob

files = glob.glob("data/raw/gold_netcdf/*.nc")
if not files:
    print("No files found.")
    sys.exit(1)

f = files[0]
print(f"Inspecting {f}...")
ds = nc.Dataset(f)
print("Variables:")
for var in ds.variables:
    print(f" - {var}")
ds.close()
