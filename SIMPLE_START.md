# Quick Start Guide — Simplified Setup

## One-Command Launch 🚀

Run both backend + frontend with a single command:

```bash
python start.py
```

That's it! The system will:
1. ✅ Check your environment (.env file, dependencies)
2. ✅ Install frontend dependencies if needed (auto npm install)
3. ✅ Start the backend API (port 8000)
4. ✅ Start the frontend UI (port 3000)
5. ✅ Open your browser to http://localhost:3000

---

## First-Time Setup (5 minutes)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Groq API key
# Get a free key at: https://console.groq.com
```

Edit `.env`:
```ini
GROQ_API_KEY=gsk_your_actual_key_here
```

### 3. Launch!

```bash
python start.py
```

**System will open at:** http://localhost:3000

---

## What You'll See

### Browser (http://localhost:3000)
- **Workspace page** with a goal input form
- Enter a goal like: `"Calculate 15 * 7 using the calculator tool"`
- Click "Run Agent"
- Watch the AI agent:
  - 📋 Plan the steps
  - 🔧 Execute tools (calculator, web search)
  - 📊 Show results in real-time

### Terminal Output
```
[API] Uvicorn running on http://localhost:8000
[UI]  Local: http://localhost:3000

✓ System ready! Open http://localhost:3000 in your browser
```

Press **Ctrl+C** to stop both servers.

---

## Example Goals to Try

### Simple (No Rate Limits)
```
Calculate 15 * 7 using the calculator tool
```

### Multi-Step (May hit rate limits on free tier)
```
Calculate the factorial of 5
```

### With Web Search (Requires good rate limit)
```
Find the capital of France and calculate its population divided by 1000
```

**Note:** Groq free tier has rate limits. Start with simple goals first!

---

## Troubleshooting

### "Module not found: sentence_transformers"
```bash
pip install sentence-transformers==3.3.1
```

### "GROQ_API_KEY not set"
Edit `.env` and add your key from https://console.groq.com

### "npm not found"
Install Node.js from https://nodejs.org (LTS version recommended)

### Frontend won't start
```bash
cd frontend
npm install
cd ..
python start.py
```

### Rate limit errors (429)
- Groq free tier has limits
- Try simpler goals (fewer LLM calls)
- Wait a minute and try again

---

## Architecture

```
┌──────────────┐         ┌──────────────┐
│   Browser    │ ←────→  │   Frontend   │
│ localhost:   │  HTTP   │   (Next.js)  │
│    3000      │         │              │
└──────────────┘         └───────┬──────┘
                                 │
                            SSE Streaming
                                 │
                         ┌───────▼──────┐
                         │   Backend    │
                         │   FastAPI    │
                         │ localhost:   │
                         │    8000      │
                         └───────┬──────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼──────┐         ┌───────▼──────┐
            │  Groq LLM    │         │    Tools     │
            │              │         │ · Calculator │
            │ (llama-3.1)  │         │ · Web Search │
            └──────────────┘         └──────────────┘
```

---

## What Makes This "Agentic"?

Unlike a simple chatbot, this system:
1. **Plans** — Breaks goals into steps
2. **Acts** — Executes tools autonomously
3. **Observes** — Processes tool results
4. **Reasons** — Evaluates quality
5. **Iterates** — Refines approach (up to 3 iterations)

**It's a genuine autonomous agent, not just an LLM wrapper.**

---

## Alternative: CLI Only

Don't need the UI? Run the CLI:

```bash
python main.py
```

Enter your goal when prompted. Results print to the terminal.

---

## Testing (No API Key Needed)

Run the test suite without Groq:

```bash
pytest tests/ -v
```

All 122 tests are mocked — no LLM calls, no API keys required.

---

## Next Steps

- Read [README.md](README.md) for full documentation
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Check [FINAL_AUDIT_REPORT.md](FINAL_AUDIT_REPORT.md) for project audit

---

**That's it! You now have a working agentic AI system.** 🎉
