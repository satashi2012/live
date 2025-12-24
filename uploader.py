import os
import base64
import requests

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "zaltvvn/live"
FILE_PATH = "StreamedSU.m3u8"
BRANCH = "main"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

with open(FILE_PATH, "rb") as f:
    content = base64.b64encode(f.read()).decode()

# Check if file exists
resp = requests.get(url, headers=headers)
sha = resp.json().get("sha") if resp.status_code == 200 else None

payload = {
    "message": "Auto update StreamedSU.m3u8",
    "content": content,
    "branch": BRANCH
}

if sha:
    payload["sha"] = sha

r = requests.put(url, json=payload, headers=headers)
r.raise_for_status()

print("✅ Uploaded to GitHub")
