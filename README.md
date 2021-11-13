# Committing files over the GitHub API with Python

This is a demo repo where I was testing making commits over the GitHub API using Python and the `requests` library.
I've found this method useful when automating tasks that involve interacting with the GitHub API.
It removes the need to have `git` installed in the environment your process is running in, and removes the need to clone the repository locally for the sake of editing one or two files.

All code can be found in the [`examples` folder](./examples).
The requirements for the code can be installed by running

```bash
pip install -r requirements.txt
```

To run these examples, you will need to [create a Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) (the `public_repo` scope should be adequate) and add it to your bash environment.

```bash
export GITHUB_TOKEN="PASTE YOUR TOKEN HERE"
```

Each example script requires the repo to interact with, in the form `user/repo`, and the path to the file to edit relative to the root of the repo, e.g.:

```bash
python examples/<SCRIPT_NAME> sgibson91/github-commits-over-api README.md
```

Some of the more complex workflow examples may require additional inputs.
You can get the help for each example by running

```bash
python examples/<SCRIPT_NAME> --help
```

### The Examples

- [`1_commit.py`](examples/1_commit.py): My first attempt, largely following this blog: <http://www.levibotelho.com/development/commit-a-file-with-the-github-api/>
- [`2_commit-simple.py`](examples/2_commit-simple.py): Then I found a shortcut for all the blob and tree stuff which reduced the number of steps/API calls required
- [`3_branch-commit-pr.py`](examples/3_branch-commit-pr.py): Replicates the workflow of creating a branch, committing to it and opening a Pull Request
- [`4_fork-branch-commit-pr.py`](examples/4_fork-branch-commit-pr.py): Replicates the workflow of forking the repo, creating a branch, committing to the branch, and opening a Pull Request back to the original repo
