# Examples

This document provides practical examples of using the Agentic AI System.

## Basic Usage

### Example 1: Code Generation

```bash
$ python main.py
Enter your autonomous goal: Write a Python function to calculate the nth Fibonacci number efficiently
```

The system will:
1. Break it into steps
2. Generate the code
3. Critique the implementation
4. Refine and improve it

Output:
```
Result 1:
Here's an efficient Fibonacci function using memoization:

def fibonacci(n, memo=None):
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
    return memo[n]
...
```

### Example 2: Problem Analysis

```bash
$ python main.py
Enter your autonomous goal: Analyze the pros and cons of microservices architecture
```

The system works through:
- Planning: Outline key microservices aspects
- Execution: Develop detailed analysis
- Criticism: Ensure comprehensive coverage
- Refinement: Add missing considerations

### Example 3: Documentation Writing

```bash
$ python main.py
Enter your autonomous goal: Create API documentation for a REST endpoint handling user registration
```

Output includes:
- Step-by-step guide
- Detailed endpoint specs
- Request/response examples
- Error handling documentation

## Configuration Examples

### Fast Processing (2 iterations)

Create `.env`:
```
MAX_ITERATIONS=2
TEMPERATURE=0.2
MAX_TOKENS=1024
```

Good for quick drafts.

### Creative Output (More iterations)

```
MAX_ITERATIONS=10
TEMPERATURE=0.8
MAX_TOKENS=4096
```

Ideal for brainstorming and creative tasks.

### Production Use (Deterministic)

```
MAX_ITERATIONS=5
TEMPERATURE=0.1
MAX_TOKENS=2048
LOG_LEVEL=WARNING
```

For consistent, reliable results.

## Programmatic Usage

You can also use the system as a library:

```python
from llm.groq_llm import GroqLLM
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.critic_agent import CriticAgent
from agents.manager_agent import ManagerAgent

# Initialize
llm = GroqLLM()
stm = ShortTermMemory()
ltm = LongTermMemory(storage_file="logs/custom_memory.json")

# Create agents
planner = PlannerAgent("Planner", llm, stm, ltm)
executor = ExecutorAgent("Executor", llm, stm, ltm)
critic = CriticAgent("Critic", llm, stm, ltm)

# Run system
manager = ManagerAgent(planner, executor, critic, ltm)
results = manager.run("Your goal here")

# Access results
for result in results:
    print(result)

# Recall memories
print(ltm.recall())
```

## Advanced Examples

### Custom Agent

Create your own agent:

```python
from agents.base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    \"\"\"Agent for research tasks.\"\"\"
    
    def research(self, topic: str) -> str:
        prompt = f\"\"\"\nResearch the topic below comprehensively:\n{topic}\nProvide:\n- Overview\n- Key Points\n- Recent Developments\n- Implications\n\"\"\"\n        return self.think(prompt)

# Use it
research_agent = ResearchAgent("Researcher", llm, stm, ltm)
report = research_agent.research("Quantum Computing")
```

### Batch Processing

```python
goals = [
    "Generate 5 creative business ideas",
    "Analyze market trends for SaaS",
    "Create marketing strategy"
]

results_db = {}

for goal in goals:
    results = manager.run(goal)
    results_db[goal] = results
    
# Access all results
for goal, results in results_db.items():
    print(f"Goal: {goal}")
    print(f"Results: {results}\n")
```

### Memory Analysis

```python
# Check recent context
recent = stm.get()
print("Recent interactions:")
print(recent)

# Analyze historical results
all_memories = ltm.recall()
print("All saved results:")
print(all_memories)

# Get specific iterations
import json
with open("logs/memory.json") as f:
    memory_data = json.load(f)
    for entry in memory_data[:5]:  # First 5 entries
        print(f"Timestamp: {entry['timestamp']}")
        print(f"Content: {entry['content']}\n")
```

## Common Patterns

### Iterative Refinement

```python
# Get initial draft
draft = manager.run("Write a blog post about Python async/await")

# Refine with specific focus
refined = manager.run("Improve the blog post: add code examples and best practices")

# Further refinement
final = manager.run("Add performance tips and common pitfalls to the blog post")
```

### Multi-Step Workflow

```python
# Step 1: Research
research = planner.create_plan("Research machine learning trends")

# Step 2: Analyze
analysis_plan = executor.execute_task("Analyze the research findings")

# Step 3: Critique
critique = critic.critique(analysis_plan)

# Step 4: Improve
improvement = executor.think(f"Improve based on this critique: {critique}")
```

### Generate and Validate

```python
# Generate content
code = executor.execute_task("Generate a Python decorator pattern example")

# Validate
critique = critic.critique(code)

# If critique is negative, regenerate
if "error" in critique.lower() or "incorrect" in critique.lower():
    code = executor.execute_task("Fix the code based on: " + critique)
    print("Fixed code:", code)
else:
    print("Code approved:", code)
```

## Troubleshooting Examples

### Empty Results

```python
# Check if goal was too vague
if not results:
    # Try a more specific goal
    results = manager.run("Write a 300-word tutorial on Python type hints with examples")
```

### Memory Issues

```python
# Check memory size
print(f"STM size: {len(stm.buffer)}")

# Clear if needed
stm.clear()

# Check LTM
print(f"LTM entries: {len(ltm.store)}")
```

### API Errors

```python
try:
    results = manager.run(goal)
except ValueError as e:
    print(f"Configuration error: {e}")
    # Check .env file
except Exception as e:
    print(f"API error: {e}")
    # Check Groq API status
```

## Performance Tuning

### For Speed
```
- MAX_ITERATIONS=2
- MAX_TOKENS=1024
- TEMPERATURE=0.1
```

### For Quality
```
- MAX_ITERATIONS=8
- MAX_TOKENS=4096
- TEMPERATURE=0.5
```

### For Consistency
```
- TEMPERATURE=0.0
- MAX_ITERATIONS=5
- SHORT_TERM_MEMORY_SIZE=5
```

## Tips and Tricks

1. **Break complex goals into sub-goals**: The system performs better with focused objectives
2. **Use specific prompts**: "Write a Python function" vs "Write a Python function to validate email format with regex"
3. **Monitor logs**: Check `logs/agentic_system.log` for debugging
4. **Review memory**: Use `ltm.recall()` to understand what the system learned
5. **Adjust iterations**: More iterations = better quality but slower
6. **Fine-tune temperature**: Lower for factual, higher for creative content
