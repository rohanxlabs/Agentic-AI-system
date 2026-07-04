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

### Step 5: Run
```bash
python main.py
```

Then enter your goal:
```
Enter your autonomous goal: Write a Python function to check if a number is prime
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

### 1. Code Generation
```
Write a Python decorator that measures function execution time
```

### 2. Problem Analysis
```
Analyze the pros and cons of REST vs GraphQL APIs
```

### 3. Content Creation
```
Write a blog post about machine learning in healthcare
```

### 4. Learning
```
Explain how blockchain technology works
```

### 5. Business
```
Create a marketing plan for a new SaaS product
```

## Adjusting Settings

For faster results, edit `.env`:
```
MAX_ITERATIONS=2
TEMPERATURE=0.1
```

For more detailed results:
```
MAX_ITERATIONS=8
TEMPERATURE=0.5
MAX_TOKENS=4096
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

1. **Read examples**: See [EXAMPLES.md](EXAMPLES.md)
2. **Understand architecture**: See [README.md](README.md)
3. **Development**: See [DEVELOPMENT.md](DEVELOPMENT.md)
4. **All improvements**: See [IMPROVEMENTS.md](IMPROVEMENTS.md)

## Getting Help

1. Check logs: `logs/agentic_system.log`
2. Review examples: [EXAMPLES.md](EXAMPLES.md)
3. Check configuration: [README.md](README.md#configuration)
4. Verify Groq API: [console.groq.com](https://console.groq.com)

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
