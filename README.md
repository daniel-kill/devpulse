# DevPulse ⚡

A high-performance Python CLI utility designed to audit workspace repositories, verify working tree statuses and GPG signatures, and provide real-time developer environment telemetry.

## Features

- **Workspace Audit (`devpulse audit`)**: Recursively scans development directories for Git repositories, detects dirty working trees, inspects detached HEADs, and verifies GPG commit signatures.
- **Resource & Service Monitor (`devpulse monitor`)**: Rich TUI dashboard tracking real-time CPU, RAM, disk utilization, and Docker container statuses.
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

## Usage

### 1. Repository Audit
Audit all git repositories in a workspace:
```bash
devpulse audit ~/Repos
```
Or verify against a specific GPG signing key fingerprint:
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

You can also run directly from the repository root:
```bash
python3 devpulse.py audit ~/Repos
python3 devpulse.py monitor --live
```
