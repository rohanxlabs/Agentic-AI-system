#!/usr/bin/env python3
"""
Unified launcher for Agentic AI System.
Starts both backend API and frontend dev server with a single command.
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_banner():
    """Print startup banner."""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BOLD}{GREEN}  Agentic AI System - Unified Launcher{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")

def check_env():
    """Check if .env file exists and has GROQ_API_KEY."""
    env_path = Path(".env")
    if not env_path.exists():
        print(f"{RED}❌ Error: .env file not found{RESET}")
        print(f"{YELLOW}Run: cp .env.example .env{RESET}")
        print(f"{YELLOW}Then edit .env and set your GROQ_API_KEY{RESET}")
        return False
    
    # Check if GROQ_API_KEY is set
    with open(env_path) as f:
        content = f.read()
        if "GROQ_API_KEY=" not in content or "GROQ_API_KEY=\n" in content:
            print(f"{YELLOW}⚠️  Warning: GROQ_API_KEY appears to be empty in .env{RESET}")
            print(f"{YELLOW}The system will start but LLM calls will fail.{RESET}")
            print(f"{YELLOW}Get a free key at: https://console.groq.com{RESET}\n")
    
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import groq
        import sentence_transformers
        print(f"{GREEN}✓{RESET} Python dependencies installed")
        return True
    except ImportError as e:
        print(f"{RED}❌ Missing Python dependency: {e.name}{RESET}")
        print(f"{YELLOW}Run: pip install -r requirements.txt{RESET}")
        return False

def check_node_modules():
    """Check if frontend node_modules exist."""
    node_modules = Path("frontend/node_modules")
    if not node_modules.exists():
        print(f"{YELLOW}⚠️  Frontend dependencies not installed{RESET}")
        print(f"{YELLOW}Installing... (this may take a minute){RESET}")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd="frontend",
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            print(f"{GREEN}✓{RESET} Frontend dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print(f"{RED}❌ Failed to install frontend dependencies{RESET}")
            print(f"{YELLOW}Run manually: cd frontend && npm install{RESET}")
            return False
    else:
        print(f"{GREEN}✓{RESET} Frontend dependencies installed")
        return True

def start_backend():
    """Start the FastAPI backend server."""
    print(f"\n{BLUE}Starting backend API...{RESET}")
    return subprocess.Popen(
        [sys.executable, "run_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

def start_frontend():
    """Start the Next.js frontend dev server."""
    print(f"{BLUE}Starting frontend...{RESET}\n")
    return subprocess.Popen(
        ["npm", "run", "dev"],
        cwd="frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

def monitor_processes(backend_proc, frontend_proc):
    """Monitor both processes and print their output."""
    print(f"{GREEN}{'=' * 70}{RESET}")
    print(f"{BOLD}System is starting...{RESET}")
    print(f"{GREEN}{'=' * 70}{RESET}\n")
    
    backend_ready = False
    frontend_ready = False
    
    try:
        while True:
            # Check backend output
            if backend_proc.poll() is None and backend_proc.stdout:
                line = backend_proc.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        print(f"{BLUE}[API]{RESET} {line}")
                        if "Uvicorn running on" in line and not backend_ready:
                            backend_ready = True
                            print(f"\n{GREEN}✓ Backend API ready at http://localhost:8000{RESET}")
                            print(f"{GREEN}  - API docs: http://localhost:8000/docs{RESET}\n")
            
            # Check frontend output
            if frontend_proc.poll() is None and frontend_proc.stdout:
                line = frontend_proc.stdout.readline()
                if line:
                    line = line.strip()
                    if line and not line.startswith("  "):  # Skip framework internal logs
                        print(f"{YELLOW}[UI]{RESET}  {line}")
                        if "Local:" in line and not frontend_ready:
                            frontend_ready = True
                            print(f"\n{GREEN}✓ Frontend ready at http://localhost:3000{RESET}")
                            print(f"{GREEN}{'=' * 70}{RESET}")
                            print(f"{BOLD}{GREEN}System ready! Open http://localhost:3000 in your browser{RESET}")
                            print(f"{GREEN}{'=' * 70}{RESET}\n")
                            print(f"{YELLOW}Press Ctrl+C to stop both servers{RESET}\n")
            
            # Check if processes died
            if backend_proc.poll() is not None:
                print(f"{RED}❌ Backend process exited{RESET}")
                break
            if frontend_proc.poll() is not None:
                print(f"{RED}❌ Frontend process exited{RESET}")
                break
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Shutting down...{RESET}")
    finally:
        # Clean shutdown
        backend_proc.terminate()
        frontend_proc.terminate()
        try:
            backend_proc.wait(timeout=5)
            frontend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_proc.kill()
            frontend_proc.kill()
        print(f"{GREEN}✓ Shutdown complete{RESET}\n")

def main():
    """Main entry point."""
    print_banner()
    
    # Pre-flight checks
    if not check_env():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_node_modules():
        sys.exit(1)
    
    # Start both servers
    backend_proc = start_backend()
    time.sleep(2)  # Give backend a head start
    frontend_proc = start_frontend()
    
    # Monitor until Ctrl+C
    monitor_processes(backend_proc, frontend_proc)

if __name__ == "__main__":
    main()
