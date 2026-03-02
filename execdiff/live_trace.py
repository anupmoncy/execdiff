__all__ = [
    'TraceSession', 'ChangeEvent', 'ReviewHandler', 'LiveConsole'
]
"""
live_trace.py
Implements live progress update and review system for execdiff trace.
"""
import os
import time
import threading
import shutil
import difflib
import json
from datetime import datetime
from queue import Queue

class ChangeEvent:
    def __init__(self, time_str, event_type, target, lines, functions, imports, risk, intensity):
        self.time = time_str
        self.type = event_type
        self.target = target
        self.lines = lines
        self.functions = functions
        self.imports = imports
        self.risk = risk
        self.intensity = intensity
    def to_dict(self):
        return {
            "time": self.time,
            "type": self.type,
            "target": self.target,
            "lines": self.lines,
            "functions": self.functions,
            "imports": self.imports,
            "risk": self.risk,
            "intensity": self.intensity
        }

class TraceSession:
    def __init__(self, workspace="."):
        self.workspace = workspace
        self.snapshots_dir = os.path.join(".execdiff", "snapshots")
        self.live_dir = os.path.join(".execdiff", "live")
        self.progress_file = os.path.join(self.live_dir, "progress.jsonl")
        os.makedirs(self.snapshots_dir, exist_ok=True)
        os.makedirs(self.live_dir, exist_ok=True)
        self.event_queue = Queue()
        self.event_history = []
        self.lock = threading.Lock()
        self.running = False
    def start(self):
        self.running = True
        # Clear progress file at the start of each trace session
        with open(self.progress_file, 'w', encoding='utf-8'):
            pass
        # Start background thread for live console
        self.console = LiveConsole(self.progress_file, self.event_history, self.lock)
        self.console_thread = threading.Thread(target=self.console.run, daemon=True)
        self.console_thread.start()
    def stop(self):
        self.running = False
        self.console.stop()
    def enrich_and_log_change(self, relpath, before_path, after_path):
        # Ignore internal execdiff files
        if relpath.startswith('.execdiff/'):
            return None
        # Read before and after
        with open(before_path, 'r', encoding='utf-8', errors='ignore') as f:
            before_lines = f.readlines()
        with open(after_path, 'r', encoding='utf-8', errors='ignore') as f:
            after_lines = f.readlines()
        diff = list(difflib.unified_diff(before_lines, after_lines, lineterm=''))
        # Count lines added/removed
        lines_added = sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))
        lines_removed = sum(1 for l in diff if l.startswith('-') and not l.startswith('---'))
        # Count new functions/imports in after
        functions_added = sum(1 for l in after_lines if l.strip().startswith('def '))
        imports_added = sum(1 for l in after_lines if l.strip().startswith('import '))
        # File size delta
        size_before = os.path.getsize(before_path)
        size_after = os.path.getsize(after_path)
        risk = 'low'
        if '.env' in relpath or 'Dockerfile' in relpath:
            risk = 'high'
        elif 'settings.py' in relpath or 'requirements.txt' in relpath:
            risk = 'medium'
        # Intensity
        intensity = lines_added * 1 + functions_added * 3 + imports_added * 5
        # Event
        event = ChangeEvent(
            time_str=datetime.now().strftime('%H:%M:%S'),
            event_type='MODIFY',
            target=relpath,
            lines=f'+{lines_added}/-{lines_removed}',
            functions=f'+{functions_added}',
            imports=f'+{imports_added}',
            risk=risk,
            intensity=intensity
        )
        with self.lock:
            self.event_history.append(event)
        with open(self.progress_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event.to_dict()) + '\n')
        return event
    def snapshot_before(self, relpath, src_path):
        # Ignore internal execdiff files
        if relpath.startswith('.execdiff/'):
            return None
        dest = os.path.join(self.snapshots_dir, relpath + '.before')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src_path, dest)
        return dest
    def get_event_history(self):
        with self.lock:
            return list(self.event_history)

        class ChangeEvent:
            def __init__(self, time_str, event_type, target, lines, functions, imports, risk, intensity):
                self.time = time_str
                self.type = event_type
                self.target = target
                self.lines = lines
                self.functions = functions
                self.imports = imports
                self.risk = risk
                self.intensity = intensity
            def to_dict(self):
                return {
                    "time": self.time,
                    "type": self.type,
                    "target": self.target,
                    "lines": self.lines,
                    "functions": self.functions,
                    "imports": self.imports,
                    "risk": self.risk,
                    "intensity": self.intensity
                }

        class TraceSession:
            def __init__(self, workspace="."):
                self.workspace = workspace
                self.snapshots_dir = os.path.join(".execdiff", "snapshots")
                self.live_dir = os.path.join(".execdiff", "live")
                self.progress_file = os.path.join(self.live_dir, "progress.jsonl")
                os.makedirs(self.snapshots_dir, exist_ok=True)
                os.makedirs(self.live_dir, exist_ok=True)
                self.event_queue = Queue()
                self.event_history = []
                self.lock = threading.Lock()
                self.running = False
            def start(self):
                self.running = True
                # Clear progress file at the start of each trace session
                with open(self.progress_file, 'w', encoding='utf-8'):
                    pass
                # Start background thread for live console
                self.console = LiveConsole(self.progress_file, self.event_history, self.lock)
                self.console_thread = threading.Thread(target=self.console.run, daemon=True)
                self.console_thread.start()
            def stop(self):
                self.running = False
                self.console.stop()
            def enrich_and_log_change(self, relpath, before_path, after_path):
                # Ignore internal execdiff files
                if relpath.startswith('.execdiff/'):
                    return None
                # Read before and after
                with open(before_path, 'r', encoding='utf-8', errors='ignore') as f:
                    before_lines = f.readlines()
                with open(after_path, 'r', encoding='utf-8', errors='ignore') as f:
                    after_lines = f.readlines()
                diff = list(difflib.unified_diff(before_lines, after_lines, lineterm=''))
                # Count lines added/removed
                lines_added = sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))
                lines_removed = sum(1 for l in diff if l.startswith('-') and not l.startswith('---'))
                # Count new functions/imports in after
                functions_added = sum(1 for l in after_lines if l.strip().startswith('def '))
                imports_added = sum(1 for l in after_lines if l.strip().startswith('import '))
                # File size delta
                size_before = os.path.getsize(before_path)
                size_after = os.path.getsize(after_path)
                # Risk
                risk = 'low'
                if '.env' in relpath or 'Dockerfile' in relpath:
                    risk = 'high'
                elif 'settings.py' in relpath or 'requirements.txt' in relpath:
                    risk = 'medium'
                # Intensity
                intensity = lines_added * 1 + functions_added * 3 + imports_added * 5
                # Event
                event = ChangeEvent(
                    time_str=datetime.now().strftime('%H:%M:%S'),
                    event_type='MODIFY',
                    target=relpath,
                    lines=f'+{lines_added}/-{lines_removed}',
                    functions=f'+{functions_added}',
                    imports=f'+{imports_added}',
                    risk=risk,
                    intensity=intensity
                )
                with self.lock:
                    self.event_history.append(event)
                with open(self.progress_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(event.to_dict()) + '\n')
                return event
            def snapshot_before(self, relpath, src_path):
                # Ignore internal execdiff files
                if relpath.startswith('.execdiff/'):
                    return None
                dest = os.path.join(self.snapshots_dir, relpath + '.before')
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src_path, dest)
                return dest
            def get_event_history(self):
                with self.lock:
                    return list(self.event_history)

        class LiveConsole:
            def __init__(self, progress_file, event_history, lock):
                self.progress_file = progress_file
                self.event_history = event_history
                self.lock = lock
                self.running = True
            def stop(self):
                self.running = False
                if hasattr(self, 'header_printed') and self.header_printed:
                    print('\033[1m' + '└' + '─'*10 + '┴' + '─'*10 + '┴' + '─'*22 + '┘\033[0m')
                self.print_summary()
            def print_summary(self):
                # Print a summary of all changes (deduplicated, only file paths)
                with self.lock:
                    events = [e for e in self.event_history if not e.target.startswith('.execdiff/')]
                if not events:
                    print("No changes detected.")
                    return
                print("\nSummary of changes:")
                by_type = {'MODIFY': set(), 'CREATE': set(), 'DELETE': set()}
                for e in events:
                    by_type.get(e.type, set()).add(e.target)
                if by_type['CREATE']:
                    print("Created:")
                    for t in sorted(by_type['CREATE']):
                        print(f"- {t}")
                if by_type['MODIFY']:
                    print("Modified:")
                    for t in sorted(by_type['MODIFY']):
                        print(f"- {t}")
                if by_type['DELETE']:
                    print("Deleted:")
                    for t in sorted(by_type['DELETE']):
                        print(f"- {t}")
            def run(self):
                last_pos = 0
                self.header_printed = False
                header = (
                    '\033[1m'  # Bold
                    '┌' + '─'*10 + '┬' + '─'*10 + '┬' + '─'*22 + '┐\n'
                    '│' + f"{'Time':^10}" + '│' + f"{'Change':^10}" + '│' + f"{'Target':^22}" + '│\n'
                    '├' + '─'*10 + '┼' + '─'*10 + '┼' + '─'*22 + '┤\033[0m'
                )
                while self.running:
                    try:
                        with open(self.progress_file, 'r', encoding='utf-8') as f:
                            f.seek(last_pos)
                            while True:
                                line = f.readline()
                                if not line:
                                    break
                                event = json.loads(line)
                                # Skip internal execdiff files
                                if event['target'].startswith('.execdiff/'):
                                    continue
                                if not self.header_printed:
                                    print(header)
                                    self.header_printed = True
                                # Color and symbol logic
                                type_color = {'MODIFY': '\033[94m✏️ ', 'CREATE': '\033[92m➕', 'DELETE': '\033[91m➖'}.get(event['type'], '\033[0m')
                                # Print row with box drawing (no lines/risk/score)
                                print(
                                    f"│{event['time']:^10}│"
                                    f"{type_color}{event['type']:^8}\033[0m │"
                                    f"{event['target'][:20]:^22}│"
                                )
                            last_pos = f.tell()
                    except FileNotFoundError:
                        pass
                    time.sleep(0.5)


# --- ReviewHandler moved to top-level ---

class ReviewHandler:
    def __init__(self, session):
        self.session = session
    def review(self, n):
        events = self.session.get_event_history()
        if n < 1 or n > len(events):
            print('Invalid change number')
            return
        event = events[n-1]
        relpath = event.target
        before_path = os.path.join(self.session.snapshots_dir, relpath + '.before')
        after_path = os.path.join(self.session.workspace, relpath)
        try:
            with open(before_path, 'r', encoding='utf-8', errors='ignore') as f:
                before_lines = f.readlines()
            with open(after_path, 'r', encoding='utf-8', errors='ignore') as f:
                after_lines = f.readlines()
            diff = difflib.unified_diff(before_lines, after_lines, fromfile=relpath+'.before', tofile=relpath, lineterm='')
            print(''.join(diff))
        except Exception as e:
            print(f'Error during review: {e}')
