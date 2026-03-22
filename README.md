# Deep Agents Lab

Deployment lab for a deep agent built with `create_deep_agent(...)`.

## What this lab gives you

- **Modern Graph Structure**: A deployable deep agent graph at `src/deep_agent/agents/graph.py`.
- **Advanced Workflow**: Explicit workflow prompt (plan, delegate, critique, finalize).
- **Sub-Agents**: Predefined specialized sub-agents (`researcher`, `critic`) located in `src/deep_agent/agents/contexts/prompt.py`.
- **Custom Tools**: Built-in tools for Git operations, web searching, and task management.
- **Human-in-the-loop**: Interrupts on sensitive actions like `execute` and `write_file`.
- **Configurable Backend**: Option to toggle between LangSmith Sandboxes and local execution.

## Prerequisites

- An API key for your model provider (OpenRouter used in this lab).
- A [LangSmith](https://smith.langchain.com/) account for tracing and optional sandboxes.

## Configuration

1. **Sync the project**:
   ```bash
   uv sync
   cp .env.example .env
   ```

2. **Setup your `.env`**:
   - `model`: Model ID (e.g., `openrouter:google/gemini-2.0-flash-lite-001`).
   - `api_key`: Your provider API key.
   - `USE_SANDBOX`: Set to `false` to disable LangSmith Sandboxes if you don't have a Plus plan or want to run locally.

## Available Tools

The agent comes with the following custom tools defined in `src/deep_agent/agents/tools/`:
- **Git**: `get_git_status`, `get_git_diff` for repository awareness.
- **Search**: `web_search` (DuckDuckGo with security hardening).
- **Tasks**: `write_todos` for managing project task lists.
- **Utilities**: `utc_now` for time-aware operations.

## Development

1. **Start the dev server**:
   ```bash
   uv run langgraph dev
   ```

2. **Run tests and linting**:
   ```bash
   make test
   make lint
   make format
   ```

## Structure

```text
src/deep_agent/
├── agents/             # Core agent logic
│   ├── contexts/       # Prompts and agent definitions
│   ├── tools/          # Custom tool implementations
│   ├── skills/         # Complex behaviors (if any)
│   ├── graph.py        # Main LangGraph entry point
│   └── sandbox.py      # Backend configuration
├── llm.py              # LLM initialization
└── settings.py         # Configuration management
```

## Reference docs

- LangGraph: [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
- Deep Agents: [https://docs.langchain.com/oss/python/deepagents/overview](https://docs.langchain.com/oss/python/deepagents/overview)
