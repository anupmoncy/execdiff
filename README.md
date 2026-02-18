# ExecDiff

See what AI-generated code will change before running it.

---

## Problem

AI coding tools and agents today can:

- install dependencies  
- create files  
- modify configs  
- run migrations  
- delete project files  

All automatically.

When something breaks after execution, tools cannot answer:

> What exactly changed because of this action?

Git tracks source code changes —  
but it does **not** track execution side effects like:

- newly installed Python packages  
- runtime-created files  
- deleted files  
- modified configs  

So tools often fall back to:

> regenerate and try again

---

## Solution

ExecDiff allows tools to run AI-generated code and observe:

> what changed in the workspace because of that execution

It detects:

- files created  
- files modified  
- files deleted  
- Python packages installed  

inside a specific workspace  
during a specific execution window.

---

## Installation

```bash
pip install execdiff
```

---

## Example

Create a test script:

```python
import execdiff
import json
import os

os.makedirs("workspace", exist_ok=True)

diff = execdiff.run_traced(
    "touch workspace/test.txt",
    workspace="workspace"
)

print(json.dumps(diff, indent=2))
```

Run:

```bash
python test.py
```

---

## API Reference

### `start_action_trace(workspace=".")`

Start tracing a workspace for changes. Must be called before any operations.

```python
import execdiff

execdiff.start_action_trace(workspace="./my_workspace")
# ... your code that makes changes ...
```

### `stop_action_trace()`

Stop tracing and return a diff of all changes detected. Automatically logs to `.execdiff/logs/actions.jsonl`.

```python
diff = execdiff.stop_action_trace()
# Returns: {"files": {...}, "packages": {...}}
```

### `last_action_summary(workspace=".")`

Get a human-readable summary of the last action trace without parsing JSON.

```python
summary = execdiff.last_action_summary(workspace=".")
print(summary)
```

Output example:
```
Last AI Action:

Created:
- output.txt
- data.json

Installed:
- requests==2.32.0
```

### `snapshot_workspace_state(workspace)`

Take a full metadata snapshot of the workspace (files with mtime/size, installed packages).

```python
state = execdiff.snapshot_workspace_state(workspace=".")
# Returns: {"files": {...}, "packages": {...}}
```

---

## Output Format

### Diff Structure

```json
{
  "files": {
    "created": [{"path": "file.txt", "mtime": 123.45, "size": 1024}],
    "modified": [{"path": "config.yaml", "before_mtime": 123, "after_mtime": 124, "before_size": 512, "after_size": 1024}],
    "deleted": [{"path": "old_file.txt", "mtime": 123.45, "size": 256}]
  },
  "packages": {
    "installed": [{"name": "requests", "version": "2.32.0"}],
    "upgraded": [{"name": "django", "before_version": "3.2", "after_version": "4.0"}],
    "removed": [{"name": "deprecated_lib", "version": "1.0"}]
  }
}
```

### Log File

All action traces are automatically persisted to `.execdiff/logs/actions.jsonl`:

```json
{
  "timestamp": "2026-02-18T18:19:35.872838",
  "workspace": "/path/to/workspace",
  "diff": {...}
}
```

---

## Use Cases

ExecDiff can help AI coding tools:

- preview changes before applying generated code  
- detect unintended file or dependency changes  
- explain execution impact to users  
- debug failed automation  
- build undo / rollback systems  

---

## License

MIT

````
