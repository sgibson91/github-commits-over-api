# Committing files over the GitHub API

This is a little repo where I was testing making commits over the GitHub API.

- `github_commit.py`: My first attempt, largely following this blog: http://www.levibotelho.com/development/commit-a-file-with-the-github-api/
- `github_commit_simple.py`: Then I found a shortcut for all the blob and tree stuff which reduced the number of steps/API calls required
- `github_commit_branch_pr.py`: Replicates the workflow of creating a branch, committing to it and opening a PR
- `github_commit_fork_pr.py`: Replicates the workflow of forking the repo, creating a branch, committing to the branch, and opening a PR back to the original repo
