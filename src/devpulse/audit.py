import os
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
import git

console = Console()

SKIP_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__",
    ".pytest_cache", ".ruff_cache", "target", "build", "dist"
}

def audit_repositories(
    path: str = typer.Argument(".", help="Root directory to scan for Git repositories."),
    gpg_key: Optional[str] = typer.Option(
        None, "--gpg-key", help="Expected GPG fingerprint or key ID to verify against commit signatures."
    ),
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

    for root, dirs, files in os.walk(target_path):
        # Prune known heavy non-repo directories for fast traversal
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS or d == ".git"]

        if ".git" in dirs:
            repo_path = Path(root)
            repo_count += 1

            try:
                repo = git.Repo(repo_path)
                branch_name = repo.active_branch.name if not repo.head.is_detached else "DETACHED"

                is_dirty = repo.is_dirty(untracked_files=True)
                status_str = "[yellow]⚠️  Modified[/yellow]" if is_dirty else "[green]✨ Clean[/green]"

                head_commit = repo.head.commit
                has_sig = hasattr(head_commit, "gpgsig") and bool(head_commit.gpgsig)

                if has_sig:
                    if gpg_key and gpg_key.lower() in head_commit.gpgsig.lower():
                        sig_str = "[bold green]Verified (Key Match)[/bold green]"
                    else:
                        sig_str = "[green]Signed[/green]"
                else:
                    sig_str = "[dim]Unverified/None[/dim]"

                commit_msg = head_commit.message.strip().split("\n")[0]
                if len(commit_msg) > 30:
                    commit_msg = commit_msg[:27] + "..."

                table.add_row(
                    repo_path.name,
                    branch_name,
                    status_str,
                    sig_str,
                    f"{commit_msg}"
                )
            except Exception as e:
                table.add_row(repo_path.name, "[red]Error[/red]", str(e)[:30], "-", "-")

            # Avoid traversing deeper into this repo's internals
            dirs.remove(".git")

    if repo_count == 0:
        console.print("[yellow]No Git repositories found in this directory.[/yellow]")
    else:
        console.print(table)
        console.print(f"\n[bold]Total Repositories Audited:[/] {repo_count}\n")
