import json
import os
from pathlib import Path
from typing import Any

import git
import typer
from rich.console import Console
from rich.table import Table

from devpulse.config import load_config

console = Console()

SKIP_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__",
    ".pytest_cache", ".ruff_cache", "target", "build", "dist"
}

def audit_repositories(
    path: str = typer.Argument(".", help="Root directory to scan for Git repositories."),
    gpg_key: str | None = typer.Option(
        None, "--gpg-key", help="Expected GPG fingerprint or key ID to verify against commit signatures."
    ),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: 'table' or 'json'."
    ),
):
    """Audit local Git repositories for status, uncommitted changes, and GPG signatures."""
    target_path = Path(path).resolve()

    if not target_path.exists():
        console.print(f"[red]Error: Path does not exist: {target_path}[/red]")
        raise typer.Exit(code=1)

    # Check config file fallback for gpg_key if not provided on CLI
    cfg = load_config()
    expected_gpg_key = gpg_key or cfg.get("audit", {}).get("default_gpg_key")

    repos_data: list[dict[str, Any]] = []

    for root, dirs, _files in os.walk(target_path):
        # Prune known heavy non-repo directories for fast traversal
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS or d == ".git"]

        if ".git" in dirs:
            repo_path = Path(root)
            repo_info: dict[str, Any] = {
                "name": repo_path.name,
                "path": str(repo_path),
                "branch": "UNKNOWN",
                "is_dirty": False,
                "gpg_signed": False,
                "gpg_verified": False,
                "last_commit": "",
                "error": None
            }

            try:
                repo = git.Repo(repo_path)
                branch_name = repo.active_branch.name if not repo.head.is_detached else "DETACHED"
                is_dirty = repo.is_dirty(untracked_files=True)
                head_commit = repo.head.commit
                has_sig = hasattr(head_commit, "gpgsig") and bool(head_commit.gpgsig)
                is_verified = False

                if has_sig and expected_gpg_key:
                    is_verified = expected_gpg_key.lower() in head_commit.gpgsig.lower()

                commit_msg = head_commit.message.strip().split("\n")[0]
                short_commit = commit_msg[:27] + "..." if len(commit_msg) > 30 else commit_msg

                repo_info["branch"] = branch_name
                repo_info["is_dirty"] = is_dirty
                repo_info["gpg_signed"] = has_sig
                repo_info["gpg_verified"] = is_verified
                repo_info["last_commit"] = commit_msg
                repo_info["short_commit"] = short_commit
            except (git.exc.GitError, OSError, ValueError) as e:
                repo_info["error"] = str(e)[:50]

            repos_data.append(repo_info)
            # Avoid traversing deeper into this repo's internals
            dirs.remove(".git")

    if format.lower() == "json":
        summary = {
            "workspace": str(target_path),
            "total_repositories": len(repos_data),
            "repositories": repos_data
        }
        typer.echo(json.dumps(summary, indent=2))
        return

    # Table output (default)
    console.print(f"\n[bold cyan]🔍 Scanning workspace:[/] {target_path}\n")

    if not repos_data:
        console.print("[yellow]No Git repositories found in this directory.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Repository", style="dim", width=25)
    table.add_column("Branch", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("GPG Signed", justify="center")
    table.add_column("Last Commit", style="green")

    for r in repos_data:
        if r["error"]:
            table.add_row(r["name"], "[red]Error[/red]", r["error"], "-", "-")
            continue

        status_str = "[yellow]⚠️  Modified[/yellow]" if r["is_dirty"] else "[green]✨ Clean[/green]"
        if r["gpg_verified"]:
            sig_str = "[bold green]Verified (Key Match)[/bold green]"
        elif r["gpg_signed"]:
            sig_str = "[green]Signed[/green]"
        else:
            sig_str = "[dim]Unverified/None[/dim]"

        table.add_row(
            r["name"],
            r["branch"],
            status_str,
            sig_str,
            r.get("short_commit", "")
        )

    console.print(table)
    console.print(f"\n[bold]Total Repositories Audited:[/] {len(repos_data)}\n")
