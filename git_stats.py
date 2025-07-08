import subprocess
import os
from collections import defaultdict


def validate_repo_path(repo_path):
    """
    Validate that the given path is a Git repository.
    """
    if not os.path.isdir(repo_path):
        raise ValueError(f"The path '{repo_path}' is not a valid directory.")
    git_dir = os.path.join(repo_path, ".git")
    if not os.path.isdir(git_dir):
        raise ValueError(f"The path '{repo_path}' is not a valid Git repository.")


def run_git_command(repo_path, git_args):
    """
    Run a Git command in the specified repository.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + git_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git command failed: {e.stderr}")


def get_all_authors(repo_path):
    """
    Get a list of all authors who have contributed to the repository.
    """
    output = run_git_command(repo_path, ["log", "--pretty=format:%an"])
    authors = [name.split("\\")[-1] for name in output.split("\n")] # Split name if it has weird format like Domain\username
    return sorted(set(authors))


def get_author_stats(repo_path, author:str):
    """
    Get the number of commits, lines added, and lines deleted by the specified author.
    """
    # Count commits
    commits_output = run_git_command(
        repo_path, ["log", "--author", author, "--pretty=oneline"]
    )
    commit_count = len(commits_output.split("\n")) if commits_output else 0

    # Count lines added and deleted
    lines_output = run_git_command(
        repo_path, ["log", "--author", author, "--pretty=tformat:", "--numstat"]
    )
    lines_added = 0
    lines_deleted = 0
    for line in lines_output.split("\n"):
        if line:
            parts = line.split("\t")
            if len(parts) == 3:
                added, deleted, _ = parts
                lines_added += int(added) if added.isdigit() else 0
                lines_deleted += int(deleted) if deleted.isdigit() else 0

    return commit_count, lines_added, lines_deleted


if __name__ == "__main__":
    print("Enter the path to the Git repository:")
    repo_path = input().strip()

    # Validate the repository path
    try:
        validate_repo_path(repo_path)
    except ValueError as e:
        print(e)
        exit(1)

    print(f"Fetching all authors and their contributions from '{repo_path}'...")

    # Get all authors
    try:
        authors = get_all_authors(repo_path)
    except RuntimeError as e:
        print(e)
        exit(1)

    if not authors:
        print("No authors found in the repository.")
        exit(0)

    # Collect stats for each author
    author_stats = defaultdict(dict)
    for author in authors:
        try:
            commits, lines_added, lines_deleted = get_author_stats(repo_path, author)
            author_stats[author] = {
                "commits": commits,
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
            }
        except RuntimeError as e:
            print(f"Error processing stats for {author}: {e}")
            continue

    # Print the stats
    print(f"{'Author':<30} {'Commits':<10} {'Lines Added':<15} {'Lines Deleted':<15}")
    print("-" * 70)
    for author, stats in author_stats.items():
        print(
            f"{author:<30} {stats['commits']:<10} {stats['lines_added']:<15} {stats['lines_deleted']:<15}"
        )