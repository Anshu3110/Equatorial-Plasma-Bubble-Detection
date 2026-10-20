import requests
import json

url = "http://localhost:8000/api/analyze/nasa"
payload = {"filename": "gold_l2_nmax_2026_032_v05_r01_c02.nc"}
headers = {"Content-Type": "application/json"}

try:
    print(f"Sending POST request to {url}...")
    print(f"Testing file: {payload['filename']}")
    response = requests.post(url, json=payload, headers=headers, timeout=120)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
        print("SUCCESS: Analysis completed.")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
