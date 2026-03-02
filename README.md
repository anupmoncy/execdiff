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

## Step 4: Start Tracing Using the CLI


## Live Progress & Interactive Review (New!)


ExecDiff now supports live progress updates and interactive review while tracing, with a visually enhanced, colored, and symbol-rich table:

```bash
execdiff trace
```


You will see a live-updating table of file changes as they happen, with colors and symbols:

```
┌──────────┬──────────┬──────────────────────┬──────────┬────────┬───────┐
│   Time   │  Change  │       Target         │ ΔLines   │  Risk  │ Score │
├──────────┼──────────┼──────────────────────┼──────────┼────────┼───────┤
│ 12:01:05 │✏️ MODIFY │    settings.py       │  +14/-3  │⚠️ MED  │  42   │
│ 12:01:10 │➕ CREATE │   newfile.py         │  +20/-0  │🛡️ LOW  │  20   │
│ 12:01:15 │➖ DELETE │   oldfile.py         │  +0/-10  │💣 HIGH │  10   │
```

Legend:
- ✏️ MODIFY: File modified
- ➕ CREATE: File created
- ➖ DELETE: File deleted
- 🛡️ LOW, ⚠️ MED, 💣 HIGH: Risk levels (color-coded)
- Colors: Green for added, red for removed, yellow for medium risk, etc.

**Features:**
- See file changes live while tracing
- Enriched metadata: lines/functions/imports/risk/score
- Interactively review any change: type `r <n>` (e.g. `r 2`) to see a unified diff for change #2
- Tracing continues while you review (non-blocking)

**Commands:**
- `r <n>` — Review change number n (shows before/after diff)
- `Ctrl+C` — Stop tracing and exit

All with zero external dependencies (pure Python stdlib).

---

When you are done, press `Ctrl+C` in the terminal. ExecDiff will stop tracing and exit cleanly.

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
