import os
import base64
import requests

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

# Step 1. Get a reference to HEAD
url = "/".join([repo_api, "git", "ref", "heads", "main"])
resp = requests.get(url, headers=HEADER)
resp = resp.json()
ref_sha = resp["object"]["sha"]

# Step 2. Create a new ref
branch_name = "test_branch"
url = "/".join([repo_api, "git", "refs"])
body = {
    "ref": f"refs/heads/{branch_name}",
    "sha": ref_sha,
}
resp = requests.post(url, json=body, headers=HEADER)
resp = resp.json()
branch_sha = resp["object"]["sha"]

# Step 3. Get relevant file URLs
path = "test.md"
url = "/".join([repo_api, "contents", path])
query = {"ref": branch_name}
resp = requests.get(url, params=query, headers=HEADER)
resp = resp.json()
download_url = resp["download_url"]
blob_sha = resp["sha"]

# Step 4. Get the file contents
resp = requests.get(resp["download_url"], headers=HEADER)
file_contents = resp.text.strip("\n")

# Step 5. Edit the file contents
file_contents += "!"

# Step 6. Encode the file contents
encoded_file_contents = file_contents.encode("ascii")
base64_bytes = base64.b64encode(encoded_file_contents)
raw_contents = base64_bytes.decode("utf-8")

# Step 7. Replace the file in the repository
url = "/".join([repo_api, "contents", path])
body = {
    "message": f"Updating {path}",
    "content": raw_contents,
    "sha": blob_sha,
    "branch": branch_name,
}
requests.put(url, json=body, headers=HEADER)

# Step 7. Open a Pull Request
url = "/".join([repo_api, "pulls"])
body = {
    "title": f"Updating {path}",
    "body": "Adding an `!` to the Markdown",
    "base": "main",
    "head": branch_name,
}
requests.post(url, json=body, headers=HEADER)
