import asyncio

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

console = Console()

class CLI:
    """
    Rich interactive terminal UI with live system telemetry.
    """
    def __init__(self) -> None:
        self.console = console

    def display_welcome(self) -> None:
        self.console.print(Panel.fit("[bold cyan]MiroFish Autonomous OS[/bold cyan]\n[italic]Universal AI Operating System[/italic]", border_style="blue"))

    def render_dashboard(self, workers: int, mem_usage: float, q_size: int) -> Table:
        table = Table(title="OS Telemetry", style="cyan")
        table.add_column("Metric", style="magenta")
        table.add_column("Value", style="green")
        
        table.add_row("Active Workers", str(workers))
        table.add_row("Memory Usage (GB)", f"{mem_usage:.2f}")
        table.add_row("Task[Any] Queue Size", str(q_size))
        return table

    async def run_live_dashboard(self) -> None:
        """Simulates a live dashboard loop."""
        # In a real setup, we'd hook this to the ApexOrchestrator state
        with Live(self.render_dashboard(8, 2.1, 0), refresh_per_second=2) as live:
            for _ in range(5):
                await asyncio.sleep(1)
                live.update(self.render_dashboard(8, 2.2, 0))
