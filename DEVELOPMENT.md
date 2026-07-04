# Development Guide

## Project Standards

This document outlines development standards and best practices for the Agentic AI System.

### Code Style

- **Type Hints**: All functions and methods must have type hints
  ```python
  def process_goal(goal: str) -> List[str]:
      """Process a goal and return steps."""
      pass
  ```

- **Docstrings**: Use Google-style docstrings for classes and methods
  ```python
  def execute(self, task: str) -> str:
      """Execute a task with maximum precision.
      
      Args:
          task: Task description to execute
          
      Returns:
          Task execution result
          
      Raises:
          ValueError: If task is empty
      """
      pass
  ```

- **Line Length**: Maximum 100 characters
- **Imports**: Organized as: stdlib, third-party, local (with blank lines between groups)
- **Naming**: Use snake_case for functions/variables and PascalCase for classes

### Directory Structure

```
module_name/
├── __init__.py          # Package marker
├── module_file.py       # Implementation
└── utils.py            # Helpers (if needed)
```

### Testing

While not yet implemented, here's the structure for when tests are added:

```bash
tests/
├── __init__.py
├── test_agents.py
├── test_memory.py
└── test_llm.py
```

Run tests with:
```bash
python -m pytest tests/
```

### Error Handling

Always handle exceptions appropriately:

```python
try:
    result = llm.call(prompt)
except Exception as e:
    logger.error(f"LLM error: {e}")
    raise
```

Use specific exceptions when possible, not bare `except:`.

### Logging

Use the logging module for all messages:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Starting process")
logger.warning("Unexpected value")
logger.error("Failed to process", exc_info=True)
```

Never use `print()` for system output (except in CLI with Rich).

### Adding New Agents

1. Create new file in `agents/` directory
2. Inherit from `BaseAgent`
3. Implement specific agent logic
4. Add type hints and docstrings
5. Update imports in respective modules

Example:
```python
\"\"\"Tool agent for executing external tools.\"\"\"
from agents.base_agent import BaseAgent

class ToolAgent(BaseAgent):
    \"\"\"Agent for tool execution.\"\"\"
    
    def use_tool(self, tool_name: str, args: dict) -> str:
        \"\"\"Use an external tool.
        
        Args:
            tool_name: Name of the tool
            args: Tool arguments
            
        Returns:
            Tool execution result
        \"\"\"
        pass
```

### Configuration

- Never hardcode values
- Use environment variables for all configuration
- Add to `.env.example` when adding new config
- Validate configuration at startup

### Dependencies

- Update `requirements.txt` when adding packages
- Use specific versions for stability
- Minimize external dependencies

### Performance Considerations

1. **Memory Usage**: Monitor memory buffer sizes
2. **API Calls**: Implement caching/batching where possible
3. **Logging**: Use appropriate log levels to avoid performance impact

### Security

- Never log sensitive information (API keys, passwords)
- Validate all user inputs
- Use environment variables for secrets
- Sanitize LLM prompts when using user input

## Deployment

### Local Development

1. Create virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure
4. Run: `python main.py`

### Production Considerations

- Implement proper error reporting
- Set `LOG_LEVEL=WARNING` for production
- Monitor memory files for growth
- Implement backup for long-term memory
- Use process manager (e.g., systemd, supervisord)

## Troubleshooting Development Issues

### Import Errors
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`
- Check relative imports match directory structure

### Type Checking
- Use `mypy` for type checking (when added):
```bash
mypy main.py agents/ llm/ memory/ config/
```

### Common Mistakes
- Forgetting to activate virtual environment
- Not updating `requirements.txt` after `pip install`
- Using `Itm` instead of `ltm` (naming inconsistency)
- Returning inside loops instead of properly structured logic

## CI/CD Pipeline (Future)

When implemented:
- Run type checks with `mypy`
- Run formatting check with `black`
- Run linting with `pylint` or `flake8`
- Run tests with `pytest`
- Generate coverage reports

## Review Checklist

Before committing changes:
- [ ] Type hints added
- [ ] Docstrings complete
- [ ] Error handling implemented
- [ ] Logging added appropriately
- [ ] Requirements.txt updated (if needed)
- [ ] No hardcoded values
- [ ] Code follows style guidelines
- [ ] Tested locally

## Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Groq API Documentation](https://console.groq.com/docs)
- [Rich Library](https://rich.readthedocs.io/)
