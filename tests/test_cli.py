import json

import git
from typer.testing import CliRunner

from devpulse import __version__
from devpulse.cli import app

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "DevPulse" in result.stdout
    assert "audit" in result.stdout
    assert "monitor" in result.stdout
    assert "vault" in result.stdout

def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout

def test_audit_empty_directory(tmp_path):
    result = runner.invoke(app, ["audit", str(tmp_path)])
    assert result.exit_code == 0
    assert "No Git repositories found" in result.stdout

def test_audit_json_format(tmp_path):
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    repo = git.Repo.init(repo_dir)

    test_file = repo_dir / "sample.txt"
    test_file.write_text("hello devpulse")
    repo.index.add(["sample.txt"])
    repo.index.commit("Initial commit for testing")

    result = runner.invoke(app, ["audit", str(tmp_path), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total_repositories"] == 1
    assert data["repositories"][0]["name"] == "test_repo"
    assert data["repositories"][0]["branch"] in ("main", "master")

def test_audit_git_repository(tmp_path):
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    repo = git.Repo.init(repo_dir)

    # Create and commit a file
    test_file = repo_dir / "sample.txt"
    test_file.write_text("hello devpulse")
    repo.index.add(["sample.txt"])
    repo.index.commit("Initial commit for testing")

    result = runner.invoke(app, ["audit", str(tmp_path)])
    assert result.exit_code == 0
    assert "test_repo" in result.stdout
    assert "Total Repositories Audited: 1" in result.stdout

def test_monitor_snapshot():
    result = runner.invoke(app, ["monitor"])
    assert result.exit_code == 0
    assert "System Resource Utilization" in result.stdout
    assert "CPU Load" in result.stdout

def test_vault_inspect(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=secret_key_12345\nDEBUG=true\n")
    result = runner.invoke(app, ["vault", "inspect", str(env_file)])
    assert result.exit_code == 0
    assert "API_KEY" in result.stdout
    assert "DEBUG" in result.stdout
    assert "secret_key_12345" not in result.stdout  # Ensure value is masked

def test_vault_sync_dry_run(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\n")
    result = runner.invoke(
        app,
        ["vault", "sync", "user@remote:/app/.env", "--source", str(env_file), "--dry-run"],
    )
    assert result.exit_code == 0
    assert "[DRY RUN]" in result.stdout
