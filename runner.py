# runner.py
import os, sys, subprocess
from pathlib import Path

MOUNT       = Path(os.getenv("MOUNT_PATH", "/mnt/gcs")).resolve()
REQUEST_ID  = os.getenv("REQUEST_ID", "")
REQ         = os.environ["REQUEST_ROOT"].strip("/")              # e.g. requests/REQ-123
SCRIPT_REL  = os.environ["SCRIPT_REL"].lstrip("/")               # e.g. analysis/plate_heatmap.py

if not SCRIPT_REL:
    raise RuntimeError("Missing SCRIPT_REL env var")

# Prefer script under the mounted request, fallback to image
script_gcs = (MOUNT / REQ / SCRIPT_REL).resolve()
script_img = (Path("/app") / SCRIPT_REL).resolve()
script = script_gcs if script_gcs.exists() else script_img if script_img.exists() else None
if not script:
    raise FileNotFoundError(f"Script not found. Tried:\n  {script_gcs}\n  {script_img}")

# Ensure output folders exist (based on *_REL envs)
base = MOUNT / REQ
for rel in [
    os.getenv("RESULTS_REL", "results"),
    os.getenv("FIGURES_REL", "results/figures"),
    os.getenv("TABLES_REL", "results/tables"),
    os.getenv("ARTIFACTS_REL", "results/artifacts"),
]:
    (base / rel).resolve().mkdir(parents=True, exist_ok=True)

print("[runner] --------------------------------------------------")
if REQUEST_ID:
    print(f"[runner] REQUEST_ID     : {REQUEST_ID}")
print(f"[runner] BUCKET          : {os.getenv('BUCKET')}")
print(f"[runner] REQUEST_ROOT    : {REQ}")
print(f"[runner] SCRIPT_REL      : {SCRIPT_REL}")
print(f"[runner] Executing       : {script}")
print("[runner] --------------------------------------------------", flush=True)

# Stream output to logs; inherit env by default
proc = subprocess.run([sys.executable, str(script)], cwd=str(script.parent), text=True)
proc.check_returncode()
