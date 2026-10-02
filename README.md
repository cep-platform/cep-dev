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