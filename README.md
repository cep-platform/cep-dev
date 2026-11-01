# cep-dev

Spins up a NixOS development VPS on Hetzner Cloud using [nixos-anywhere](https://github.com/nix-community/nixos-anywhere).

## Prerequisites

- A Hetzner Cloud API token
- An SSH key pair at `~/.ssh/id_ed25519`
- [uv](https://docs.astral.sh/uv/) and [Nix](https://nix.dev/) installed

## Setup

1. Copy `.env.example` to `.env` and fill in your token:

   ```
   cp .env.example .env
   ```

2. Install Python dependencies:

   ```
   uv sync
   ```

## Usage

Create a server (installs NixOS from the flake in this repo):

```
uv run create_vps.py "$(cat ~/.ssh/id_ed25519.pub)"
```

When finished, the script prints the server's IP. Connect with:

```
ssh developer@<ip>
```

Delete the server when you're done:

```
uv run delete_vps.py
```

## Developing cep-dev on the VPS

Copy the repository onto the VPS to continue developing cep-dev there:

```
uv run copy_repo.py
```

The script finds the server named `cep-dev` via the API and streams the repository to `~/cep-dev` on the target using tar over SSH. `.git` is included, so it arrives as a working repository; `.env`, `.venv`, `__pycache__`, and `result` are excluded. Re-running it overwrites changed files.

Once on the VPS, set up the Python environment:

```
ssh developer@<ip>
cd ~/cep-dev
uv sync
```

To run `create_vps.py`/`delete_vps.py` from the VPS, copy `.env` over manually:

```
scp -i ~/.ssh/id_ed25519 .env developer@<ip>:~/cep-dev/.env
```
