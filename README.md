# Agentic-AI-system
hii

## Running the application

Prerequisites: Python 3.11+, recommended to use a virtual environment.

From the project root (Windows PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe run_server.py
```

To run the console/CLI app:

```powershell
.\venv\Scripts\python.exe main.py
```

Helper scripts are provided in the `scripts/` folder:

```powershell
.\scripts\start.ps1    # create venv (if missing), install deps, start API
.\scripts\run_main.ps1 # run the console app
```

If you prefer to run the API directly with uvicorn:

```powershell
.\venv\Scripts\python.exe -m uvicorn api:app --reload --port 8000
```
