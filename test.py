import execdiff
import os
import json

execdiff.start_trace()

# Create the workspace directory
os.makedirs("test_workspace", exist_ok=True)

diff = execdiff.run_traced(["touch", "test_workspace/ai_created.txt"])
print(json.dumps(diff, indent=2))
