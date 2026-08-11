# Agentic AI System

**A goal-driven autonomous agent system featuring multi-step planning, tool use, reasoning, and iterative refinement.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-122%20passing-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What Makes This Agentic?

This is not a chatbot. This is an **autonomous agent system** that:

1. **Plans** — breaks down goals into executable steps
2. **Acts** — executes steps using tools (calculator, web search)
3. **Observes** — processes tool results and evaluates progress
4. **Reasons** — critiques outputs and refines the approach
5. **Iterates** — repeats until the goal is achieved or limits are reached

**Example execution flow:**

```
User: "Research the current price of Bitcoin and calculate 5% of it"

Agent Plan:
  1. Search web for current Bitcoin price
  2. Extract price from results
  3. Calculate 5% using calculator tool

Agent Execution:
  ▶ Step 1: Execute web search → Tool: web_search("Bitcoin price") → $43,250
  ▶ Step 2: Extract value → $43,250
  ▶ Step 3: Calculate → Tool: calculator("43250 * 0.05") → 2162.5
  
Agent Output: "5% of the current Bitcoin price ($43,250) is $2,162.50"
```

The system **autonomously selects and invokes tools**, processes their output, and continues until the goal is satisfied.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          User / API                         │
└────────────────────────┬────────────────────────────────────┘
                         ↓
          ┌──────────────────────────────┐
          │      Manager Agent           │  ← Orchestrates the loop
          │  (Plan → Execute → Critique) │
          └──────────────┬───────────────┘
                         ↓
         ┌───────────────┴────────────────┐
         │                                │
    ┌────▼─────┐    ┌────────┐    ┌──────▼────┐
    │ Planner  │    │Executor│    │  Critic   │
    │  Agent   │    │ Agent  │    │   Agent   │
    └────┬─────┘    └───┬────┘    └─────┬─────┘
         │              │               │
         └──────┬───────┴───────┬───────┘
                │               │
                ↓               ↓
         ┌────────────┐   ┌───────────┐
         │    LLM     │   │   Tools   │
         │  (Groq)    │   │ Registry  │
         └────────────┘   └─────┬─────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              ┌─────▼──────┐        ┌──────▼────────┐
              │ Calculator │        │  Web Search   │
              │  (AST-safe)│        │ (DuckDuckGo)  │
              └────────────┘        └───────────────┘
```

### Agent Roles

| Agent | Responsibility |
|-------|----------------|
| **Manager** | Orchestrates the plan → execute → critique → refine loop. Decides when to continue and when to stop. |
| **Planner** | Decomposes a goal into numbered, executable steps. Incorporates feedback from prior iterations. |
| **Executor** | Executes individual steps. Can invoke tools (calculator, web search) via LLM function calling. |
| **Critic** | Evaluates executor outputs. Identifies flaws and suggests improvements. |

### Memory System

- **Short-Term Memory (STM):** Ring buffer (default: 10 entries) that maintains recent conversation context within a session.
- **Long-Term Memory (LTM):** JSON-file-backed persistent storage with semantic search (sentence-transformers embeddings). Each session has its own isolated LTM file under `logs/sessions/<session_id>.json`.

---

## Key Features

✅ **True Agentic Loop** — Plan → Execute → Observe → Critique → Refine  
✅ **Tool Use** — LLM function calling with Groq's tool-calling API (OpenAI-compatible protocol)  
✅ **Multi-Step Planning** — Goals are decomposed into discrete, actionable steps  
✅ **Iterative Refinement** — Critic evaluates outputs; poor results trigger re-execution  
✅ **Session Isolation** — Each session has its own STM and LTM (no cross-session leakage)  
✅ **Structured Observability** — SSE streaming of plan/step/tool/critique/complete events  
✅ **Security Controls** — Tool allowlist, argument validation, result sanitization, goal length caps  
✅ **Comprehensive Tests** — 122 passing tests (tools, memory, sessions, agents, API) — all mocked, no LLM calls required  

---

## Tools

The system has **two safe, validated tools**:

### 1. Calculator

- **Safe execution:** AST-based parser (no `eval()` or `exec()`)
- **Supported operations:** `+`, `-`, `*`, `/`, `**`, parentheses, unary minus
- **Blocks:** function calls, imports, attribute access, strings

**Example:**
```python
calculator(expression="(3 + 5) * 2 ** 3")  # → "64"
```

### 2. Web Search (DuckDuckGo)

- **Query sanitization:** 200-character limit, control-character stripping
- **Result sanitization:** URL scheme validation (http/https only), snippet length caps
- **Fallback:** Returns safe error string on network failure (never raises)

**Example:**
```python
web_search(query="Python 3.12 release date")  # → "1. Python 3.12 Released\n   October 2023..."
```

---

## Installation & Quick Start

**⚡ Want to get started immediately? See [SIMPLE_START.md](SIMPLE_START.md) for one-command launch!**

### Prerequisites

- Python 3.8+
- Node.js 18+ (for frontend)
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Quick Setup (Full System)

```bash
# Clone the repository
git clone https://github.com/rohanxlabs/Agentic-AI-system.git
cd Agentic-AI-system

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your GROQ_API_KEY

