#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
import git

app = typer.Typer(help="DevPulse — Inspect workspace health, git status, and GPG signing across repositories.")
console = Console()

TARGET_GPG_KEY = "E453F9AEC380D33E4BA7FAC69B542AA270F867E5"

@app.command()
def audit(
    path: str = typer.Argument(".", help="Root directory to scan for Git repositories.")
):
    """Audit local Git repositories for status, uncommitted changes, and GPG signatures."""
    target_path = Path(path).resolve()
    
    if not target_path.exists():
        console.print(f"[red]Error: Path does not exist: {target_path}[/red]")
        raise typer.Exit(code=1)

    console.print(f"\n[bold cyan]🔍 Scanning workspace:[/] {target_path}\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Repository", style="dim", width=25)
    table.add_column("Branch", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("GPG Signed", justify="center")
    table.add_column("Last Commit", style="green")

    repo_count = 0

    # Find directories containing a .git folder
    for root, dirs, files in os.walk(target_path):
        if ".git" in dirs:
            repo_path = Path(root)
            repo_count += 1
            
            try:
                repo = git.Repo(repo_path)
                branch_name = repo.active_branch.name if not repo.head.is_detached else "DETACHED"
                
                # Check dirty working tree
                is_dirty = repo.is_dirty(untracked_files=True)
                status_str = "[yellow]⚠️  Modified[/yellow]" if is_dirty else "[green]✨ Clean[/green]"

                # Check latest commit GPG signature
                head_commit = repo.head.commit
                has_sig = hasattr(head_commit, "gpgsig") and bool(head_commit.gpgsig)
                signature_status = "[green]Signed[/green]" if has_sig else "[dim]Unverified/None[/dim]"
                
                commit_msg = head_commit.message.strip().split("\n")[0]
                if len(commit_msg) > 30:
                    commit_msg = commit_msg[:27] + "..."

                table.add_row(
                    repo_path.name,
                    branch_name,
                    status_str,
                    signature_status,
                    f"{commit_msg}"
                )
            except Exception as e:
                table.add_row(repo_path.name, "[red]Error[/red]", str(e)[:30], "-", "-")
            
            # Don't recurse into submodules/nested .git repos for this scan
            dirs.remove(".git")

    if repo_count == 0:
        console.print("[yellow]No Git repositories found in this directory.[/yellow]")
    else:
        console.print(table)
        console.print(f"\n[bold]Total Repositories Audited:[/] {repo_count}\n")

if __name__ == "__main__":
    app()
