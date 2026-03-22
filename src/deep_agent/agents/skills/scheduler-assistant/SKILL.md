---
name: scheduler-assistant
description: Scheduled tasks and heartbeat management skill. Used when the user involves reminders, scheduled tasks, periodic checks, or heartbeat triggers. Supports creation, query, modification, and deletion of one-time reminders and periodic tasks.
---

# Scheduled Tasks and Heartbeat Management

Let AI help users set up and manage scheduled tasks and heartbeats within the conversation, without needing to go to a UI panel.

---

## AI Decision Guide

### Time Confirmation Rules

> Before setting a reminder, first confirm the current system time (check time information in the context, or execute the `date` command via execute).
> Pure relative times ("In 5 minutes", "1 hour later") can skip confirmation and directly use current time + delay to calculate the ISO timestamp.
> When involving specific dates or vague times ("Tomorrow afternoon", "Next Monday"), first confirm the current date before calculating.

### User Intent Recognition

> **Most important judgment**: Does the user want the agent to **do something** (Action type) or just be **reminded** (Reminder type)?
> - This determines the value of the `taskType` field: `"action"` or `"reminder"`
> - "Remind me to drink water" → `taskType="reminder"`
> - "Help me fix plaintext passwords" / "Check security issues in the code" / "Scan project dependencies" → `taskType="action"`
> - Judgment criteria: If the user's request contains **action verbs** like "fix/check/scan/refactor/deploy/run/build/clean/replace/analyze", it is an `"action"`
> - **When in doubt, default to `"action"`**

| User Statement | Intent | taskType | Key Parameters |
|----------|------|----------|----------|
| "Remind me to drink water in 5 minutes" | One-time reminder | `"reminder"` | frequency=once, runAt=ISO timestamp |
| "Remind me to check emails every day at 9 AM" | Periodic reminder | `"reminder"` | frequency=daily, runAtTime="09:00" |
| "Help me fix plaintext passwords in the workspace" | **Action Task** | `"action"` | frequency=once/manual |
| "Check for security vulnerabilities in the project every day" | **Periodic Action** | `"action"` | frequency=daily, runAtTime |
| "Check service status every 5 minutes" | **High-frequency Action** | `"action"` | frequency=interval, intervalMinutes=5 |
| "Remind me to move around every hour" | Periodic reminder | `"reminder"` | frequency=hourly |
| "Remind me to write the daily report at 6 PM on weekdays" | Weekday reminder | `"reminder"` | frequency=weekdays, runAtTime="18:00" |
| "Scan TODOs in the code and summarize" | **Action Task** | `"action"` | frequency=once/manual |
| "Generate project progress report every Monday" | **Periodic Action** | `"action"` | frequency=weekly, weekday=1 |
| "What scheduled tasks do I have?" | Query | - | action=list |
| "Cancel/Delete xx reminder" | Delete | - | action=delete, first list to find taskId |
| "Pause xx task" | Disable | - | action=disable, taskId |
| "Resume xx task" | Enable | - | action=enable, taskId |
| "Execute xx task immediately" | Manual trigger | - | action=run, taskId |
| "Check execution records of xx task" | View history | - | action=runs, taskId |
| "Check the heartbeat" | Trigger heartbeat | - | action=wake |
| "Check scheduler status" | View status | - | action=status |
| "Change the time of xx reminder" | Update | - | action=update, taskId + modified fields |

### Mandatory Follow-up Situations

1. **No time specified**: "Remind me to drink water" -> "When should I remind you? e.g., in 5 minutes, every day at 9 AM, etc."
2. **Vague time**: "Remind me later" -> "What time exactly? Or how long from now?"
3. **Unknown frequency**: "Remind me regularly" -> "How often? Every day? Every week? Every hour?"
4. **Unknown reminder content**: Only mentioned time but not what to do -> "What do you need to be reminded about?"

---

## manage_scheduler Tool Calling Templates

