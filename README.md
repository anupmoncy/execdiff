# execdiff
Track what changes when AI-generated code runs

## Features
- Trace file system changes (created, modified, deleted files)
- Detect newly installed Python packages
- Track changes only within a specified workspace directory
- Execution window: only changes made during the traced execution are reported
- Simple API, no classes

## API Usage

### Basic Tracing
```python
import execdiff

execdiff.start_trace(workspace=".")
# ... your code that makes changes ...
diff = execdiff.stop_trace()
print(diff)
```

### Trace a Subprocess Command
```python
import execdiff
import json

diff = execdiff.run_traced(["touch", "example.txt"])
print(json.dumps(diff, indent=2))
```

### Diff Output Structure
The result is a dictionary with:
- `files`: created, modified, and deleted files (with mtimes, only those changed during execution)
- `packages`: newly installed Python packages (name and version)

Example:
```json
{
  "files": {
    "created": [ {"path": "example.txt", "mtime": 1234567890.0} ],
    "modified": [],
    "deleted": []
  },
  "packages": {
    "installed": [ {"name": "requests", "version": "2.32.0"} ]
  }
}
```

## Installation
This package is self-contained and requires only Python 3. No external dependencies are needed for core tracing features. For package detection, ensure `pip` is available in your environment.

Clone the repository and use the code directly, or copy `execdiff/` into your project.

## Running the Test
To verify the MVP end-to-end:

```bash
python3 test.py
```

You should see output like:

```
{
  "files": {
    "created": [
      {"path": "test_workspace/ai_created.txt", "mtime": ...}
    ],
    "modified": [],
    "deleted": []
  },
  "packages": {
    "installed": []
  }
}
```

## Contributing
- Please open issues or pull requests for bugs, ideas, or improvements.
- Keep the implementation simple and function-based (no classes).

## License
MIT
