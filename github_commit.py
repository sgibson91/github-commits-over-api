import os
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

# Step 1. Get a reference to HEAD
url = "/".join([repo_api, "git", "ref", "heads", "main"])
resp = requests.get(url, headers=HEADER)
resp = resp.json()
commit_sha = resp["object"]["sha"]
obj_url = resp["object"]["url"]

# Step 2. Grab the commit HEAD points to
resp = requests.get(obj_url, headers=HEADER)
resp = resp.json()
tree_sha = resp["tree"]["sha"]
tree_url = resp["tree"]["url"]

# === Updating the file === #
# a. Download the file contents
path = "test.md"
url = "/".join([repo_api, "contents", path])
resp = requests.get(url, headers=HEADER)
resp = resp.json()
resp = requests.get(resp["download_url"], headers=HEADER)
file_contents = resp.text.strip("\n")

# b. Edit file contents
file_contents += " World"
# === END === #

# Step 3. Post new file to the server
url = "/".join([repo_api, "git", "blobs"])
body = {
    "content": file_contents,
    "encoding": "utf-8",
}
resp = requests.post(url, json=body, headers=HEADER)
resp = resp.json()
blob_sha = resp["sha"]

# Step 4. Create a tree containing the updated file
url = "/".join([repo_api, "git", "trees"])
body = {
    "base_tree": tree_sha,
    "tree": [
        {
            "path": path,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha,
        },
    ],
}
resp = requests.post(url, json=body, headers=HEADER)
resp = resp.json()
new_tree_sha = resp["sha"]

# Step 5. Create a commit
url = "/".join([repo_api, "git", "commits"])
body = {
    "message": f"Updating {path}: Add 'World'",
    "tree": new_tree_sha,
    "parents": [commit_sha],
}
resp = requests.post(url, json=body, headers=HEADER)
resp = resp.json()
new_commit_sha = resp["sha"]

# Step 6. Update HEAD to point to new commit
url = "/".join([repo_api, "git", "refs", "heads", "main"])
body = {"sha": new_commit_sha, "force": True}
requests.patch(url, json=body, headers=HEADER)
