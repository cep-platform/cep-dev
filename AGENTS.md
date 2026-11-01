# AGENTS.md

## Overview

Tooling to create and delete a NixOS development VPS (`cep-dev`) on Hetzner Cloud. NixOS is installed remotely with nixos-anywhere from the flake in this repo.

## Structure

- `create_vps.py` — creates the Hetzner server, injects the given SSH public key into `modules/users.nix`, then installs NixOS via nixos-anywhere
- `delete_vps.py` — finds and deletes the server named `cep-dev` (asks for confirmation)
- `copy_repo.py` — finds the server named `cep-dev` and copies this repository to `~/cep-dev` on it (tar over SSH; excludes `.env`, `.venv`, `__pycache__`, `result`)
- `modules/` — NixOS modules composing the flake output `#cep-dev`
- `flake.nix` — NixOS configuration for the dev instance

## Commands

Install dependencies (Python 3.13, managed with uv):

```
uv sync
```

Create the VPS:

```
uv run create_vps.py "$(cat ~/.ssh/id_ed25519.pub)"
```

Delete the VPS:

```
uv run delete_vps.py
```

Copy the repository to the VPS (for continuing cep-dev development on it):

```
uv run copy_repo.py
```

Build/check the NixOS configuration:

```
nix build .#nixosConfigurations.cep-dev.config.system.build.toplevel
```

## Notes

- `HCLOUD_TOKEN` lives in `.env` (gitignored); never commit secrets
- Scripts expect an SSH key pair at `~/.ssh/id_ed25519`
- Keep changes minimal and consistent with the existing simple script style