> ⚠️ **The `taskType` field is mandatory**——it determines how the prompt is handled:
> - `taskType="action"`: The prompt is sent exactly as is to the agent to execute
> - `taskType="reminder"`: The prompt only needs to contain the reminder text, the system will automatically wrap it in a friendly template

### Action Task Examples (taskType="action")

**One-time execution——Fix plaintext passwords**:
```json
{
  "action": "create",
  "taskType": "action",
  "name": "Fix Plaintext Passwords",
  "description": "Scan and fix plaintext passwords in the workspace",
  "prompt": "Please scan all source files in D:\\git\\lf39.031\\LF39.18_WE directory to find hardcoded plaintext passwords (such as password=xxx in DB connection strings, keys in configs). For each plaintext password found:\n1. Replace it with an environment variable reference or encrypted config\n2. Record the modified file and line number\n3. Output a summary of modifications",
  "frequency": "once",
  "runAt": "2026-03-08T23:35:00+08:00"
}
```

**Daily execution——Security check**:
```json
{
  "action": "create",
  "taskType": "action",
  "name": "Daily Security Check",
  "description": "Check project for security issues every day at 9 AM",
  "prompt": "Please perform a security check on ~/projects/myapp:\n1. Scan source code for hardcoded keys, tokens, or passwords\n2. Check for insecure HTTP calls\n3. Output a security check report listing discovered issues and suggested fixes",
  "frequency": "daily",
  "runAtTime": "09:00"
}
```

**Minute-level execution——Check service every 5 minutes**:
```json
{
  "action": "create",
  "taskType": "action",
  "name": "Service Status Check",
  "description": "Check if the service is running normally every 5 minutes",
  "prompt": "Please check the service status of ~/projects/myapp:\n1. Execute curl http://localhost:3000/health to check the health endpoint\n2. If the service does not respond or returns an error, output detailed error info\n3. Output a status check summary",
  "frequency": "interval",
  "intervalMinutes": 5
}
```

**Weekly execution——Project report**:
```json
{
  "action": "create",
  "taskType": "action",
  "name": "Weekly Report Generation",
  "description": "Generate project progress report every Monday",
  "prompt": "Please analyze the git log of the past week in ~/projects/myapp to generate a project progress report:\n1. Number of new commits and main changes this week\n2. Active development branches\n3. Completion status of tasks in TODO.md\nOutput the report in markdown format.",
  "frequency": "weekly",
  "runAtTime": "10:00",
  "weekday": 1
}
```

---

### Reminder Task Examples (taskType="reminder")

> Only used for "Remind me to do X" scenarios, where the user will do it themselves.
> The prompt only needs the **reminder content**, and the system will wrap it in a friendly template.

**One-time reminder (N minutes/hours later)**:

> runAt must be an ISO-8601 timestamp with a timezone offset (like `+08:00`), **Using Z (UTC) is forbidden**, you must calculate it yourself.

```json
{
  "action": "create",
  "taskType": "reminder",
  "name": "Drink Water Reminder",
  "description": "Remind to drink water in 5 minutes",
  "prompt": "It's time to drink water",
  "frequency": "once",
  "runAt": "2026-03-08T23:35:00+08:00"
}
```

**Time Calculation Method**:
| User Statement | Calculation Method |
|----------|----------|
| In 5 minutes | Current local time + 5 minutes, with timezone offset (e.g. `+08:00`) |
| In half an hour | Current local time + 30 minutes |
| In 1 hour | Current local time + 60 minutes |
| Tomorrow at 8 AM | Confirm current date, calculate tomorrow's target time, with timezone offset |

> **IMPORTANT**: runAt always uses local time + timezone offset format, such as `2026-03-09T01:32:00+08:00`, NEVER use the `Z` suffix.

