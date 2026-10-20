import os
import ftplib
import argparse
from datetime import datetime, timedelta

# Configuration
FTP_HOST = "ftp.aiub.unibe.ch"
FTP_DIR_TEMPLATE = "/CODE/{year}/"
OUTPUT_DIR = "data/raw/tec_ionex"

def download_ionex(start_date, end_date):
    """Download IONEX files for date range"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login() 
        print(f"Connected to {FTP_HOST}")
        
        current_date = start_date
        while current_date <= end_date:
            year = current_date.year
            doy = int(current_date.strftime("%j"))
            yy = current_date.strftime("%y")
            
            # Navigate to year directory
            remote_dir = FTP_DIR_TEMPLATE.format(year=year)
            try:
                ftp.cwd(remote_dir)
            except ftplib.error_perm as e:
                print(f"Directory not found: {remote_dir} - {e}")
                current_date += timedelta(days=1)
                continue
                
            # Filename format: COD0OPSFIN_{YYYY}{DDD}0000_01D_01H_GIM.INX.gz
            # Example: COD0OPSFIN_20252440000_01D_01H_GIM.INX.gz
            filename = f"COD0OPSFIN_{year}{doy:03d}0000_01D_01H_GIM.INX.gz"
            output_path = os.path.join(OUTPUT_DIR, filename)
            
            if os.path.exists(output_path):
                print(f"Skipping (exists): {filename}")
            else:
                print(f"Downloading {filename}...")
                try:
                    with open(output_path, 'wb') as f:
                        ftp.retrbinary(f"RETR {filename}", f.write)
                    print(f"✓ Downloaded: {output_path}")
                except ftplib.error_perm as e:
                    print(f"✗ File not found: {filename} - {e}")
            
            current_date += timedelta(days=1)
            
        ftp.quit()
        
    except Exception as e:
        print(f"FTP Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download GNSS IONEX Data")
    parser.add_argument("--start", type=str, default="2025-09-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default="2025-09-30", help="End date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")
    
    print(f"Starting IONEX download from {args.start} to {args.end}")
    download_ionex(start_date, end_date)
    print("Note: Files are compressed (.gz). You may need 7-Zip or 'gzip' to extract them.")

if __name__ == "__main__":
    main()
