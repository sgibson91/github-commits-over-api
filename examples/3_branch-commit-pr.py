import argparse
import base64
import os
import subprocess
import sys
import tempfile

import requests


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="""
A script that creates a new branch, makes a commit to it, then opens a Pull
Request in a repository over the GitHub API
"""
    )

    parser.add_argument(
        "repository", type=str, help="The repository to commit to in the form USER/REPO"
    )
    parser.add_argument(
        "filepath",
        type=str,
        help="The path to the file to be edited, relative to the repository root",
    )
    parser.add_argument(
        "branch_name", type=str, help="The name of the new branch to create"
    )
    parser.add_argument(
        "-d",
        "--default-branch",
        type=str,
        default="main",
        help="The name of your default branch. Defaults to 'main'.",
    )

    return parser.parse_args()


def main():
    # Parse arguments from the command line
    args = parse_args(sys.argv[1:])

    # Verify GITHUB_TOKEN has been set in the environment
    token = os.environ["GITHUB_TOKEN"] if "GITHUB_TOKEN" in os.environ else None
    if token is None:
        raise ValueError("GITHUB_TOKEN must be set in the environment!")

    # Set API URL
    API_ROOT = "https://api.github.com"
    repo_api = "/".join([API_ROOT, "repos", args.repository])

    # Create a requests header
    HEADER = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }

    # === Begin making the branch, commit and Pull Request === #
    # Step 1. Get a reference to HEAD
    url = "/".join([repo_api, "git", "ref", "heads", args.default_branch])
    resp = requests.get(url, headers=HEADER)
    resp = resp.json()
    ref_sha = resp["object"]["sha"]

    # Step 2. Create a new branch
    url = "/".join([repo_api, "git", "refs"])
    body = {
        "ref": f"refs/heads/{args.branch_name}",
        "sha": ref_sha,
    }
    resp = requests.post(url, json=body, headers=HEADER)

    # Step 3. Get relevant file URLs
    url = "/".join([repo_api, "contents", args.filepath])
    query = {"ref": args.branch_name}
    resp = requests.get(url, params=query, headers=HEADER)
    resp = resp.json()
    blob_sha = resp["sha"]

    # Step 4. Updating the file
    # 4a. Getting the file contents
    resp = requests.get(resp["download_url"], headers=HEADER)

    # 4b. Dump the file contents to a temporary file
    tmpf = tempfile.NamedTemporaryFile()
    with open(tmpf.name, "w") as f:
        f.write(resp.text)

    # 4c. Edit the file contents
    subprocess.run(["nano", tmpf.name])

    # 4d. Read in the edited file
    with open(tmpf.name) as f:
        file_contents = f.read()

    # 4e. Clean up the temporary file
    tmpf.close()

    # Step 5. Encode the file contents
    encoded_file_contents = file_contents.encode("ascii")
    base64_bytes = base64.b64encode(encoded_file_contents)
    raw_contents = base64_bytes.decode("utf-8")

    # Step 6. Replace the file in the repository
    print("Please provide a commit message:")
    msg = input("> ")

    url = "/".join([repo_api, "contents", args.filepath])
    body = {
        "message": msg,
        "content": raw_contents,
        "sha": blob_sha,
        "branch": args.branch_name,
    }
    requests.put(url, json=body, headers=HEADER)

    # Step 7. Open a Pull Request
    print("Provide a title for your Pull Request:")
    pr_title = input("> ")

    print("Provide a description of your Pull Request:")
    pr_body = input("> ")

    url = "/".join([repo_api, "pulls"])
    body = {
        "title": pr_title,
        "body": pr_body,
        "base": args.default_branch,
        "head": args.branch_name,
    }
    requests.post(url, json=body, headers=HEADER)


if __name__ == "__main__":
    main()
