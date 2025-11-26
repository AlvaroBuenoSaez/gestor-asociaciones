import requests
from requests.structures import CaseInsensitiveDict
import os

# Using the key from the user's snippet which matches the .env file
url = "https://api.geoapify.com/v1/geocode/autocomplete?text=Mosco&apiKey=ebbcd2121ac241dcbb9339a1843d1727"

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"

try:
    resp = requests.get(url, headers=headers)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text[:200]}...") # Print first 200 chars
except Exception as e:
    print(f"Error: {e}")
