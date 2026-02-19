import argparse
import execdiff

def main():
    parser = argparse.ArgumentParser(prog="execdiff", description="ExecDiff CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    trace_parser = subparsers.add_parser("trace", help="Trace workspace changes during AI actions")

    args = parser.parse_args()

    if args.command == "trace":
        print("Tracing is ON. Use your AI copilot now, hit enter once you are done with the work to see trace")
        execdiff.start_action_trace(workspace=".")
        input()
        execdiff.stop_action_trace()
        print(execdiff.last_action_summary())