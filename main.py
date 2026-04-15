"""Main entry point for the Agentic AI System."""
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from llm.groq_llm import GroqLLM
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.critic_agent import CriticAgent
from agents.manager_agent import ManagerAgent
from config.config import LOG_LEVEL, LOG_FILE

# Setup logging
log_path = Path(LOG_FILE)
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
console = Console()


def main() -> None:
    """Run the Agentic AI System."""
    try:
        # Initialize components
        logger.info("Initializing Agentic AI System...")
        
        llm = GroqLLM()
        stm = ShortTermMemory()
        ltm = LongTermMemory()

        planner = PlannerAgent("Planner", llm, stm, ltm)
        executor = ExecutorAgent("Executor", llm, stm, ltm)
        critic = CriticAgent("Critic", llm, stm, ltm)

        manager = ManagerAgent(planner, executor, critic, ltm)
        
        # Get user goal
        console.print("\n[bold cyan]Agentic AI System[/bold cyan]", justify="center")
        console.print("-" * 50, justify="center")
        
        goal = console.input("\n[bold]Enter your autonomous goal:[/bold] ")
        
        if not goal.strip():
            console.print("[red]Error: Goal cannot be empty[/red]")
            return
        
        console.print(Panel(goal, title="Goal", expand=False))
        
        # Run the system
        logger.info(f"Starting system with goal: {goal}")
        console.print("\n[bold cyan]Running Level-10 Agentic System...[/bold cyan]\n")
        
        results = manager.run(goal)
        
        # Display results
        console.print(Panel("[bold green]FINAL OUTPUT[/bold green]", expand=False))
        for i, result in enumerate(results, 1):
            console.print(f"\n[bold yellow]Result {i}:[/bold yellow]")
            console.print(result)
        
        logger.info("System completed successfully")
        console.print("\n[bold green]✓ System completed successfully[/bold green]")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        console.print(f"[red]Configuration Error: {e}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("System interrupted by user")
        console.print("\n[yellow]System interrupted[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
