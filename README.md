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

## Output

```json
{
  "files": {
    "created": [
      {
        "path": "workspace/test.txt",
        "mtime": 1700000000.0
      }
    ],
    "modified": [],
    "deleted": []
  },
  "packages": {
    "installed": []
  }
}
```

---

## Package Install Detection Example

```python
import execdiff
import json
import os

os.makedirs("workspace", exist_ok=True)

diff = execdiff.run_traced(
    "pip install requests",
    workspace="workspace"
)

print(json.dumps(diff, indent=2))
```

---

## Output

```json
{
  "files": {
    "created": [],
    "modified": [],
    "deleted": []
  },
  "packages": {
    "installed": [
      {
        "name": "requests",
        "version": "2.32.0"
      }
    ]
  }
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
