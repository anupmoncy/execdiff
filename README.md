# Monitor AI Tool Workspace Changes

AI coding tools like GitHub Copilot, Cursor, Replit AI, and agentic workflows install dependencies, modify configurations, and run setup commands in a project workspace.

## Tracking Changes Beyond Git

If GitHub Copilot implements a feature like API integration, it may:

- Generate code.
- Install libraries via the terminal.
- Modify configuration files.
- Create output files.

But when something breaks after execution, Git only shows code changes — not:

- newly installed packages
- runtime-created files
- deleted files
- config updates done during execution

So it’s hard to tell what actually changed after an AI copilot action.

Here’s how to capture everything automatically using VS Code (or any IDE with a terminal).

---

## Step 1: Open Your Project in Your IDE

Open your project folder in VS Code (or any IDE).

Now open the integrated terminal: **Terminal → New Terminal**

---

## Step 2 (Optional): Create a Project-Level Python Environment

If you want installs isolated to this project:

```bash
python3 -m venv venv
source venv/bin/activate
```

Otherwise, you can skip this step.

---

## Step 3: Install ExecDiff from Terminal

Run this inside the terminal:

```bash
pip install execdiff
```

---

## Step 4: Start Tracing Before Using Your AI Copilot

Create a new Python file in your project: `trace_ai.py` with the code below

```python
import execdiff
import time

print("\nStarting AI action trace...\n")
execdiff.start_action_trace(workspace=".")

input("Tracing is ON. Use your AI copilot now.\n\nPress ENTER here once it's done...")

print("\nStopping trace...\n")
execdiff.stop_action_trace()

print("\nSummary of last AI action:\n")
print(execdiff.last_action_summary())
```

Now run this from the terminal:

```bash
python trace_ai.py
```

Tracing has now started and you’ll see:

```
Starting AI action trace...

Tracing is ON. Use your AI copilot now.
Press ENTER here once it's done...
```

Leave this terminal running.

---

## Step 5: Use Your AI Copilot Normally

Now continue development normally inside your IDE using any AI copilot.

For example, ask:

> “Create a new feature for loading hello world into a pandas data frame and displaying it. Install the required libraries”

Your copilot may now:

- generate new code
- install dependencies
- modify config files
- create or delete files

inside your project workspace.

You don’t need to change anything in your workflow.

Just let your AI copilot run whatever setup it needs internally.

---

## Step 6: Stop the Trace

Once it’s done, come back to terminal and press Enter

You’ll get:

```
Summary of last AI action:
Created:
- output.txt
- data.json
Modified:
- settings.py
Installed:
- requests==2.32.0
```

This includes:

- filesystem changes
- installed packages
- deleted files
- execution-time config updates

All changes made during runtime.

---

## Automatic Logs

Each AI-driven action is also stored inside:

```
.execdiff/logs/actions.jsonl
```

Now get a running history of what changed in your project after every AI action.

---

You can now continue using any AI copilot inside VS Code (or any IDE) normally while ExecDiff captures everything it changes behind the scenes.
