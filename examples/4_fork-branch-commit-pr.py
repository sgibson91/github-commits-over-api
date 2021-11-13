import argparse
import base64
import os
import subprocess
import sys
import tempfile
import time

import requests


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="""
A script that forks a repository on GitHub, creates a new branch in the fork,
makes a commit to that branch, and then opens a Pull Request back to the original
repository. All over the GitHub API.
"""
    )

    parser.add_argument(
        "repository",
        type=str,
        help="The repository to commit to in the form USER/REPO",
    )
    parser.add_argument(
        "filepath",
        type=str,
        help="The path to the file to be edited, relative to the repository root",
    )
    parser.add_argument(
        "branch_name",
        type=str,
        help="The name of the new branch to create",
    )
    parser.add_argument(
        "-d",
        "--default-branch",
        type=str,
        default="main",
        help="The name of your default branch. Defaults to 'main'.",
    )
    parser.add_argument(
        "-o",
        "--org-name",
        type=str,
        default=None,
        help="The name of the organisation to create a fork for, if not a user. Defaults to None.",
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
    # Step 1. Fork the repo
    url = "/".join([repo_api, "forks"])

    if args.org_name is None:
        body = {}
    else:
        body = {"organization": args.org_name}

    requests.post(url, json=body, headers=HEADER)

    # Step 2. Set fork API
    repo_name = args.repository.split("/")[-1]

    if args.org_name is None:
        # Get the authenticated user
        url = "/".join([API_ROOT, "user"])
        resp = requests.get(url, headers=HEADER)
        resp = resp.json()
        user = resp["login"]
        fork_api = "/".join([API_ROOT, "repos", user, repo_name])
    else:
        fork_api = "/".join([API_ROOT, "repos", args.org_name, repo_name])

    # Wait a short amount of time for the fork to resolve asynchronously
    time.sleep(5)

    # Step 2. Get a reference to HEAD
    url = "/".join([fork_api, "git", "ref", "heads", args.default_branch])
    resp = requests.get(url, headers=HEADER)
    resp = resp.json()
    ref_sha = resp["object"]["sha"]

    # Step 3. Create a new branch
    url = "/".join([fork_api, "git", "refs"])
    body = {
        "ref": f"refs/heads/{args.branch_name}",
        "sha": ref_sha,
    }
    resp = requests.post(url, json=body, headers=HEADER)
    resp = resp.json()

    # Step 4. Get the relevant file URLs
    url = "/".join([fork_api, "contents", args.filepath])
    query = {"ref": args.branch_name}
    resp = requests.get(url, params=query, headers=HEADER)
    resp = resp.json()
    blob_sha = resp["sha"]

    # Step 5. Updating the file
    # 5a. Getting the file contents
    resp = requests.get(resp["download_url"], headers=HEADER)

    # 5b. Dump the file contents in a temporary file
    tmpf = tempfile.NamedTemporaryFile()
    with open(tmpf.name, "w") as f:
        f.write(resp.text)

    # 5c. Edit the file contents
    subprocess.run(["nano", tmpf.name])

    # 5d. Read in the edited file
    with open(tmpf.name, "r") as f:
        file_contents = f.read()

    # 5e. Clean up the temporary file
    tmpf.close()

    # Step 6. Encode the file contents
    encoded_file_contents = file_contents.encode("ascii")
    base64_bytes = base64.b64encode(encoded_file_contents)
    raw_contents = base64_bytes.decode("utf-8")

    # Step 8. Replace the file in the repository
    print("Provide a commit message:")
    msg = input("> ")

    url = "/".join([fork_api, "contents", args.filepath])
    body = {
        "message": msg,
        "content": raw_contents,
        "sha": blob_sha,
        "branch": args.branch_name,
    }
    requests.put(url, json=body, headers=HEADER)

    # Step 9. Open a Pull Request
    print("Provide a title for your Pull Request:")
    pr_title = input("> ")

    print("Provide a description for your Pull Request:")
    pr_body = input("> ")

    url = "/".join([repo_api, "pulls"])

    if args.org_name is None:
        body = {
            "title": pr_title,
            "body": pr_body,
            "base": args.default_branch,
            "head": f"{user}:{args.branch_name}",
        }
    else:
        body = {
            "title": pr_title,
            "body": pr_body,
            "base": args.default_branch,
            "head": f"{args.org_name}:{args.branch_name}",
        }

    requests.post(url, json=body, headers=HEADER)


if __name__ == "__main__":
    main()