**Daily reminder**:
```json
{
  "action": "create",
  "taskType": "reminder",
  "name": "Check Emails Reminder",
  "description": "Check emails every day at 9 AM",
  "prompt": "It's time to check today's emails, don't let urgent matters slip by",
  "frequency": "daily",
  "runAtTime": "09:00"
}
```

**Weekly reminder** (weekday: 0=Sunday, 1=Monday, ..., 6=Saturday):
```json
{
  "action": "create",
  "taskType": "reminder",
  "name": "Weekly Meeting Reminder",
  "description": "Weekly meeting every Monday at 10 AM",
  "prompt": "The weekly meeting is about to start, get your weekly work report ready",
  "frequency": "weekly",
  "runAtTime": "10:00",
  "weekday": 1
}
```

---

### Tasks with Conversation Context (contextMessages)

> When the user says "remind me about this" during a discussion, use `contextMessages` to automatically attach the current conversation content to the prompt,
> letting the agent know "what it's about" when triggered.

```json
{
  "action": "create",
  "taskType": "reminder",
  "name": "Follow Up on Plan Reminder",
  "description": "Remind to follow up on the plan just discussed in 30 minutes",
  "prompt": "It's time to follow up on the plan we discussed earlier, check if there are any missing details",
  "frequency": "once",
  "runAt": "2026-03-09T00:00:00+08:00",
  "contextMessages": 5
}
```

**contextMessages Usage Principles**:
- Value between 1-10, representing taking the most recent N messages from the current conversation
- Applicable scenario: User discussing something and says "remind me about this", context needs storing
- Inapplicable scenario: Generic reminders (like "drink water every day"), doesn't need context
- Context will be auto-truncated, max 220 chars per message, max 700 chars total
- If `contextAttached` is `false` in the returned result and you passed `contextMessages`, you should explain to the user: Failed to get conversation context, this task is not attached to the recent conversation

---

### View Task Execution History (runs)

```json
{
  "action": "runs",
  "taskId": "Task ID",
  "limit": 5
}
```

Returns the latest N execution records, including: start time, end time, status (ok/error), error info, and duration.

---

## Prompt Writing Guide

