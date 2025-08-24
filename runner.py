# runner.py
import os, subprocess, sys
from pathlib import Path

MOUNT = os.environ.get("MOUNT_PATH", "/mnt/gcs")
SCRIPT_REL = os.environ.get("SCRIPT_REL")  # e.g., requests/REQ-1234/analysis/plate_heatmap.py
if not SCRIPT_REL:
    raise RuntimeError("Missing SCRIPT_REL env var")

script = Path(MOUNT) / SCRIPT_REL
if not script.exists():
    raise FileNotFoundError(f"Script not found at: {script}")

# Execute the user script; it will `from conductor_sdk import ctx`
# and read CONDUCTOR_CONTEXT from env.
print(f"[runner] Executing: {script}")
proc = subprocess.run([sys.executable, str(script)], cwd=str(script.parent), text=True)
proc.check_returncode()
