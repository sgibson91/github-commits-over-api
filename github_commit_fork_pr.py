import os
import time
import base64
import requests

from pprint import pprint

# Get GitHub token from env
token = os.environ["GITHUB_TOKEN"]

# Set the API URLs
API_ROOT = "https://api.github.com"
REPOSITORY = "sgibson91/github_api_test"
repo_api = "/".join([API_ROOT, "repos", REPOSITORY])

# Set a header
HEADER = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {token}",
}

# Step 1. Fork the repo
url = "/".join([repo_api, "forks"])

# Note: This org in the body is only required because my personal
# account owns the original repo
org_name = "binderhub-test-org"
body = {"organization": org_name}

requests.post(url, json=body, headers=HEADER)

# Set fork API
repo_name = REPOSITORY.split("/")[-1]
fork_api = "/".join([API_ROOT, "repos", org_name, repo_name])

# Wait a short amount of time for the fork to resolve asynchronously
time.sleep(5)

# Step 2. Get a reference to HEAD
url = "/".join([fork_api, "git", "ref", "heads", "main"])
resp = requests.get(url, headers=HEADER)
resp = resp.json()
ref_sha = resp["object"]["sha"]

# Step 3. Create a new ref
branch_name = "fork_test_branch"
url = "/".join([fork_api, "git", "refs"])
body = {
    "ref": f"refs/heads/{branch_name}",
    "sha": ref_sha,
}
resp = requests.post(url, json=body, headers=HEADER)
resp = resp.json()
branch_sha = resp["object"]["sha"]

# Step 4. Get relevant file URLs
path = "test.md"
url = "/".join([fork_api, "contents", path])
query = {"ref": branch_name}
resp = requests.get(url, params=query, headers=HEADER)
resp = resp.json()
download_url = resp["download_url"]
blob_sha = resp["sha"]

# Step 5. Get the file contents
resp = requests.get(resp["download_url"], headers=HEADER)
file_contents = resp.text.strip("\n")

# Step 6. Edit the file contents
file_contents += "!"

# Step 7. Encode the file contents
encoded_file_contents = file_contents.encode("ascii")
base64_bytes = base64.b64encode(encoded_file_contents)
raw_contents = base64_bytes.decode("utf-8")

# Step 8. Replace the file in the repository
url = "/".join([fork_api, "contents", path])
body = {
    "message": f"Updating {path}",
    "content": raw_contents,
    "sha": blob_sha,
    "branch": branch_name,
}
requests.put(url, json=body, headers=HEADER)

# Step 9. Open a Pull Request
url = "/".join([repo_api, "pulls"])
body = {
    "title": f"Updating {path}",
    "body": "Adding an `!` to the Markdown",
    "base": "main",
    "head": f"{org_name}:{branch_name}",
}
requests.post(url, json=body, headers=HEADER)
