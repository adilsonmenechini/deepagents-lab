# Task: Map Agents and Subagents to JSON

## Objective
Implement a mechanism to map the current agent and subagent structure into a specific JSON format for team coordination and visualization.

## JSON Target Format
```json
{
  "agents": [
    {
      "id": "agent-id",
      "name": "agent-name",
      "role": "Role Description",
      "prompt": "System prompt or mission",
      "parent": "parent-id or null",
      "children": ["child-id-1", "child-id-2"],
      "capabilities": {
        "skills": ["skill1", "skill2"],
        "tools": ["tool1", "tool2"],
        "policies": ["policy1"]
      },
      "context_scope": "global/local",
      "status": "idle/busy",
      "created_at": 1773834058.550273,
      "updated_at": 1773834058.550273
    }
  ]
}
```

## Subtasks
- [ ] Define `AgentModel` and `AgentCapability` Pydantic models to match the schema.
- [ ] Implement a `Mapper` class or function in `src/deep_agent/agents/contexts/prompt.py` (or a new module) to convert the current `SUBAGENTS` and `SYSTEM_PROMPT` into the JSON format.
- [ ] Add `created_at` and `updated_at` timestamps using `utc_now`.
- [ ] Map `AGENT_TOOLS` and `RESEARCH_TOOLS` names to the `capabilities.tools` list.
- [ ] Update `src/deep_agent/agents/contexts/prompt.py` to include this mapping logic.

## Implementation Details
The lead agent will be the main `deep_agent` defined in `graph.py`, and subagents from `SUBAGENTS` will be its children.
