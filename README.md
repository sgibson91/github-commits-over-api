# Committing files over the GitHub API

This is a demo repo where I was testing making commits over the GitHub API.
All code can be found in the [`examples` folder](./examples).

- [`1_commit.py`](examples/1_commit.py): My first attempt, largely following this blog: <http://www.levibotelho.com/development/commit-a-file-with-the-github-api/>
- [`2_commit-simple.py`](examples/2_commit-simple.py): Then I found a shortcut for all the blob and tree stuff which reduced the number of steps/API calls required
- [`3_branch-commit-pr.py`](examples/3_branch-commit-pr.py): Replicates the workflow of creating a branch, committing to it and opening a Pull Request
- [`4_fork-branch-commit-pr.py`](examples/4_fork-branch-commit-pr.py): Replicates the workflow of forking the repo, creating a branch, committing to the branch, and opening a Pull Request back to the original repo
