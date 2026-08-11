# Architecture Documentation

## System Overview

The Agentic AI System implements a **Plan → Execute → Observe → Critique → Refine** loop orchestrated by a Manager agent that coordinates three specialized agents (Planner, Executor, Critic).

---

## Component Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                          Frontend (Next.js)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Workspace  │  │  Sessions   │  │   Agents    │  │   Memory    │ │
│  │    Page     │  │    Page     │  │    Page     │  │    Page     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         └────────────────┴────────────────┴────────────────┘         │
│                              │ (SSE / REST)                           │
└──────────────────────────────┼────────────────────────────────────────┘
                               ↓
┌───────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (api.py)                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  Endpoints: /run, /run/stream, /sessions, /tools, /metrics      │ │
│  └──────────────────────────────┬───────────────────────────────────┘ │
│                                 ↓                                      │
│         ┌───────────────────────────────────────┐                     │
│         │      Session Store (in-memory)        │                     │
│         │  ┌─────────────────────────────────┐  │                     │
│         │  │  Session ID → {STM, LTM, ...}   │  │                     │
│         │  └─────────────────────────────────┘  │                     │
│         └───────────────────┬───────────────────┘                     │
└─────────────────────────────┼─────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────────┐
│                       Manager Agent                                   │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  Orchestrates: Plan → Execute → Critique → Refine                │ │
│  │  Manages: Iteration count, deadline, event streaming             │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐          │
│  │  Planner    │      │  Executor   │      │   Critic    │          │
│  │   Agent     │      │   Agent     │      │    Agent    │          │
│  │             │      │             │      │             │          │
│  │ - Decomposes│      │ - Executes  │      │ - Evaluates │          │
│  │   goals     │      │   steps     │      │   outputs   │          │
│  │ - Creates   │      │ - Calls     │      │ - Suggests  │          │
│  │   numbered  │      │   tools     │      │   improve-  │          │
│  │   plans     │      │ - Processes │      │   ments     │          │
│  │             │      │   results   │      │             │          │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘          │
│         │                    │                     │                  │
│         └────────────────────┴─────────────────────┘                  │
│                              │                                        │
│                    ┌─────────┴─────────┐                             │
│                    │                   │                             │
└────────────────────┼───────────────────┼─────────────────────────────┘
                     ↓                   ↓
     ┌───────────────────────┐   ┌──────────────────┐
     │   LLM (Groq API)      │   │  Tool Registry   │
     │                       │   │                  │
     │ - llama-3.1-8b-instant│   │ - Allowlist      │
     │ - Function calling    │   │ - Validation     │
     │ - Rate limit retry    │   │ - Dispatch       │
     └───────────────────────┘   └────────┬─────────┘
                                          │
                           ┌──────────────┴──────────────┐
                           ↓                             ↓
                  ┌─────────────────┐         ┌─────────────────┐
                  │   Calculator    │         │  Web Search     │
                  │   (AST-safe)    │         │  (DuckDuckGo)   │
                  │                 │         │                 │
                  │ - No eval()     │         │ - Query cap     │
                  │ - No imports    │         │ - Result        │
                  │ - Arithmetic    │         │   sanitization  │
                  │   only          │         │ - URL validation│
                  └─────────────────┘         └─────────────────┘
```

---

## Data Flow: Agentic Execution Loop

### High-Level Flow

```
┌─────────────┐
│  User Goal  │
└──────┬──────┘
       ↓
