"""Todo management tools for agent."""

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class TodoItem(BaseModel):
    id: str = Field(..., description="Unique ID for the task")
    content: str = Field(..., description="Task description")
    status: str = Field(
        "pending",
        description="Status: 'pending', 'in_progress', 'completed', 'cancelled'",
    )


@tool
def write_todos(todos: list[dict]) -> str:
    """
    Update the full todo/task list.
    Each todo should have 'id', 'content' and 'status'.
    Example: [{"id": "1", "content": "Search K8s cost", "status": "pending"}]
    """
    # In DeepAgents, returning this will update the state if 'todos' is a state key
    # For now, we return a confirmation. The orchestrator/runtime handles state sync.
    return f"Updated {len(todos)} tasks in the plan."
