from .git import get_git_diff, get_git_status
from .todo import write_todos
from .web_search import web_fetch, web_search
from .utc_now import utc_now

# List of all available custom tools
AGENT_TOOLS = [
    get_git_status,
    get_git_diff,
    web_search,
    write_todos,
    utc_now,
]

RESEARCH_TOOLS = [
    utc_now,
    web_search,
]

GIT_TOOLS = [
    get_git_status,
    get_git_diff,
]
