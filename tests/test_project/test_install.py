import execdiff

print("execdiff imported from:", getattr(execdiff, "__file__", "<built-in>"))
print("Has start_trace():", hasattr(execdiff, "start_trace"))
print("Has run_traced():", hasattr(execdiff, "run_traced"))

# Minimal sanity check: call a no-side-effect function if available
try:
    summary = execdiff.last_action_summary()
    print("last_action_summary():", summary[:200] if isinstance(summary, str) else summary)
except Exception as e:
    print("last_action_summary() raised:", type(e).__name__, e)
