import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("CR_API_KEY")
if not api_key:
    raise RuntimeError("CR_API_KEY environment variable not set")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json"    
}

player_tag = "#C0V0UQ9UY"
encoded_tag = "%23" + player_tag[1:]

url = f"https://api.clashroyale.com/v1/players/{encoded_tag}"

response = requests.get(url, headers=headers)

if response.status_code != 200:
    raise Exception(
        f"API Error {response.status_code}: {response.text}"
    )

player_data = response.json()
print("Success:", response.status_code)
