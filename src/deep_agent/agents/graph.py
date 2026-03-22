"""Deep Agent graph for deployment."""

from __future__ import annotations

import contextlib

from langchain_core.runnables import RunnableConfig
from deep_agent.llm import llm

from deepagents import create_deep_agent
from langgraph_sdk.runtime import ServerRuntime
from deep_agent.settings import settings

from deep_agent.agents.sandbox import get_or_create_sandbox
from deep_agent.agents.contexts.prompt import SUBAGENTS
from deep_agent.agents.contexts.prompt import SYSTEM_PROMPT
from deep_agent.agents.tools import AGENT_TOOLS
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()


def _build_agent(backend=None):
    return create_deep_agent(
        model=llm,
        tools=AGENT_TOOLS,
        backend=backend,
        system_prompt=SYSTEM_PROMPT,
        subagents=SUBAGENTS,
        skills=["src/deep_agent/agents/skills"],
        memory="src/deep_agent/agents/contexts/AGENTS.md",
        # You can disable these if you want to run without interrupts
        interrupt_on={"execute": True, "write_file": True},
        name="deep_agent",
        checkpointer=checkpointer,
    )


RO_AGENT = _build_agent()
backend = None


@contextlib.asynccontextmanager
async def get_agent(config: RunnableConfig, runtime: ServerRuntime):
    ert = runtime.execution_runtime
    if ert and settings.use_sandbox:
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        backend = await get_or_create_sandbox(thread_id)
        yield _build_agent(backend=backend)
    else:
        yield RO_AGENT
