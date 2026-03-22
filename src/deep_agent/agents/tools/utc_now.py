from datetime import datetime, timezone

from langchain_core.tools import tool


@tool
def utc_now() -> str:
    """Return the current UTC timestamp in ISO format."""
    return datetime.now(tz=timezone.utc).isoformat()
