from rich.console import Console
from rich.table import Table
from typing import Dict

class ResultVisualizer:
    def __init__(self):
        self.console = Console()

    def print_welcome(self, num_tools: int):
        self.console.print(f"\n[bold blue]🚀 Starting LLM Tool Performance Audit[/bold blue]")
        self.console.print(f"[dim]Simulating agent environment with {num_tools} tools...[/dim]\n")

    def print_comparison(self, std_res: Dict, def_res: Dict):
        table = Table(title="Performance Comparison")

        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Standard", style="magenta")
        table.add_column("Deferred (Search)", style="green")
        table.add_column("Delta", justify="right", style="bold white")

        # Calculate Deltas
        lat_delta = def_res['latency_seconds'] - std_res['latency_seconds']
        tok_delta = def_res['input_tokens'] - std_res['input_tokens']
        
        # Latency Row
        lat_color = "red" if lat_delta > 0 else "green"
        table.add_row(
            "Latency (s)", 
            f"{std_res['latency_seconds']:.3f}s",
            f"{def_res['latency_seconds']:.3f}s",
            f"[{lat_color}]{lat_delta:+.3f}s[/{lat_color}]"
        )

        # Tokens Row
        tok_color = "red" if tok_delta > 0 else "green" 
        # Note: Positive delta on tokens is bad (red), negative is good (green)
        table.add_row(
            "Input Tokens",
            str(std_res['input_tokens']),
            str(def_res['input_tokens']),
            f"[{tok_color}]{tok_delta:+}[/{tok_color}]"
        )

        self.console.print(table)
        
        self.console.print("\n[bold]Analysis:[/bold]")
        if tok_delta > 0:
            self.console.print("[yellow]⚠️  Deferred loading used MORE tokens. This happens when the System Prompt is large, as it is processed twice.[/yellow]")
        else:
            self.console.print("[green]✅ Deferred loading successfully reduced token count.[/green]")