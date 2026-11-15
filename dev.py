import subprocess
import sys
import os
import signal
import time

def main():
    print("=" * 60)
    print("  ⚡ Starting BuildUI (Backend FastAPI + Frontend Vite)")
    print("=" * 60)

    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")

    # Command 1: Backend FastAPI
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--reload", "--port", "8000"]
    
    # Command 2: Frontend Vite
    # On Windows, pnpm is often pnpm.cmd
    pnpm_bin = "pnpm.cmd" if os.name == "nt" else "pnpm"
    frontend_cmd = [pnpm_bin, "dev"]

    print(f"\n[1/2] Launching Backend API on http://localhost:8000 ...")
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=root_dir,
        stdout=None,
        stderr=None
    )

    print(f"[2/2] Launching Frontend Studio on http://localhost:5173 ...")
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir,
        stdout=None,
        stderr=None
    )

    print("\n" + "=" * 60)
    print("  🚀 Both services are running!")
    print("  • Frontend Studio: http://localhost:5173")
    print("  • Backend API:     http://localhost:8000")
    print("  • API Docs (Swagger): http://localhost:8000/docs")
    print("  Press Ctrl+C to stop both servers.")
    print("=" * 60 + "\n")

    def handle_sigint(signum, frame):
        print("\nShutting down servers...")
        try:
            frontend_proc.terminate()
            backend_proc.terminate()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        while True:
            # Check if any process terminated unexpectedly
            if backend_proc.poll() is not None:
                print(f"[!] Backend process exited with code {backend_proc.returncode}")
                frontend_proc.terminate()
                break
            if frontend_proc.poll() is not None:
                print(f"[!] Frontend process exited with code {frontend_proc.returncode}")
                backend_proc.terminate()
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        handle_sigint(None, None)

if __name__ == "__main__":
    main()
