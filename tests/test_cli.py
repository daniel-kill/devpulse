import pytest
from typer.testing import CliRunner
from devpulse.cli import app
from devpulse import __version__

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "DevPulse" in result.stdout
    assert "audit" in result.stdout
    assert "monitor" in result.stdout

def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout

def test_audit_empty_directory(tmp_path):
    result = runner.invoke(app, ["audit", str(tmp_path)])
    assert result.exit_code == 0
    assert "No Git repositories found" in result.stdout

def test_audit_git_repository(tmp_path):
    import git
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
