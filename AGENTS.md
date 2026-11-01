# AGENTS.md

## Overview

Tooling to create and delete a NixOS development VPS (`cep-dev`) on Hetzner Cloud. NixOS is installed remotely with nixos-anywhere from the flake in this repo.

## Structure

- `ssh_deploy.py` — generic SSH deployment: installs the NixOS configuration on any SSH-reachable host via nixos-anywhere (root required); also holds the shared SSH/deploy helpers used by `create_vps.py`
- `create_vps.py` — Hetzner part of the deploy: registers the SSH key with the Hetzner API, creates the server named `cep-dev`, then hands off to `ssh_deploy.py`
- `delete_vps.py` — finds and deletes the server named `cep-dev` (asks for confirmation)
- `copy_repo.py` — finds the server named `cep-dev` and copies this repository to `~/cep-dev` on it (tar over SSH; excludes `.env`, `.venv`, `__pycache__`, `result`)
- `Makefile` — convenience targets wrapping the scripts
- `modules/` — NixOS modules composing the flake output `#cep-dev`
- `flake.nix` — NixOS configuration for the dev instance

## Commands

Install dependencies (Python 3.13, managed with uv):

```
uv sync
```

Deploy to Hetzner (create the server and install NixOS):

```
make hetzner_deploy
```

Delete the Hetzner VPS:

```
make hetzner_destroy
```

Deploy NixOS to any SSH host:

```
make ssh_deploy HOST=root@<ip>
```

Copy the repository to the VPS (for continuing cep-dev development on it):

```
make copy_repo
```

Build/check the NixOS configuration:

```
nix build .#nixosConfigurations.cep-dev.config.system.build.toplevel
```

## Notes

- `HCLOUD_TOKEN` lives in `.env` (gitignored); never commit secrets
- Scripts expect an SSH key pair at `~/.ssh/id_ed25519`
- Keep changes minimal and consistent with the existing simple script style
