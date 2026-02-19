import argparse
import execdiff

def trace_command():
    execdiff.start_action_trace(workspace=".")
    print("Tracing is ON. Use your AI copilot now.\n(Tracing is ON)")
    input()
    execdiff.stop_action_trace()
    print(execdiff.last_action_summary())

def main():
    parser = argparse.ArgumentParser(prog="execdiff", description="ExecDiff CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    trace_parser = subparsers.add_parser("trace", help="Trace workspace changes during AI actions")

    args = parser.parse_args()

    if args.command == "trace":
        trace_command()

if __name__ == "__main__":
    main()
