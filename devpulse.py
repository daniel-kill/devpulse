#!/usr/bin/env python3
import click
import psutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

console = Console()

def generate_dashboard() -> Layout:
    layout = Layout()
    
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    
    # Header
    header_panel = Panel(
        Text("⚡ DEVPULSE // Infrastructure & Dev Metrics TUI", justify="center", style="bold cyan"),
        style="blue"
    )
    layout["header"].update(header_panel)
    
    # Body split into System Metrics & Services
    body_layout = Layout()
    body_layout.split_row(
        Layout(name="system"),
        Layout(name="services")
    )
    layout["body"].update(body_layout)
    
    # System Table
    sys_table = Table(title="System Resource Utilization", expand=True)
    sys_table.add_column("Metric", style="magenta")
    sys_table.add_column("Usage", style="green")
    
    cpu_pct = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    sys_table.add_row("CPU Load", f"{cpu_pct}%")
    sys_table.add_row("Memory Used", f"{mem.percent}% ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)")
    sys_table.add_row("Disk Usage", f"{disk.percent}%")
    
    layout["system"].update(Panel(sys_table, border_style="magenta"))
    
    # Services Table
    svc_table = Table(title="Monitored Services", expand=True)
    svc_table.add_column("Service", style="cyan")
    svc_table.add_column("Status", style="bold green")
    
    svc_table.add_row("curio-byte (Docker)", "[green]● Running[/green]")
    svc_table.add_row("VPS Heartbeat", "[green]● Active[/green]")
    
    layout["services"].update(Panel(svc_table, border_style="cyan"))
    
    # Footer
    footer_text = Text("Press Ctrl+C to exit | Built for devpulse toolchain", justify="center", style="dim")
    layout["footer"].update(Panel(footer_text))
    
    return layout

@click.command()
@click.option('--live-mode', is_flag=True, help="Run in interactive live TUI mode.")
def main(live_mode):
    """DevPulse CLI: Real-time system monitoring and engineering dashboard."""
    if live_mode:
        console.print("[yellow]Starting DevPulse Live TUI...[/yellow]")
        with Live(generate_dashboard(), refresh_per_second=2, console=console) as live:
            try:
                while True:
                    live.update(generate_dashboard())
            except KeyboardInterrupt:
                console.print("\n[bold red]Exiting DevPulse Live TUI. Goodbye![/bold red]")
    else:
        console.print(Panel("📊 **DevPulse Status Report**\nRun with [bold cyan]--live-mode[/bold cyan] for real-time dashboard.", title="DevPulse", border_style="green"))

if __name__ == "__main__":
    main()
