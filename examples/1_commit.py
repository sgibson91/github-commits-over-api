import argparse
import os
import subprocess
import sys
import tempfile

import requests


def parse_args(args):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "repository", type=str, help="The repository to commit to in the form USER/REPO"
    )
    parser.add_argument(
        "filepath",
        type=str,
        help="The path to the file to be edited, relative to the repository root",
    )

    return parser.parse_args()


def main():
    # Verify GITHUB_TOKEN has been set in the environment
    token = os.environ["GITHUB_TOKEN"] if "GITHUB_TOKEN" in os.environ else None
    if token is None:
        raise ValueError("GITHUB_TOKEN must be set in the environment!")

    # Create a requests header
    HEADER = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }

    # Parse arguments from the command line
    args = parse_args(sys.argv[1:])

    # Set API URL
    API_ROOT = "https://api.github.com"
    repo_api = "/".join([API_ROOT, "repos", args.repository])

    # === Begin making the changes and commit === #
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

    # Step 3. Updating the file
    # 3a. Download the file contents
    url = "/".join([repo_api, "contents", args.filepath])
    resp = requests.get(url, headers=HEADER)
    resp = resp.json()
    resp = requests.get(resp["download_url"], headers=HEADER)

    # 3b. Dump the contents to a temporary file
    tmpf = tempfile.NamedTemporaryFile()
    with open(tmpf.name, "w") as f:
        f.write(resp.text)

    # 3c. Edit file contents
    subprocess.run(["nano", tmpf.name])

    # 3d. Read in edited file
    with open(tmpf.name, "r") as f:
        file_contents = f.read()

    # 3e. Clean up the temporary file
    tmpf.close()

    # Step 4. Post new file to the server
    url = "/".join([repo_api, "git", "blobs"])
    body = {
        "content": file_contents,
        "encoding": "utf-8",
    }
    resp = requests.post(url, json=body, headers=HEADER)
    resp = resp.json()
    blob_sha = resp["sha"]

    # Step 5. Create a tree containing the updated file
    url = "/".join([repo_api, "git", "trees"])
    body = {
        "base_tree": tree_sha,
        "tree": [
            {
                "path": args.filepath,
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha,
            },
        ],
    }
    resp = requests.post(url, json=body, headers=HEADER)
    resp = resp.json()
    new_tree_sha = resp["sha"]

    # Step 6. Create a commit
    print("Please provide a commit message:")
    msg = input("> ")

    url = "/".join([repo_api, "git", "commits"])
    body = {
        "message": msg,
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


if __name__ == "__main__":
    main()
