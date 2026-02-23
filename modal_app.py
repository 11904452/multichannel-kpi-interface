"""
Modal deployment script for the Email KPI Dashboard (Streamlit).

Usage:
  # Ephemeral serve (watches for file changes):
  modal serve modal_app.py

  # Production deploy (permanent URL):
  modal deploy modal_app.py
"""

import shlex
import subprocess
from pathlib import Path
from config import APP_NAME, SECRET_NAME, MODAL_ENV, MIN_CONTAINERS, MAX_INPUTS, PORT
from dotenv import load_dotenv
import modal

# ---------------------------------------------------------------------------
# Image: install all Python dependencies from requirements.txt
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(__file__).parent
load_dotenv(PROJECT_DIR / ".env")

# ── Validate prod requirements ────────────────────────────────────────────────
if MODAL_ENV == "prod" and not SECRET_NAME:
    raise EnvironmentError(
        "MODAL_SECRET_NAME must be set in .env when MODAL_ENV=prod.\n"
        "Create a secret in the Modal dashboard first, then set its name here."
    )

# ── Choose secret source ──────────────────────────────────────────────────────
if MODAL_ENV == "prod":
    secrets = [modal.Secret.from_name(SECRET_NAME)]
else:
    # Dev: inject secrets from the local .env file
    secrets = [modal.Secret.from_dotenv(path=str(PROJECT_DIR))]

# ── Container image ───────────────────────────────────────────────────────────
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install_from_requirements(str(PROJECT_DIR / "requirements.txt"))
    # Mount the entire project into /root/dashboard inside the container
    .add_local_dir(
        PROJECT_DIR,
        remote_path="/root/dashboard",
        # Don't ship the virtual-env, cache, or git history into the image
        ignore=[
            ".git",
            "__pycache__",
            "**/__pycache__",
            "*.pyc",
            "venv",
            ".venv",
            "node_modules",
        ],
    )
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = modal.App(name=APP_NAME, image=image)

# ---------------------------------------------------------------------------
# Serve function
# ---------------------------------------------------------------------------

@app.function(
    # Load secrets from the local .env file (used during `modal serve`).
    # For production deploys, swap this for:
    #   secrets=[modal.Secret.from_name("")]
    # after creating the secret in the Modal dashboard.
    secrets=secrets,
    # Keep 1 container warm so cold-starts don't interrupt users.
    min_containers=MIN_CONTAINERS,
)
@modal.concurrent(max_inputs=MAX_INPUTS)
@modal.web_server(PORT)
def run():
    """Launch the Streamlit server inside the Modal container."""
    target = shlex.quote("/root/dashboard/app.py")
    cmd = (
        f"streamlit run {target} "
        f"--server.port {PORT} "
        "--server.address 0.0.0.0 "
        "--server.headless true "
        "--server.enableCORS false "
        "--server.enableXsrfProtection false "
        "--server.fileWatcherType none"
    )
    subprocess.Popen(cmd, shell=True)
