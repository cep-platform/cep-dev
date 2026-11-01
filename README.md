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

All operations are available as Makefile targets; run `make help` for an overview:

```
make help
```

### Hetzner

Deploy (create the Hetzner server and install NixOS from the flake in this repo):

```
make hetzner_deploy
```

When finished, the script prints the server's IP. Connect with:

```
ssh developer@<ip>
```

Destroy (delete the server when you're done):

```
make hetzner_destroy
```

### Any SSH host

Deploy NixOS to a machine reachable over SSH (root access required; the target must be a running Linux system):

```
make ssh_deploy HOST=root@<ip>
```

Each target wraps a standalone script (`ssh_deploy.py`, `create_vps.py`, `delete_vps.py`, `copy_repo.py`) that can also be run directly with `uv run`.

## Developing cep-dev on the VPS

Copy the repository onto the VPS to continue developing cep-dev there:

```
make copy_repo
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
