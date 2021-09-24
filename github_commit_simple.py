import os
import base64
import requests

# Get GitHub token from env
token = os.environ["GITHUB_TOKEN"]

# Set API URLs
API_ROOT = "https://api.github.com"
REPOSITORY = "sgibson91/github_api_test"
repo_api = "/".join([API_ROOT, "repos", REPOSITORY])

# Set a header
HEADER = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {token}",
}

# Step 1. Get relevant URLs
path = "test.md"
url = "/".join([repo_api, "contents", path])
resp = requests.get(url, headers=HEADER)
resp = resp.json()
download_url = resp["download_url"]
blob_sha = resp["sha"]

# Step 2. Get the file contents
resp = requests.get(resp["download_url"], headers=HEADER)
file_contents = resp.text.strip("\n")

# Step 3. Edit the file contents
file_contents += "!"

# Step 4. Encode the file contents
encoded_file_contents = file_contents.encode("ascii")
base64_bytes = base64.b64encode(encoded_file_contents)
raw_contents = base64_bytes.decode("utf-8")

# Step 5. Replace the file in the repository
url = "/".join([repo_api, "contents", path])
body = {
    "message": f"Updating {path}",
    "content": raw_contents,
    "sha": blob_sha,
}
requests.put(url, json=body, headers=HEADER)

# That's it! HEAD is automatically updated!
