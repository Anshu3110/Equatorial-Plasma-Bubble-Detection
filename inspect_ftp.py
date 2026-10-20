import ftplib

FTP_HOST = "ftp.aiub.unibe.ch"
YEAR = 2025
REMOTE_DIR = f"/CODE/{YEAR}/"

def list_files():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login()
        print(f"Connected to {FTP_HOST}")
        
        try:
            ftp.cwd(REMOTE_DIR)
            print(f"Changed directory to {REMOTE_DIR}")
            
            print("Fetching file list (NLST)...")
            files = ftp.nlst()
            
            print(f"Found {len(files)} files.")
            print("First 10 files:")
            for f in files[:10]:
                print(f)
                
        except ftplib.error_perm as e:
            print(f"Error accessing directory: {e}")
            
        ftp.quit()
    except Exception as e:
        print(f"FTP Error: {e}")

if __name__ == "__main__":
    list_files()
