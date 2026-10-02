import asyncio
import os
import sys

# Ensure absolute path resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from mirofish_os.brain.memory import SQLiteMemory
from mirofish_os.evolution.router import DynamicRouter
from mirofish_os.interface.manager import ManagerAgent

console = Console()

async def interactive_shell():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(Panel.fit(
        "[bold cyan]🚀 MiroFish Autonomous OS (Terminal UI)[/bold cyan]\n"
        "[italic]Elite Architecture | SQLite Memory | Dynamic Routing[/italic]", 
        border_style="cyan"
    ))
    
    console.print("[yellow]Initializing Core AI Engines...[/yellow]")
    memory = SQLiteMemory()
    await memory.connect()
    
    router = DynamicRouter()
    manager = ManagerAgent(memory=memory, router=router)
    
    session_id = "local_terminal_user"
    console.print("[green]System Online. Type 'exit' to shutdown.[/green]\n")
    
    while True:
        try:
            user_input = Prompt.ask("[bold magenta]You[/bold magenta]")
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
                
            if not user_input.strip():
                continue
            
            with console.status("[bold cyan]OS is thinking (Routing internally)...[/bold cyan]"):
                response = await manager.chat(session_id, user_input)
                
            console.print("\n[bold cyan]MiroFish OS[/bold cyan]:")
            console.print(Markdown(response))
            console.print("-" * 50)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]System Error: {e}[/bold red]")

    await memory.close()
    console.print("[bold red]\nSystem shutting down. Goodbye![/bold red]")

if __name__ == "__main__":
    asyncio.run(interactive_shell())
