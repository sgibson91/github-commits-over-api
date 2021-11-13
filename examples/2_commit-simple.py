import argparse
import base64
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
    # Step 1. Get relevant URLs
    url = "/".join([repo_api, "contents", args.filepath])
    resp = requests.get(url, headers=HEADER)
    resp = resp.json()
    blob_sha = resp["sha"]

    # Step 2. Updating the file
    # 2a. Getting the file contents
    resp = requests.get(resp["download_url"], headers=HEADER)

    # 2b. Dump the contents to a temporary file
    tmpf = tempfile.NamedTemporaryFile()
    with open(tmpf.name, "w") as f:
        f.write(resp.text)

    # 2c. Edit the file contents
    subprocess.run(["nano", tmpf.name])

    # 2d. Read in the edited file
    with open(tmpf.name, "r") as f:
        file_contents = f.read()

    # 2e. Clean up the temporary file
    tmpf.close()

    # Step 4. Encode the file contents
    encoded_file_contents = file_contents.encode("ascii")
    base64_bytes = base64.b64encode(encoded_file_contents)
    raw_contents = base64_bytes.decode("utf-8")

    # Step 5. Replace the file in the repository
    print("Please provide a commit message:")
    msg = input("> ")

    url = "/".join([repo_api, "contents", args.filepath])
    body = {
        "message": msg,
        "content": raw_contents,
        "sha": blob_sha,
    }
    requests.put(url, json=body, headers=HEADER)

    # That's it! HEAD is automatically updated!


if __name__ == "__main__":
    main()
