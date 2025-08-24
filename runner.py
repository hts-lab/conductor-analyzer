# runner.py
import os, sys, json, subprocess
from pathlib import Path

MOUNT       = Path(os.getenv("MOUNT_PATH", "/mnt/gcs")).resolve()
REQUEST_ID  = os.getenv("REQUEST_ID", "")
BUCKET      = os.environ["BUCKET"]
REQ         = os.environ["REQUEST_ROOT"].strip("/")              # e.g. requests/REQ-123
SCRIPT_REL  = os.environ["SCRIPT_REL"].lstrip("/")               # e.g. analysis/plate_heatmap.py

# Prefer script under the mounted request, fallback to image path
script_gcs = (MOUNT / REQ / SCRIPT_REL).resolve()
script_img = (Path("/app") / SCRIPT_REL).resolve()
script = script_gcs if script_gcs.exists() else script_img if script_img.exists() else None
if not script:
    raise FileNotFoundError(f"Script not found. Tried:\n  {script_gcs}\n  {script_img}")

# Resolve output rel paths (override via env if needed)
rels = {
    "results":   os.getenv("RESULTS_REL",   "results"),
    "figures":   os.getenv("FIGURES_REL",   "results/figures"),
    "tables":    os.getenv("TABLES_REL",    "results/tables"),
    "artifacts": os.getenv("ARTIFACTS_REL", "results/artifacts"),
}
# Ensure dirs exist
base = MOUNT / REQ
for rel in rels.values():
    (base / rel).resolve().mkdir(parents=True, exist_ok=True)

# Build CONDUCTOR_CONTEXT once, from the minimal envs
paths_full = {k: f"{REQ}/{v.strip('/')}" for k, v in rels.items()}
ctx = {
    "bucket": BUCKET,
    "mount_path": str(MOUNT),      # '/mnt/gcs' in Cloud Run; can be './_sandbox' locally
    "request_root": REQ,
    "paths": paths_full,
}
# Optional: include inputs if provided as JSON
inputs_json = os.getenv("INPUTS_JSON")
if inputs_json:
    try:
        ctx["inputs"] = json.loads(inputs_json)
    except Exception:
        print("[runner] WARNING: Could not parse INPUTS_JSON; ignoring.", flush=True)

# Export for scripts that do `from conductor_sdk import ctx`
os.environ["CONDUCTOR_CONTEXT"] = json.dumps(ctx, separators=(",", ":"))

print("[runner] --------------------------------------------------")
if REQUEST_ID: print(f"[runner] REQUEST_ID     : {REQUEST_ID}")
print(f"[runner] BUCKET          : {BUCKET}")
print(f"[runner] REQUEST_ROOT    : {REQ}")
print(f"[runner] SCRIPT_REL      : {SCRIPT_REL}")
print(f"[runner] Executing       : {script}")
print("[runner] --------------------------------------------------", flush=True)

# Run the user script from its directory
proc = subprocess.run([sys.executable, str(script)], cwd=str(script.parent), text=True)
proc.check_returncode()
