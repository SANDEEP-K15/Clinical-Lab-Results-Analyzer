"""Start the FastAPI server without watching venv (avoids OneDrive/reload loops)."""

from pathlib import Path

import uvicorn

BACKEND_DIR = Path(__file__).parent

# Only watch application source — NOT venv, tests, or site-packages
RELOAD_DIRS = [
    str(BACKEND_DIR / "api"),
    str(BACKEND_DIR / "agent"),
    str(BACKEND_DIR / "mcp"),
    str(BACKEND_DIR / "models"),
    str(BACKEND_DIR / "services"),
    str(BACKEND_DIR / "utils"),
]

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=RELOAD_DIRS,
    )
