# Quick Start Guide

Get up and running with the Agentic AI System in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- Groq API key (free at [console.groq.com](https://console.groq.com))

## Installation (Window

s)

### Step 1: Clone/Download Project
```bash
cd e:\Projects\Agentic-AI-System
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
copy .env.example .env
# Edit .env and add your GROQ_API_KEY
# Open .env in any text editor and replace:
# GROQ_API_KEY=your_api_key_here
```

### 5. Run
```bash
python main.py
```

Then enter your goal when prompted. The agent will plan, execute, and display results.

**Example:**
```
Enter your autonomous goal: Calculate the factorial of 5 using the calculator tool

[Agent execution with tool calls...]

✓ System completed successfully
```

## Installation (macOS/Linux)

```bash
cd Agentic-AI-System
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key

python main.py
```

## Getting Your Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Go to API Keys section
4. Create new API key
5. Copy and paste into `.env` file

```
GROQ_API_KEY=gsk_your_key_here
```

## First Run Example

```bash
$ python main.py

Agentic AI System
--------------------------------------------------

Enter your autonomous goal: Explain quantum computing in simple terms

Goal
┌──────────────────────────────────────────────────────┐
│ Explain quantum computing in simple terms            │
└──────────────────────────────────────────────────────┘

Running Level-10 Agentic System...

[bold green]FINAL OUTPUT[/bold green]

Result 1:
Quantum computing harnesses quantum mechanics principles...
```

## Common Goals to Try

### 1. Multi-step with Tools
```
Research the current weather in Tokyo and tell me if I need an umbrella
```

### 2. Calculator Tool
```
Calculate the compound interest on $1000 at 5% annual rate for 3 years
```

### 3. Web Search Tool
```
Find the latest Python version and list 3 new features
```

### 4. Planning Task
```
Create a 3-step plan to learn machine learning
```

### 5. Reasoning
```
Explain the difference between supervised and unsupervised learning
```

## Adjusting Settings

Edit `.env` to customize behavior:

**For faster results (simple mode):**
```
MAX_ITERATIONS=1
TEMPERATURE=0.1
```

**For full agentic mode (planning + critique):**
```
MAX_ITERATIONS=3
TEMPERATURE=0.3
MAX_TOKENS=2048
```

## Viewing Results

Results (and logs) are saved in `logs/`:
- `agentic_system.log` - System logs
- `memory.json` - All results with timestamps

View recent results:
```bash
# On Windows:
type logs\agentic_system.log

# On macOS/Linux:
tail -f logs/agentic_system.log
```

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "GROQ_API_KEY not found"
- Check that `.env` file exists
- Verify it contains: `GROQ_API_KEY=your_key`
- Check file is in project root

### "Connection timeout"
- Check internet connection
- Verify API key is correct
- Increase timeout in `.env`: `API_TIMEOUT=60`

### "Empty results"
- Try a more specific goal
- Increase `MAX_ITERATIONS` in `.env`
- Check logs: `logs/agentic_system.log`

## Next Steps

1. **Try different goals**: Test the agent with multi-step tasks
2. **Explore the API**: See [README.md](README.md#api-reference) for endpoints
3. **Run tests**: `pytest tests/ -v` to see 122 passing tests
4. **Customize**: Edit `.env` to adjust `MAX_ITERATIONS`, `TEMPERATURE`, etc.

## Getting Help

1. Check logs: `logs/agentic_system.log`
2. Review configuration: [README.md](README.md#configuration)
3. Verify Groq API: [console.groq.com](https://console.groq.com)
4. Run tests to verify setup: `pytest tests/ -v`

## Pro Tips

1. **Be specific**: "Write a Python function to calculate fibonacci with memoization" works better than "write code"
2. **Monitor progress**: Check `logs/agentic_system.log` while running
3. **Experiment**: Try different MAX_ITERATIONS and TEMPERATURE values
4. **Review results**: Use `ltm.recall()` to see all past results

## System Requirements

- **Disk**: 500MB (for dependencies and logs)
- **RAM**: 2GB minimum
- **Internet**: Required (for Groq API)
- **Python**: 3.8+

## Supported Platforms

✅ Windows
✅ macOS
✅ Linux

## Having Issues?

1. Activate virtual environment
2. Ensure dependencies installed: `pip install -r requirements.txt`
3. Check `.env` has correct API key
4. Review logs: `logs/agentic_system.log`
5. Try example goal first

## Ready To Go!

You're all set! Start with:
```bash
python main.py
```

Then enter: "Write a Python hello world program"

Enjoy! 🚀
