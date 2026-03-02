
import argparse
import execdiff
import os
import time
import threading
from execdiff.live_trace import TraceSession, ReviewHandler

def main():
    parser = argparse.ArgumentParser(prog="execdiff", description="ExecDiff CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    trace_parser = subparsers.add_parser("trace", help="Trace workspace changes during AI actions")

    args = parser.parse_args()

    if args.command == "trace":
        print("Tracing is ON. Live progress and review enabled. Press Ctrl+C to stop.")
        session = TraceSession(workspace=".")
        session.start()
        review = ReviewHandler(session)

        # Monitor for file changes in a background thread
        def trace_worker():
            # Take initial snapshot
            prev_snapshot = {}
            for root, dirs, files in os.walk(session.workspace):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    relpath = os.path.relpath(fpath, session.workspace)
                    try:
                        prev_snapshot[relpath] = os.path.getmtime(fpath)
                    except Exception:
                        pass
            while session.running:
                time.sleep(1)
                for root, dirs, files in os.walk(session.workspace):
                    for fname in files:
                        fpath = os.path.join(root, fname)
                        relpath = os.path.relpath(fpath, session.workspace)
                        try:
                            mtime = os.path.getmtime(fpath)
                        except Exception:
                            continue
                        if relpath not in prev_snapshot:
                            prev_snapshot[relpath] = mtime
                        elif mtime != prev_snapshot[relpath]:
                            # File modified
                            before_path = session.snapshot_before(relpath, fpath)
                            # Wait a moment to ensure after is written
                            time.sleep(0.1)
                            session.enrich_and_log_change(relpath, before_path, fpath)
                            prev_snapshot[relpath] = mtime

        trace_thread = threading.Thread(target=trace_worker, daemon=True)
        trace_thread.start()

        # Main thread: handle user input for review
        try:
            while True:
                cmd = input()
                if cmd.strip().startswith('r '):
                    try:
                        n = int(cmd.strip().split()[1])
                        review.review(n)
                    except Exception:
                        print('Usage: r <n>')
        except KeyboardInterrupt:
            print("\nStopping trace...")
            session.stop()
            trace_thread.join(timeout=1)
            print("Trace stopped.")