> **Core mechanism**: When a scheduled task triggers, an independent agent executes the prompt in a background thread.
> This agent **has full tool capabilities** (read/write files, execute commands, search code, etc.), and can perform real operations.
> After execution, the system will auto-send a desktop notification (showing the first 200 chars of the agent's output), and write the full output to the background thread.
>
> **`taskType` determines prompt handling**:
> - `taskType="action"`: The prompt is sent exactly as is to the agent, the agent will call tools to perform actual operations
> - `taskType="reminder"`: The prompt only needs the reminder content (e.g. "it's time to drink water"), the system auto-wraps a friendly template
> - **Do not write "Remind user xxx" or "Notify user"**——the agent cannot push actively, it can only output content to the thread

### prompt writing for taskType="action"

> The agent receives the exact prompt text and calls tools to execute. Clearly write what to do and where to do it.

**Requirements**:
1. Clearly state the operation to be performed
2. Include the absolute path of the working directory
3. State specific operation steps and expected results

**Example**:
```
Please scan all source files in the D:\git\lf39.031\LF39.18_WE directory to find hardcoded plaintext passwords.
For each plaintext password found:
1. Replace it with an environment variable reference or encrypted config
2. Record the modified file and line number
3. Lastly, output a summary of modifications
```

### prompt writing for taskType="reminder"

> Just fill in the reminder content, system auto-wraps a friendly template. You don't need to manually write templates.

**Example**: prompt is `It's time to drink water`, system auto-generates full prompt, agent might output:
`💧 Hey keyboard warrior! You've been typing for a long time, time to move your mouth~ Drink some water and refresh your body!`

### Writing Principles

1. **Pick taskType First**: Action verb → `"action"`; "Remind me" → `"reminder"`. **Wrong choice = Invalid task**
2. **Self-contained**: When triggered, the agent has no original context, all necessary info must be written in the prompt
3. **Use contextMessages wisely**: If the task relates to the current conversation, set contextMessages=3~5 to auto-attach context
4. **Include paths**: For `"action"` types involving files, write absolute paths clearly (obtain via current workDir)
5. **Be specific and clear**: Avoid vague instructions, clearly state specific steps
6. **Do NOT write "Notify user" or "Remind user"**: The agent only outputs to background thread, the system will auto-send desktop notifications

---

## User Interaction Templates

### Creation Success Feedback

**One-time Reminder**:
```
Okay, I will remind you {Reminder Content} in {Time}.
```

**Periodic Reminder**:
```
I've set up a {Period Description} reminder for {Reminder Content}, next execution time: {nextRunAt}.
```

### Query Results Feedback

```
Current scheduled tasks:

1. {name} - {frequency}{Time} - {enabled Status}
2. {name} - {frequency}{Time} - {enabled Status}

You can say "Cancel xx" to delete, or "Pause xx" to disable a task.
```

### No Tasks Feedback

```
Currently no scheduled tasks. You can say "Remind me xxx in 5 minutes" or "Remind me xxx every day at 9 AM" to create a task.
```

### Deletion Success Feedback

```
Deleted "{Task Name}".
```

### Execution History Feedback

```
The last {N} execution records of "{Task Name}":

| Time | Status | Duration |
|------|------|------|
| {startedAt} | {status} | {durationMs}ms |

{If there are errors, display error message}
```

### Disable/Enable Feedback

```
Paused "{Task Name}", it will no longer execute. Say "Resume {Task Name}" to re-enable.
```

```
Resumed "{Task Name}", next execution time: {nextRunAt}.
```

---

## Scheduled Tasks vs Heartbeat: When to use which

| Scenario | Recommended | Reason |
|------|---------|------|
| "Remind me to have a meeting in 5 minutes" | Scheduled Task (once) | Precise time, one-off |
| "Check emails every day at 9 AM" | Scheduled Task (daily) | Precise time, periodic |
| "Check service status every 5 mins" | Scheduled Task (interval) | Minute-level precision interval |
| "Check project status regularly" | Heartbeat (HEARTBEAT.md) | Can be merged with other checks, precise time unnecessary |
| "Continuously monitor if service is normal" | Scheduled (interval) or Heartbeat | Needs precise interval = interval, else heartbeat |
| "Report on project every Monday" | Scheduled Task (weekly) | Precise time, independent task |

**Simple Rule**:
- Needs precise time -> Scheduled Task
- Needs minute-level intervals -> Scheduled Task (interval)
- Periodic checks, batchable -> Heartbeat (add check items in HEARTBEAT.md)
- One-time reminder -> Scheduled Task (once)

When user needs fit heartbeat, recommend user go to Heartbeat settings panel to configure HEARTBEAT.md, or help user edit `~/.cmbcoworkagent/HEARTBEAT.md` directly via edit_file.

---

## Operation Workflow

### Create Task

1. Identify user intent (Reminder/Scheduled Task)
2. Confirm time (ask follow-ups if necessary)
3. Get current time (relative times need calculating absolute timestamps)
4. Call manage_scheduler(action="create", ...)
5. Feedback creation result (include next execution time)

### Modify Task

1. User wants to modify -> list first to find taskId
2. Call manage_scheduler(action="update", taskId=..., changed fields)
3. Feedback modify result

### Delete Task

1. User wants to cancel/delete -> list first to find taskId
2. If there are multiple similar tasks, confirm with user
3. Call manage_scheduler(action="delete", taskId=...)
4. Feedback deletion result

### View Execution History

1. User wants history of a task -> list first to find taskId
2. Call manage_scheduler(action="runs", taskId=..., limit=5)
3. Feedback execution history in table format

### Trigger Heartbeat

1. User says check heartbeat / trigger heartbeat
2. Call manage_scheduler(action="wake")
3. Feedback heartbeat triggered (executes asynchronously)
