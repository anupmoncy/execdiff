"""Minimal passive execution tracing library for file system snapshots."""

import os
import subprocess
import time


# Module-level variables to store the initial snapshot, workspace, package snapshot, and execution window
_initial_snapshot = None
_workspace = "."
_initial_packages = None
_execution_start_time = None
_execution_end_time = None


def start_trace(workspace="."):
    """
    Snapshot all files in the specified workspace directory recursively.
    Stores the snapshot in a module-level variable for later comparison.
    
    Args:
        workspace (str): The workspace directory to trace. Defaults to ".".
    """
    global _initial_snapshot, _workspace, _initial_packages, _execution_start_time
    _workspace = workspace
    _initial_snapshot = _take_snapshot()
    _initial_packages = _snapshot_packages()
    _execution_start_time = time.time()


def stop_trace():
    """
    Take a new snapshot and compare with the previous one.
    
    Returns:
        dict: A dictionary containing detailed information about created, modified, and deleted files:
            {
                "files": {
                    "created": [{"path": <file_path>, "mtime": <modified_time>}, ...],
                    "modified": [{"path": <file_path>, "before_mtime": <mtime>, "after_mtime": <mtime>}, ...],
                    "deleted": [{"path": <file_path>, "before_mtime": <mtime>}, ...]
                }
            }
    """
    global _execution_end_time
    if _initial_snapshot is None or _initial_packages is None or _execution_start_time is None:
        raise RuntimeError("start_trace() must be called before stop_trace()")

    _execution_end_time = time.time()
    current_snapshot = _take_snapshot()
    current_packages = _snapshot_packages()

    # Only include files whose mtime falls within the execution window
    def in_window(mtime):
        return _execution_start_time <= mtime <= _execution_end_time

    # Find newly created files
    created_files = []
    for file_path in sorted(set(current_snapshot.keys()) - set(_initial_snapshot.keys())):
        mtime = current_snapshot[file_path]
        if in_window(mtime):
            created_files.append({
                "path": file_path,
                "mtime": mtime
            })

    # Find modified files (files that existed before but have different mtime)
    modified_files = []
    for file_path in sorted(_initial_snapshot.keys()):
        if file_path in current_snapshot:
            before_mtime = _initial_snapshot[file_path]
            after_mtime = current_snapshot[file_path]
            if after_mtime != before_mtime and in_window(after_mtime):
                modified_files.append({
                    "path": file_path,
                    "before_mtime": before_mtime,
                    "after_mtime": after_mtime
                })

    # Find deleted files (files that existed before but don't exist now)
    deleted_files = []
    for file_path in sorted(set(_initial_snapshot.keys()) - set(current_snapshot.keys())):
        before_mtime = _initial_snapshot[file_path]
        if in_window(before_mtime):
            deleted_files.append({
                "path": file_path,
                "before_mtime": before_mtime
            })

    # Find newly installed packages using pip freeze
    installed_packages = []
    new_pkgs = current_packages - _initial_packages
    for pkg in sorted(new_pkgs):
        if "==" in pkg:
            name, version = pkg.split("==", 1)
            installed_packages.append({"name": name, "version": version})

    return {
        "files": {
            "created": created_files,
            "modified": modified_files,
            "deleted": deleted_files
        },
        "packages": {
            "installed": installed_packages
        }
    }

def run_traced(command, workspace="."):
    """
    Trace the effects of running a shell command in a subprocess.
    
    Args:
        command (list or str): The command to run (as for subprocess.run)
        workspace (str): The workspace directory to trace. Defaults to ".".
    
    Returns:
        dict: The diff as returned by stop_trace().
    """
    start_trace(workspace)
    subprocess.run(command, shell=isinstance(command, str))
    return stop_trace()


def _snapshot_packages():
    """
    Take a snapshot of installed Python packages using pip freeze.
    Returns:
        set: Set of 'package==version' strings.
    """
    try:
        result = subprocess.run(["python3", "-m", "pip", "freeze"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split("\n")
        return set(line for line in lines if line and not line.startswith("-") and "==" in line)
    except Exception:
        return set()


def _take_snapshot():
    """
    Take a snapshot of all files in the workspace directory recursively.
    
    Returns:
        dict: A dictionary mapping relative file paths to their last modified time.
    """
    file_dict = {}
    
    for root, dirs, files in os.walk(_workspace):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, _workspace)
            try:
                mtime = os.path.getmtime(file_path)
                file_dict[relative_path] = mtime
            except (OSError, IOError):
                # Skip files that can't be accessed
                pass
    
    return file_dict
