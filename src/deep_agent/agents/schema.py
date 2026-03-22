import json
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from deep_agent.agents.tools import AGENT_TOOLS, RESEARCH_TOOLS
from deep_agent.agents.tools.utc_now import utc_now

# Tool mapping for config conversion
TOOL_MAP = {
    "AGENT_TOOLS": AGENT_TOOLS,
    "RESEARCH_TOOLS": RESEARCH_TOOLS,
    "utc_now": [utc_now],
}

class AgentCapabilities(BaseModel):
    skills: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    policies: List[str] = Field(default_factory=list)

class AgentModel(BaseModel):
    id: str
    name: str
    role: str
    prompt: str
    parent: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    capabilities: AgentCapabilities
    context_scope: str = "global"
    status: str = "idle"

class AgentsConfig(BaseModel):
    agents: List[AgentModel]

def load_agents_config(config_path: str = None) -> AgentsConfig:
    if config_path is None:
        # Default path relative to this file
        config_path = os.path.join(os.path.dirname(__file__), "config/agents.json")
    
    with open(config_path, "r") as f:
        data = json.load(f)
    
    return AgentsConfig(**data)

def get_agent_definitions():
    """Returns SYSTEM_PROMPT, SUBAGENTS, skills and policies from config."""
    config = load_agents_config()
    
    lead_agent = next((a for a in config.agents if a.id == "lead-1"), None)
    if not lead_agent:
        raise ValueError("Lead agent (id='lead-1') not found in config.")
    
    system_prompt = lead_agent.prompt
    
    # Skills mapping: Use defined skills if they exist as directories, otherwise fallback to default
    skills = []
    base_skills_path = "src/deep_agent/agents/skills"
    
    # Map high-level skills to actual directories if they match, or just use the base path
    # If the JSON has specific skill identifiers that match folders, we add them
    for skill_name in lead_agent.capabilities.skills:
        skill_path = os.path.join(base_skills_path, skill_name)
        # Check if directory exists
        if os.path.isdir(skill_path):
            skills.append(skill_path)
    
    # If no specific skill directories matched, or we want the whole folder
    if not skills:
        skills = [base_skills_path]

    # Policies mapping: Map to interrupt_on configuration
    # Example: if 'execute' in policies, we might want to interrupt on it
    policies = lead_agent.capabilities.policies
    interrupt_on = {}
    if "execute" in policies:
        # Based on lead-1 JSON, 'execute' is present
        interrupt_on["execute"] = True
    if "write" in policies:
        # Based on lead-1 JSON, 'write' is present
        interrupt_on["write_file"] = True

    subagents = []
    for agent in config.agents:
        if agent.id != "lead-1":
            tool_list = []
            for t_name in agent.capabilities.tools:
                if t_name in TOOL_MAP:
                    tl = TOOL_MAP[t_name]
                    if isinstance(tl, list):
                        tool_list.extend(tl)
                    else:
                        tool_list.append(tl)
            
            subagents.append({
                "name": agent.name,
                "description": agent.role,
                "system_prompt": agent.prompt,
                "tools": tool_list
            })
            
    return system_prompt, subagents, skills, interrupt_on