┌─────────────────────────────────────────────────────┐
│  1. PLANNING PHASE                                  │
│  ┌──────────────────────────────────────────────┐  │
│  │ Planner Agent:                               │  │
│  │ - Recalls relevant past memories (LTM)       │  │
│  │ - Breaks goal into numbered steps            │  │
│  │ - Yields {"type": "plan", "content": "..."}  │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  2. EXECUTION PHASE (for each step)                 │
│  ┌──────────────────────────────────────────────┐  │
│  │ Executor Agent:                              │  │
│  │ - Yields {"type": "step_start", ...}         │  │
│  │ - Calls LLM with tool schemas                │  │
│  │                                               │  │
│  │ IF tool requested:                           │  │
│  │   → Execute tool (calculator / web_search)   │  │
│  │   → Validate arguments                       │  │
│  │   → Sanitize result                          │  │
│  │   → Yields {"type": "tool_call", ...}        │  │
│  │   → Feed result back to LLM (role="tool")    │  │
│  │   → Repeat up to MAX_TOOL_CALLS rounds       │  │
│  │                                               │  │
│  │ - Yields {"type": "step_result", ...}        │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  3. CRITIQUE PHASE                                  │
│  ┌──────────────────────────────────────────────┐  │
│  │ Critic Agent:                                │  │
│  │ - Reviews step result                        │  │
│  │ - Identifies flaws / missing parts           │  │
│  │ - Yields {"type": "critique", ...}           │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       ↓
         ┌─────────────────────────┐
         │ Critique acceptable?    │
         └─────────┬───────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ↓ NO                  ↓ YES
┌───────────────┐      ┌──────────────┐
│ REFINE PHASE  │      │  ACCEPT      │
│               │      │  RESULT      │
│ Executor:     │      └──────────────┘
│ - Re-execute  │
│   with critic │
│   feedback    │
└───────────────┘
        ↓
  [Loop to next step or iteration]
        ↓
┌─────────────────────────────────────────────────────┐
│  4. COMPLETION                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Manager:                                     │  │
│  │ - All steps done OR MAX_ITERATIONS reached   │  │
│  │ - Saves final result to LTM                  │  │
│  │ - Yields {"type": "complete", "result": ...} │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Memory Architecture

### Short-Term Memory (STM)

```
┌────────────────────────────────────────┐
│     ShortTermMemory (per-session)      │
├────────────────────────────────────────┤
│  Ring buffer: [entry₁, entry₂, ...]   │
│  Max size: 10 (configurable)          │
│  Scope: Single session only            │
│  Purpose: Recent conversation context  │
└────────────────────────────────────────┘
```

- **Storage:** In-memory list (Python)
- **Lifecycle:** Exists while session is active
- **Overflow:** Oldest entries automatically dropped
- **Use case:** Prepended to LLM prompts for contextual coherence

### Long-Term Memory (LTM)

```
┌────────────────────────────────────────┐
│  LongTermMemory (per-session file)     │
├────────────────────────────────────────┤
│  File: logs/sessions/<uuid>.json       │
│  Entries: [                            │
│    {                                   │
│      "timestamp": "ISO-8601",          │
│      "content": "text",                │
│      "embedding": [0.1, 0.2, ...]     │
│    }, ...                              │
│  ]                                     │
│  Embedding model: all-MiniLM-L6-v2    │
│  Retrieval: Cosine similarity (top-K)  │
└────────────────────────────────────────┘
```

- **Storage:** JSON file per session (persistent across restarts)
- **Lifecycle:** Survives server restarts (file-backed)
- **Retrieval:** Semantic search via sentence-transformers
- **Isolation:** Each session has its own LTM file (no cross-session leakage)

---

## Tool Execution Protocol

### OpenAI / Groq Function Calling Flow

```
┌────────────────────────────────────────────────┐
│  1. Executor calls LLM with tool schemas       │
│     messages = [{"role": "user", ...}]         │
│     tools = TOOL_SCHEMAS                       │
└─────────────────────┬──────────────────────────┘
                      ↓
┌────────────────────────────────────────────────┐
│  2. LLM response includes tool_calls           │
│     {                                          │
│       "content": None,                         │
│       "tool_calls": [                          │
│         {                                      │
│           "id": "call_abc123",   ← CRITICAL   │
│           "name": "calculator",                │
│           "arguments": {"expression": "2+2"}   │
│         }                                      │
│       ]                                        │
│     }                                          │
└─────────────────────┬──────────────────────────┘
                      ↓
┌────────────────────────────────────────────────┐
│  3. Executor dispatches to Tool Registry       │
│     - Validates tool name against ALLOWLIST    │
│     - Validates arguments (type, length)       │
│     - Executes: execute_tool(name, args)       │
│     - Result: "4"                              │
└─────────────────────┬──────────────────────────┘
                      ↓
┌────────────────────────────────────────────────┐
│  4. Executor builds role="tool" message        │
│     messages.append({                          │
│       "role": "tool",            ← REQUIRED    │
│       "tool_call_id": "call_abc123",  ← MATCH │
│       "content": "4"                           │
│     })                                         │
└─────────────────────┬──────────────────────────┘
                      ↓
┌────────────────────────────────────────────────┐
│  5. Executor calls LLM again with tool result  │
│     LLM sees the result and continues          │
└────────────────────────────────────────────────┘
```

