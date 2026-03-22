import subprocess

from langchain_core.tools import tool


@tool
def get_git_status() -> str:
    """Get the current status of the git repository.
    Returns the output of `git status` or an error message if git is not initialized.
    """
    try:
        result = subprocess.run(
            ["git", "status"], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running git status: {e.stderr}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@tool
def get_git_diff() -> str:
    """Get the current diff of the git repository.
    Returns the output of `git diff` to see unstaged changes.
    """
    try:
        result = subprocess.run(
            ["git", "diff"], capture_output=True, text=True, check=True
        )
        return result.stdout or "No unstaged changes."
    except subprocess.CalledProcessError as e:
        return f"Error running git diff: {e.stderr}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
