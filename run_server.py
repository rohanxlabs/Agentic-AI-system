"""Run the FastAPI app using uvicorn.

Usage:
    python run_server.py
    or set PORT env var to change the port.
"""
import os
import sys

if __name__ == "__main__":
    # Ensure project root is on sys.path
    sys.path.insert(0, os.path.dirname(__file__))
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    # Use the `application` alias in `api.py` for compatibility with some hosts
    uvicorn.run("api:application", host="0.0.0.0", port=port, reload=True)
