import shutil
import subprocess
import time
from typing import Any

import psutil
import typer
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from devpulse.config import load_config

console = Console()

def get_docker_status(custom_services: list[str] | None = None) -> list[tuple[str, str]]:
    """Probe local Docker daemon for running containers and check custom services."""
    results: list[tuple[str, str]] = []

    if not shutil.which("docker"):
        results.append(("Docker Engine", "[yellow]CLI not found[/yellow]"))
    else:
        try:
            proc = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}} ({{.Image}})|{{.Status}}"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2
            )
            if proc.returncode != 0:
                results.append(("Docker Daemon", "[red]● Inactive / Unreachable[/red]"))
            else:
                lines = [line.strip() for line in proc.stdout.strip().split("\n") if line.strip()]
                if not lines:
                    results.append(("Docker Containers", "[dim]No active containers[/dim]"))
                else:
                    for line in lines[:6]:  # Show up to 6 containers
                        parts = line.split("|", 1)
                        name = parts[0]
                        status = parts[1] if len(parts) > 1 else "Running"
                        results.append((name, f"[green]● {status}[/green]"))
        except (subprocess.SubprocessError, OSError):
            results.append(("Docker Daemon", "[dim]Not probed[/dim]"))

    return results

def generate_dashboard() -> Layout:
    cfg = load_config()
    monitored_paths = cfg.get("monitor", {}).get("monitored_paths", ["/"])

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

    sys_table.add_row("CPU Load", f"{cpu_pct}%")
    sys_table.add_row("Memory Used", f"{mem.percent}% ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)")

    for path in monitored_paths:
        try:
            d = psutil.disk_usage(path)
            label = f"Disk ({path})" if len(monitored_paths) > 1 else "Disk Usage"
            sys_table.add_row(label, f"{d.percent}% ({d.used // (1024**3)}GB / {d.total // (1024**3)}GB)")
        except Exception:
            pass

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
    """Monitor local system resources, disk paths, and Docker container health."""
    if live:
        console.print("[yellow]Starting DevPulse Live TUI...[/yellow]")
        with Live(generate_dashboard(), refresh_per_second=2, console=console) as live_view:
            try:
                while True:
                    time.sleep(0.5)
                    live_view.update(generate_dashboard())
            except KeyboardInterrupt:
                console.print("\n[bold red]Exiting DevPulse Live TUI. Goodbye![/bold red]")
    else:
        # One-shot snapshot
        console.print(generate_dashboard())
