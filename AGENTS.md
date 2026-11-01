# AGENTS.md

## Overview

Tooling to create and delete a NixOS development VPS (`cep-dev`) on Hetzner Cloud. NixOS is installed remotely with nixos-anywhere from the flake in this repo.

## Structure

- `ssh_deploy.py` — generic SSH deployment: installs the NixOS configuration on any SSH-reachable host via nixos-anywhere (root required); also holds the shared SSH/deploy helpers used by `create_vps.py` and `hetzner_create.py`
- `hetzner_create.py` — Hetzner part: registers the SSH key with the Hetzner API, creates the server named `cep-dev`, and waits for its SSH (no NixOS install)
- `create_vps.py` — end-to-end Hetzner deploy: injects the SSH key into `modules/users.nix`, creates the server via `hetzner_create.py`, then installs NixOS
- `delete_vps.py` — finds and deletes the server named `cep-dev` (asks for confirmation)
- `copy_repo.py` — finds the server named `cep-dev` and copies this repository to `~/cep-dev` on it (tar over SSH; excludes `.env`, `.venv`, `__pycache__`, `result`)
- `repos_sync.py` — clones/pulls the repositories listed in `repos.txt` onto the VPS as `developer` (runs automatically at the end of every deploy)
- `repos.txt` — list of git URLs to clone onto the machine, one per line
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

Create the Hetzner VPS only (no NixOS install; deploy later with `make ssh_deploy HOST=root@<ip>`):

```
make hetzner_create
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

Clone/update the repositories listed in `repos.txt` on the VPS:

```
make repos_sync
```

Build/check the NixOS configuration:

```
nix build .#nixosConfigurations.cep-dev.config.system.build.toplevel
```

## Notes

- `HCLOUD_TOKEN` lives in `.env` (gitignored); never commit secrets
- Scripts expect an SSH key pair at `~/.ssh/id_ed25519`
- Keep changes minimal and consistent with the existing simple script style
