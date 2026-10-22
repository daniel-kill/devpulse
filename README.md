# DevPulse ⚡

A high-performance Python CLI utility designed to audit workspace repositories, verify working tree statuses and GPG signatures, manage environment synchronization, and provide real-time developer environment telemetry.

## Features

- **Workspace Audit (`devpulse audit`)**: Recursively scans development directories for Git repositories, detects dirty working trees, inspects detached HEADs, and verifies GPG commit signatures.
  - Supports `--format json` for automated CI/CD pipeline integration and programmatic inspection.
- **Resource & Service Monitor (`devpulse monitor`)**: Rich TUI dashboard tracking real-time CPU, RAM, disk utilization across custom mount points, and Docker container health.
- **Environment Vault (`devpulse vault`)**: Secure local-to-remote `.env` synchronization and safe terminal inspection without leaking secret values.
- **Config File Support**: Automatically loads custom preferences (default GPG keys, monitored disk paths, service probes) from `~/.config/devpulse/config.toml`.
- **Modern Packaging**: Ready for installation via `pip` or compilation into standalone binaries via PyInstaller.

## Requirements

- Python 3.10+
- `typer`, `rich`, `GitPython`, `psutil`

## Installation

### From Source (Editable Mode)
```bash
git clone https://github.com/daniel-kill/devpulse.git
cd devpulse
pip install -e .
```

Or install dependencies into your active virtual environment:
```bash
pip install -r requirements.txt
```

## Configuration

DevPulse automatically reads settings from `~/.config/devpulse/config.toml` if present. Copy the example file:

```bash
mkdir -p ~/.config/devpulse
cp devpulse.config.example.toml ~/.config/devpulse/config.toml
```

Example configuration (`~/.config/devpulse/config.toml`):
```toml
[audit]
default_gpg_key = "E453F9AEC380D33E4BA7FAC69B542AA270F867E5"

[monitor]
monitored_paths = ["/"]
services = ["curio-byte", "docker"]
```

## Usage

### 1. Repository Audit
Audit all git repositories in a workspace:
```bash
devpulse audit ~/Repos
```
Export structured JSON for CI/CD pipelines:
```bash
devpulse audit ~/Repos --format json
```
Verify against a specific GPG signing key fingerprint:
```bash
devpulse audit ~/Repos --gpg-key E453F9AEC380D33E4BA7FAC69B542AA270F867E5
```

### 2. System & Container Monitor
One-shot status snapshot:
```bash
devpulse monitor
```

Interactive, live-refreshing TUI dashboard:
```bash
devpulse monitor --live
```

### 3. Environment Vault
Safely inspect `.env` variables without exposing secrets:
```bash
devpulse vault inspect .env
```

Sync local `.env` to a remote server over SSH/SCP:
```bash
# Preview changes with dry-run
devpulse vault sync .env srv1752914:/var/www/.env --dry-run

# Execute sync
devpulse vault sync .env srv1752914:/var/www/.env
```