**Critical requirements:**
- Tool result messages MUST use `role="tool"` (not `role="user"`)
- Tool result messages MUST include `tool_call_id` matching the request
- The `id` field from the LLM's tool call must be preserved

---

## Session Lifecycle

```
┌─────────────────────────────────────────────┐
│  POST /run  OR  POST /run/stream            │
│  {                                          │
│    "goal": "...",                           │
│    "session_id": "optional-uuid",           │
│    "enable_tools": true                     │
│  }                                          │
└──────────────────┬──────────────────────────┘
                   ↓
         ┌─────────────────────┐
         │ session_id present? │
         └──────┬──────────────┘
                │
       ┌────────┴────────┐
       ↓ YES             ↓ NO
┌──────────────┐  ┌──────────────────┐
│ Reuse        │  │ Create new       │
│ existing     │  │ session:         │
│ session      │  │ - Generate UUID  │
│              │  │ - Create STM     │
│ - Same STM   │  │ - Create LTM file│
│ - Same LTM   │  │   (logs/sessions/│
│              │  │    <uuid>.json)  │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       └────────┬──────────┘
                ↓
     ┌────────────────────┐
     │  Session active    │
     │  - STM buffers     │
     │    context         │
     │  - LTM stores      │
     │    results         │
     │  - Status tracked  │
     └────────┬───────────┘
              ↓
    ┌───────────────────────┐
    │  Session idle for     │
    │  > 1 hour?            │
    └────────┬──────────────┘
             │
      ┌──────┴──────┐
      ↓ YES         ↓ NO
┌─────────────┐ ┌────────────┐
│ Cleanup     │ │ Keep alive │
│ (automatic) │ └────────────┘
└─────────────┘
```

---

## Security Model

### Defense Layers

```
┌──────────────────────────────────────────────┐
│  Layer 1: Input Validation                   │
│  - Goal length cap: 2000 chars               │
│  - Query length cap: 200 chars               │
│  - Request rate limiting                     │
└──────────────────┬───────────────────────────┘
                   ↓
┌──────────────────────────────────────────────┐
│  Layer 2: Tool Allowlist                     │
│  - Only pre-approved tools can execute       │
│  - TOOL_ALLOWLIST = {"calculator",           │
│                      "web_search"}           │
│  - Unknown tools → Error (logged)            │
└──────────────────┬───────────────────────────┘
                   ↓
┌──────────────────────────────────────────────┐
│  Layer 3: Argument Validation                │
│  - Type checking (string, dict, etc.)        │
│  - Length caps: MAX_ARG_LENGTH = 512 chars   │
│  - Schema validation (required fields)       │
└──────────────────┬───────────────────────────┘
                   ↓
┌──────────────────────────────────────────────┐
│  Layer 4: Safe Tool Execution                │
│  ┌─────────────────────────────────────────┐ │
│  │ Calculator: AST-only (no eval/exec)     │ │
│  │ - Blocks: imports, function calls,      │ │
│  │   attribute access, strings             │ │
│  └─────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────┐ │
│  │ Web Search: Result sanitization         │ │
│  │ - Control char stripping                │ │
│  │ - URL scheme validation (http/https)    │ │
│  │ - Snippet length caps                   │ │
│  └─────────────────────────────────────────┘ │
└──────────────────┬───────────────────────────┘
                   ↓
┌──────────────────────────────────────────────┐
│  Layer 5: Result Truncation                  │
│  - All tool outputs capped at 2000 chars     │
│  - Prevents context overflow attacks         │
└──────────────────────────────────────────────┘
```

---

## Configuration Flow

