"""
run_app.py

Single-command launcher for local development: starts the FastAPI backend
and the Vite frontend together, streams both logs to this terminal with
[backend]/[frontend] prefixes, and shuts both down cleanly on Ctrl+C.

Usage (from the project root - the folder containing backend/ and frontend/):
    python run_app.py

Configuration: edit BACKEND_PORT below if your machine needs a specific port
(see README Troubleshooting - e.g. Quick Heal's IDS blocking certain ports).
This script does NOT create the venv or run `pip install` / `npm install`
for you - run those once yourself first (see README section 6 and 7), same
as always. This script only starts the two already-installed processes.
"""
from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import threading

BACKEND_PORT = 8000  # change this if you need a different port on your machine

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

IS_WINDOWS = sys.platform == "win32"


def find_backend_python() -> str:
    """Prefers the backend's venv python if it exists, else falls back to
    whatever `python` is on PATH (with a warning)."""
    if IS_WINDOWS:
        venv_python = os.path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(BACKEND_DIR, ".venv", "bin", "python")

    if os.path.exists(venv_python):
        return venv_python

    print("[run_app] WARNING: backend/.venv not found - falling back to system 'python'.")
    print("[run_app] Run the backend setup steps in README section 6 first if this fails.")
    return "python"


def find_npm() -> str:
    npm_path = shutil.which("npm")
    if npm_path:
        return npm_path
    # Windows npm is usually npm.cmd; shutil.which above should already find
    # it, but this is a fallback in case PATH resolution is unusual.
    return "npm.cmd" if IS_WINDOWS else "npm"


def stream_output(process: subprocess.Popen, prefix: str):
    for line in iter(process.stdout.readline, b""):
        try:
            text = line.decode("utf-8", errors="replace").rstrip()
        except Exception:
            text = str(line)
        print(f"[{prefix}] {text}")


def main():
    if not os.path.isdir(BACKEND_DIR) or not os.path.isdir(FRONTEND_DIR):
        print("[run_app] ERROR: run this script from the project root "
              "(the folder containing both backend/ and frontend/).")
        sys.exit(1)

    backend_python = find_backend_python()
    npm_cmd = find_npm()

    print(f"[run_app] Starting backend on port {BACKEND_PORT} ...")
    backend_proc = subprocess.Popen(
        [backend_python, "-m", "uvicorn", "app.main:app", "--reload", "--port", str(BACKEND_PORT)],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    print("[run_app] Starting frontend (npm run dev) ...")
    frontend_env = os.environ.copy()
    frontend_env["VITE_API_BASE_URL"] = f"http://localhost:{BACKEND_PORT}"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=frontend_env,
        shell=IS_WINDOWS,  # npm on Windows is a .cmd shim; shell=True resolves it reliably
    )

    threads = [
        threading.Thread(target=stream_output, args=(backend_proc, "backend"), daemon=True),
        threading.Thread(target=stream_output, args=(frontend_proc, "frontend"), daemon=True),
    ]
    for t in threads:
        t.start()

    print("[run_app] Both processes started. Press Ctrl+C to stop both.\n")

    def shutdown(*_args):
        print("\n[run_app] Stopping backend and frontend ...")
        for proc in (backend_proc, frontend_proc):
            if proc.poll() is None:
                proc.terminate()
        for proc in (backend_proc, frontend_proc):
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("[run_app] Stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if not IS_WINDOWS:
        signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            backend_exit = backend_proc.poll()
            frontend_exit = frontend_proc.poll()
            if backend_exit is not None:
                print(f"[run_app] Backend exited unexpectedly (code {backend_exit}). Stopping frontend too.")
                shutdown()
            if frontend_exit is not None:
                print(f"[run_app] Frontend exited unexpectedly (code {frontend_exit}). Stopping backend too.")
                shutdown()
            for t in threads:
                t.join(timeout=1)
                if not t.is_alive():
                    continue
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
