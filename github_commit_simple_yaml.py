import os
import yaml
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
path = "test.yaml"
url = "/".join([repo_api, "contents", path])
resp = requests.get(url, headers=HEADER)
resp = resp.json()
download_url = resp["download_url"]
blob_sha = resp["sha"]

# Step 2. Get the file content
resp = requests.get(resp["download_url"], headers=HEADER)
contents = yaml.safe_load(resp.text.strip("\n"))

# Step 3. Edit the file content
contents["key3"] = "value3"

# Step 4. Encode the edited content
contents = yaml.safe_dump(contents).encode("utf-8")
contents = base64.b64encode(contents)
contents = contents.decode("utf-8")

# Step 5. Replace the file in the repository
url = "/".join([repo_api, "contents", path])
body = {
    "message": f"Updating {path}",
    "content": contents,
    "sha": blob_sha,
}
requests.put(url, json=body, headers=HEADER)
