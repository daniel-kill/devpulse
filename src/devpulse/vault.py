"""env-vault: Secure local-to-remote environment variable synchronization.

Supports encrypting, exporting, and syncing .env files with remote hosts or cloud targets.
"""

import os
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

console = Console()
vault_app = typer.Typer(
    name="env-vault",
    help="🔒 Secure local-to-remote environment variable synchronization & inspection.",
    add_completion=False
)

@vault_app.command("inspect")
def inspect_env(
    env_file: Path = typer.Argument(Path(".env"), help="Path to .env file to inspect.")
):
    """Safely inspect environment variables without exposing sensitive secret values."""
    if not env_file.exists():
        console.print(f"[red]Error: Environment file not found:[/] {env_file}")
        raise typer.Exit(code=1)

    table = Table(title=f"Environment Variables ({env_file.name})", show_header=True)
    table.add_column("Key", style="bold cyan")
    table.add_column("Status / Length", style="green")
    table.add_column("Masked Preview", style="dim")

    count = 0
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                count += 1
                length = len(val)
                masked = (val[:2] + "*" * (length - 4) + val[-2:]) if length > 4 else "****"
                table.add_row(key, f"{length} chars", masked)

    console.print(table)
    console.print(f"\n[bold]Total Variables Inspected:[/] {count}\n")

@vault_app.command("sync")
def sync_env(
    source: Path = typer.Argument(Path(".env"), help="Local .env file path."),
    target_host: str = typer.Argument(..., help="Remote host target (e.g. user@host:/path/.env or ssh alias)."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview sync actions without making changes.")
):
    """Sync an environment file to a remote server over SSH/SCP."""
    if not source.exists():
        console.print(f"[red]Error: Source file not found:[/] {source}")
        raise typer.Exit(code=1)

    if dry_run:
        console.print(f"[yellow][DRY RUN][/yellow] Would sync [bold cyan]{source}[/] to [bold green]{target_host}[/]")
        return

    import subprocess
    cmd = ["scp", str(source), target_host]
    console.print(f"Syncing {source} -> {target_host}...")
    proc = subprocess.run(cmd)
    if proc.returncode == 0:
        console.print("[green]✔ Environment successfully synced.[/green]")
    else:
        console.print(f"[red]❌ Sync failed with exit code {proc.returncode}[/red]")
        raise typer.Exit(code=proc.returncode)