```
.env file
   ↓
config/config.py
   ↓ (loads environment variables)
   ├─→ LLM config     → llm/groq_llm.py
   ├─→ Agent config   → agents/manager_agent.py
   ├─→ Memory config  → memory/long_term.py
   ├─→ Tool config    → tools/tool_registry.py
   └─→ Security config → api.py
```

**Key configuration points:**
- `MAX_ITERATIONS` — Controls simple vs full agentic mode
- `MAX_TOOL_CALLS` — Prevents infinite tool loops
- `EMBEDDING_MODEL` — Controls LTM semantic search quality
- `API_AUTH_KEY` — Enables/disables API authentication
- `RATE_LIMIT_PER_MINUTE` — Controls request throttling

---

## Testing Architecture

All 122 tests are **fully mocked** — no LLM calls, no API keys, no network requests required.

```
tests/
├── test_tools.py (34 tests)
│   ├── Calculator: AST safety, operations, error handling
│   ├── Tool Registry: Allowlist, validation, dispatch
│   └── Web Search: Sanitization, URL validation
│
├── test_memory.py (14 tests)
│   ├── STM: Buffer, overflow, isolation
│   └── LTM: Persistence, recall, semantic search (mocked embedder)
│
├── test_sessions.py (15 tests)
│   ├── Session creation, reuse, deletion
│   ├── STM/LTM isolation between sessions
│   └── Cleanup of stale sessions
│
├── test_agents.py (38 tests)
│   ├── BaseAgent: think(), STM integration
│   ├── Planner: Plan creation, memory integration
│   ├── Executor: Tool protocol, max-rounds guard
│   ├── Critic: Evaluation logic
│   └── Manager: Loop orchestration, streaming events
│
└── test_api.py (21 tests)
    ├── All endpoints (/run, /run/stream, /sessions, etc.)
    ├── Request validation (empty goal, length caps)
    ├── Error handling (LLM errors, 404s)
    └── SSE streaming (event types, session_id propagation)
```

**Mocking strategy:**
- LLM calls → `MagicMock` returns pre-defined strings
- Embeddings → `MagicMock` returns numpy arrays
- Network requests → Not called (tool dispatch mocked)

---

## Performance Characteristics

| Metric | Typical Value | Notes |
|--------|---------------|-------|
| API response (simple mode) | 2-5s | Single LLM call |
| API response (full mode, 3 iterations) | 10-30s | Depends on step count + tool calls |
| Tool call overhead | ~50-200ms | Argument validation + dispatch |
| LTM semantic search | ~10-50ms | Depends on store size |
| Session creation | <10ms | In-memory only |
| Test suite execution | ~3s | 122 tests, all mocked |

---

## Deployment Considerations

### Environment Variables (Production)

```bash
GROQ_API_KEY=<actual_key>         # Never commit
API_AUTH_KEY=<random_secret>      # 32+ char random string
MAX_ITERATIONS=3                  # Balance quality vs speed
RATE_LIMIT_PER_MINUTE=20          # Adjust per workload
LOG_LEVEL=WARNING                 # Reduce log volume
```

### Scaling

- **Horizontal:** Multiple API server instances behind a load balancer
  - Sessions are in-memory → use sticky sessions OR external session store (Redis, PostgreSQL)
- **Vertical:** Single server can handle ~100 concurrent sessions (depends on LLM latency)

### Monitoring

- Track `/metrics` endpoint for uptime, request counts, response times
- Monitor LLM rate limits (Groq free tier: varies by model)
- Monitor LTM file growth (`logs/sessions/` directory size)

---

## Future Architecture Improvements

1. **Persistent session storage** — Move from in-memory to PostgreSQL/Redis
2. **Agent pool** — Pre-warm agent instances for faster response
3. **Streaming LLM responses** — Token-by-token SSE from LLM
4. **Tool plugin system** — Dynamic tool loading from external modules
5. **Multi-agent orchestration** — Parallel task execution across multiple agents
6. **Advanced memory** — Hierarchical summarization, temporal decay
7. **Observability** — OpenTelemetry tracing, Prometheus metrics

---

**End of Architecture Documentation**
