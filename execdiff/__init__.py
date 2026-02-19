__version__ = "0.0.9"
import sysconfig
import re
import json
from datetime import datetime

# --- Full Workspace Metadata Snapshot and Action Trace ---
_action_trace_before = None

def snapshot_workspace_state(workspace):
    """
    Take a full snapshot of the workspace state: files (mtime, size) and installed packages (name, version).
    Returns:
        dict: {"files": {relpath: {"mtime": float, "size": int}}, "packages": {name: {"version": str}}}
    """
    # File snapshot
    files = {}
    for root, dirs, filelist in os.walk(workspace):
        for fname in filelist:
            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, workspace)
            try:
                files[relpath] = {
                    "mtime": os.path.getmtime(fpath),
                    "size": os.path.getsize(fpath)
                }
            except (OSError, IOError):
                pass

    # Package snapshot
    packages = {}
    site_packages = sysconfig.get_paths()["purelib"]
    dist_info_re = re.compile(r"^(?P<name>.+?)-(?P<version>[^-]+)\.dist-info$")
    try:
        for entry in os.listdir(site_packages):
            m = dist_info_re.match(entry)
            if m:
                name = m.group("name").replace('_', '-')
                version = m.group("version")
                packages[name.lower()] = {"version": version}
    except Exception:
        pass

    return {"files": files, "packages": packages}


def start_action_trace(workspace="."):
    """
    Take and store a full workspace metadata snapshot for later diffing.
    """
    global _action_trace_before, _workspace
    _workspace = workspace
    _action_trace_before = snapshot_workspace_state(workspace)


def stop_action_trace():
    """
    Take a new snapshot and compute diff (files: created/modified/deleted, packages: installed/removed/upgraded).
    Returns:
        dict: {"files": {...}, "packages": {...}}
    """
    global _action_trace_before, _workspace
    if _action_trace_before is None:
        raise RuntimeError("start_action_trace() must be called before stop_action_trace()")
    after = snapshot_workspace_state(_workspace)
    before = _action_trace_before

    # File diffs
    before_files = before["files"]
    after_files = after["files"]
    created = []
    modified = []
    deleted = []
    for f in after_files:
        if f not in before_files:
            created.append({"path": f, **after_files[f]})
        else:
            b, a = before_files[f], after_files[f]
            if b["mtime"] != a["mtime"] or b["size"] != a["size"]:
                modified.append({"path": f, "before_mtime": b["mtime"], "after_mtime": a["mtime"], "before_size": b["size"], "after_size": a["size"]})
    for f in before_files:
        if f not in after_files:
            deleted.append({"path": f, **before_files[f]})

    # Package diffs
    before_pkgs = before["packages"]
    after_pkgs = after["packages"]
    installed = []
    removed = []
    upgraded = []
    for name in after_pkgs:
        if name not in before_pkgs:
            installed.append({"name": name, "version": after_pkgs[name]["version"]})
        else:
            if before_pkgs[name]["version"] != after_pkgs[name]["version"]:
                upgraded.append({"name": name, "before_version": before_pkgs[name]["version"], "after_version": after_pkgs[name]["version"]})
    for name in before_pkgs:
        if name not in after_pkgs:
            removed.append({"name": name, "version": before_pkgs[name]["version"]})

    diff = {
        "files": {
            "created": created,
            "modified": modified,
            "deleted": deleted
        },
        "packages": {
            "installed": installed,
            "removed": removed,
            "upgraded": upgraded
        }
    }

    _persist_action_log(diff)
    return diff


def _persist_action_log(diff):
    """
    Persist the action trace diff to global logs directory.
    Uses EXECDIFF_LOG_DIR env var, or defaults to ~/.execdiff/logs/
    """
    # Get log directory from env or use home directory
    log_base = os.environ.get('EXECDIFF_LOG_DIR') or os.path.expanduser('~/.execdiff/logs')
    log_file = os.path.join(log_base, "actions.jsonl")

    try:
        os.makedirs(log_base, exist_ok=True)
    except Exception:
        return

    try:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "workspace": os.path.abspath(_workspace),
            "diff": diff
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass
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


def last_action_summary(workspace="."):
    """
    Read the latest action trace from global logs and return a human-readable summary.
    Uses EXECDIFF_LOG_DIR env var, or defaults to ~/.execdiff/logs/
    Returns:
        str: Human-readable summary of the last AI action, or a message if no log exists.
    """
    log_base = os.environ.get('EXECDIFF_LOG_DIR') or os.path.expanduser('~/.execdiff/logs')
    log_file = os.path.join(log_base, "actions.jsonl")
    
    if not os.path.exists(log_file):
        return "No action history found."
    
    try:
        # Read the last line
        with open(log_file, "r") as f:
            lines = f.readlines()
            if not lines:
                return "No action history found."
            last_line = lines[-1].strip()
        
        entry = json.loads(last_line)
        diff = entry.get("diff", {})
        files = diff.get("files", {})
        packages = diff.get("packages", {})
        
        # Build summary
        summary_lines = ["Last AI Action:\n"]
        
        # Packages
        pkg_installed = packages.get("installed", [])
        if pkg_installed:
            summary_lines.append("Installed:")
            for pkg in pkg_installed:
                summary_lines.append(f"- {pkg['name']}=={pkg['version']}")
        
        pkg_upgraded = packages.get("upgraded", [])
        if pkg_upgraded:
            summary_lines.append("Upgraded:")
            for pkg in pkg_upgraded:
                summary_lines.append(f"- {pkg['name']}: {pkg['before_version']} → {pkg['after_version']}")
        
        pkg_removed = packages.get("removed", [])
        if pkg_removed:
            summary_lines.append("Removed:")
            for pkg in pkg_removed:
                summary_lines.append(f"- {pkg['name']}")
        
        # Files
        file_modified = files.get("modified", [])
        if file_modified:
            summary_lines.append("Modified:")
            for f in file_modified:
                summary_lines.append(f"- {f['path']}")
        
        file_created = files.get("created", [])
        if file_created:
            summary_lines.append("Created:")
            for f in file_created:
                summary_lines.append(f"- {f['path']}")
        
        file_deleted = files.get("deleted", [])
        if file_deleted:
            summary_lines.append("Deleted:")
            for f in file_deleted:
                summary_lines.append(f"- {f['path']}")
        
        return "\n".join(summary_lines) if len(summary_lines) > 1 else "No changes detected."
    except Exception:
        return "Error reading action history."