# Launch both backend + frontend
python start.py
```

**System opens at:** http://localhost:3000

Press `Ctrl+C` to stop both servers.

### Alternative: Backend Only

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure .env (same as above)
cp .env.example .env

# Run CLI
python main.py

# OR run API server
python run_server.py  # API at http://localhost:8000
```

### Run the CLI (Backend Only)

```bash
python main.py
```

**Example interaction:**
```
Enter your autonomous goal: Calculate 15 * 7 using the calculator tool

Running Level-10 Agentic System...

[PLAN]
1. Use calculator tool to compute 15 * 7

[TOOL] calculator
Expression: 15 * 7
Result: 105

[FINAL OUTPUT]
15 * 7 = 105

✓ System completed successfully
```

### Run the Full System (Backend + Frontend)

```bash
python start.py  # Starts both API (port 8000) and UI (port 3000)
```

Open http://localhost:3000 in your browser.

---

## Configuration

Edit `.env` to customize behavior:

```ini
# LLM
GROQ_API_KEY=your_key_here
MODEL_NAME=llama-3.1-8b-instant
TEMPERATURE=0.3
MAX_TOKENS=2048

# Agent Loop
MAX_ITERATIONS=3       # 1=simple mode, >=2=full agentic mode
MAX_TOOL_CALLS=5       # Max tool rounds per step

# Memory
SHORT_TERM_MEMORY_SIZE=10
EMBEDDING_MODEL=all-MiniLM-L6-v2
MEMORY_TOP_K=5

# Security
API_AUTH_KEY=          # Set a random secret to enable X-API-Key auth
RATE_LIMIT_PER_MINUTE=20
```

### Simple vs Full Mode

- **`MAX_ITERATIONS=1`** → Simple mode: single LLM call, good for testing with tight rate limits
- **`MAX_ITERATIONS>=2`** → Full agentic mode: Plan → Execute → Critique → Refine loop

---

## API Reference

### `POST /run`

Execute a goal synchronously.

**Request:**
```json
{
  "goal": "Calculate the factorial of 5",
  "session_id": "optional-uuid",
  "enable_tools": true
}
```

**Response:**
```json
{
  "results": ["The factorial of 5 is 120"],
  "session_id": "uuid"
}
```

### `POST /run/stream`

Execute a goal with SSE (Server-Sent Events) streaming.

**Event types:** `plan`, `step_start`, `tool_call`, `step_result`, `critique`, `complete`, `error`

**Example event:**
```json
{
  "type": "tool_call",
  "tool": "calculator",
  "input": "{\"expression\": \"5*4*3*2*1\"}",
  "output": "120",
  "status": "ok"
}
```

### Other Endpoints

