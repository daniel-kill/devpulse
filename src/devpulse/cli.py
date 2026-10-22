import typer

from devpulse import __version__
from devpulse.audit import audit_repositories
from devpulse.monitor import monitor_system
from devpulse.vault import vault_app

app = typer.Typer(
    name="devpulse",
    help="⚡ DevPulse: Workspace security & Git auditing, system resource telemetry, and developer health CLI.",
    add_completion=False
)

app.command("audit")(audit_repositories)
app.command("monitor")(monitor_system)
app.add_typer(vault_app, name="vault")

def version_callback(value: bool):
    if value:
        typer.echo(f"DevPulse CLI v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Show DevPulse version and exit."
    )
):
    pass

if __name__ == "__main__":
    app()
