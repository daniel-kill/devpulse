import shutil
import subprocess
import time

import psutil
import typer
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

def get_docker_status() -> list[tuple[str, str]]:
    """Probe local Docker daemon for running containers if docker CLI is available."""
    if not shutil.which("docker"):
        return [("Docker Engine", "[yellow]CLI not found[/yellow]")]
    try:
        proc = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}} ({{.Image}})|{{.Status}}"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2
        )
        if proc.returncode != 0:
            return [("Docker Daemon", "[red]● Inactive / Unreachable[/red]")]

        lines = [line.strip() for line in proc.stdout.strip().split("\n") if line.strip()]
        if not lines:
            return [("Docker Containers", "[dim]No active containers[/dim]")]

        results = []
        for line in lines[:6]:  # Show up to 6 containers
            parts = line.split("|", 1)
            name = parts[0]
            status = parts[1] if len(parts) > 1 else "Running"
            results.append((name, f"[green]● {status}[/green]"))
        return results
    except (subprocess.SubprocessError, OSError):
        return [("Docker Daemon", "[dim]Not probed[/dim]")]

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
    layout["body"].split_row(
        Layout(name="system"),
        Layout(name="services")
    )

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
    svc_table = Table(title="Services & Containers", expand=True)
    svc_table.add_column("Target", style="cyan")
    svc_table.add_column("Status", style="bold")

    for target, status in get_docker_status():
        svc_table.add_row(target, status)

    layout["services"].update(Panel(svc_table, border_style="cyan"))

    # Footer
    footer_text = Text("Press Ctrl+C to exit | Built for devpulse toolchain", justify="center", style="dim")
    layout["footer"].update(Panel(footer_text))

    return layout

def monitor_system(
    live: bool = typer.Option(False, "--live", "-l", help="Run interactive live-refreshing TUI dashboard.")
):
    """Display real-time system resource utilization and service health."""
    if live:
        console.print("[yellow]Starting DevPulse Live TUI...[/yellow]")
        with Live(generate_dashboard(), refresh_per_second=2, console=console) as live_view:
            try:
                while True:
                    live_view.update(generate_dashboard())
                    time.sleep(0.5)
            except KeyboardInterrupt:
                console.print("\n[bold red]Exiting DevPulse Live TUI. Goodbye![/bold red]")
    else:
        layout = generate_dashboard()
        console.print(layout)
        console.print("\n[dim]Tip: Use `devpulse monitor --live` for real-time dashboard.[/dim]\n")