- `GET /sessions` — List all active sessions
- `POST /sessions` — Create a new session
- `GET /sessions/{id}` — Get session details
- `DELETE /sessions/{id}` — Delete a session
- `GET /tools` — List available tools
- `GET /memory/stats` — Memory usage statistics
- `GET /metrics` — System metrics (uptime, requests, response times)

See `api.py` for full FastAPI schema.

---

## Testing

Run the full test suite:

```bash
pytest tests/ -v
```

**122 tests covering:**
- Tool system (allowlist, validation, sanitization)
- Memory (STM buffer, LTM persistence, session isolation)
- Agent loop (planning, execution, tool protocol, critique, streaming)
- API endpoints (request validation, error handling, streaming)

All tests are **fully mocked** — no LLM calls, no network requests, no API keys required.

---

## Security

### Tool Safety

1. **Allowlist enforcement** — Only `calculator` and `web_search` can be invoked
2. **Argument validation** — Type checking, length caps (512 chars per arg)
3. **Result truncation** — Tool outputs capped at 2000 chars
4. **AST-safe calculator** — No `eval()`, no imports, no function calls
5. **URL validation** — Web search only returns http/https URLs

### Input Validation

- Goal strings capped at 2000 characters
- Search queries capped at 200 characters
- Tool arguments validated against schemas before dispatch

### Rate Limiting

- Configurable per-minute rate limit (default: 20 req/min)
- Optional API key authentication via `X-API-Key` header

---

## Limitations

1. **No persistent session storage** — Sessions are in-memory only (lost on server restart)
2. **Single LLM provider** — Currently Groq only (OpenAI-compatible, easy to extend)
3. **Limited tool set** — Only 2 tools (calculator, web search) — designed for demonstration
4. **No multi-modal support** — Text-only (no images, audio, video)
5. **English prompts only** — Not tested with other languages

---

## Roadmap

**Near-term:**
- [ ] Persistent session storage (SQLite / PostgreSQL)
- [ ] Additional tools (file I/O, API calls, code execution sandbox)
- [ ] OpenAI provider support (alongside Groq)
- [ ] Tool usage analytics dashboard

**Long-term:**
- [ ] Multi-agent collaboration (parallel task execution)
- [ ] Custom tool plugin system
- [ ] Advanced memory strategies (summary, hierarchical retrieval)
- [ ] Streaming LLM responses (token-by-token)

---

## Project Structure

```
.
├── agents/              # Agent implementations (Planner, Executor, Critic, Manager)
├── config/              # Configuration (environment variables, constants)
├── frontend/            # Next.js frontend (React, TypeScript, TailwindCSS)
├── llm/                 # LLM integration (Groq API client)
├── logs/                # Runtime logs and session LTM files
│   └── sessions/        # Per-session long-term memory JSON files
├── memory/              # Short-term and long-term memory implementations
├── session/             # Session management (create, retrieve, cleanup)
├── tests/               # Test suite (122 tests, all mocked)
├── tools/               # Tool implementations and registry
├── api.py               # FastAPI application (REST API + SSE streaming)
├── main.py              # CLI entry point
├── run_server.py        # API server entry point
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## Contributing

This is a portfolio/demonstration project. If you'd like to suggest improvements:

1. Open an issue describing the enhancement
2. Fork the repository
3. Create a feature branch
4. Add tests for new functionality
5. Submit a pull request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **Groq** for fast LLM inference (llama-3.1-8b-instant)
- **DuckDuckGo** for privacy-respecting web search
- **sentence-transformers** for semantic memory retrieval
- **FastAPI** for the API framework
- **Next.js** for the frontend framework

---

## Contact

**GitHub:** [github.com/rohanxlabs/Agentic-AI-system](https://github.com/rohanxlabs/Agentic-AI-system)

**Portfolio:** This project demonstrates:
- Agentic AI system design
- LLM orchestration and tool calling
- Multi-step reasoning and planning
- FastAPI + React full-stack development
- Test-driven development (122 passing tests)
- Security-first tool design

Built to showcase practical AI systems engineering beyond simple chatbot implementations.
