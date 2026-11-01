#!/usr/bin/env python3

"""Install the cep-dev NixOS configuration on any SSH-reachable host."""

import re
import subprocess
import sys
import time
from pathlib import Path

from repos_sync import sync

SSH_PRIVATE_KEY = Path.home() / ".ssh" / "id_ed25519"
SSH_PUBLIC_KEY = SSH_PRIVATE_KEY.with_suffix(".pub")
REPO_DIR = Path(__file__).resolve().parent
FLAKE = f"{REPO_DIR}#cep-dev"
USERS_NIX = REPO_DIR / "modules" / "users.nix"


def ssh(ip, *command, timeout=5, check=False, input=None, user="root"):
    return subprocess.run(
        [
            "ssh",
            "-i",
            str(SSH_PRIVATE_KEY),
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={timeout}",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            f"{user}@{ip}",
            *command,
        ],
        input=input,
        text=True,
        check=check,
    )


def run_remote_script(ip, script, timeout=30):
    return ssh(
        ip,
        "bash",
        timeout=timeout,
        input=script,
    )


def wait_for_ssh(ip, message, timeout=300, user="root"):
    print(message)

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        result = ssh(ip, "true", user=user)

        if result.returncode == 0:
            print("SSH is ready.")
            return

        time.sleep(2)

    raise RuntimeError(f"Timed out waiting for SSH on {ip}")


def format_users_nix(public_key):
    content = USERS_NIX.read_text()
    print(content)

    content, count = re.subn(
        r'"ssh-\S+[^"]*"',
        f'"{public_key}"',
        content,
    )

    print(content)
    if count != 1:
        raise RuntimeError(
            f"Expected exactly one SSH key in {USERS_NIX}, found {count}"
        )

    USERS_NIX.write_text(content)


def normalize_target(host):
    if "@" in host:
        return host

    return f"root@{host}"


def install_nixos(target):
    target = normalize_target(target)

    print(f"Installing NixOS with nixos-anywhere on {target}...")

    result = subprocess.run(
        [
            "nix",
            "run",
            "github:nix-community/nixos-anywhere",
            "--",
            "--flake",
            FLAKE,
            "-i",
            str(SSH_PRIVATE_KEY),
            "--target-host",
            target,
        ],
        cwd=REPO_DIR,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"nixos-anywhere failed with exit code {result.returncode}"
        )


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit(
            f"Usage: {sys.argv[0]} <user@host> [ssh-public-key]\n"
            f"       ssh-public-key defaults to {SSH_PUBLIC_KEY}"
        )

    target = normalize_target(sys.argv[1])
    user, _, ip = target.rpartition("@")

    public_key = (
        sys.argv[2] if len(sys.argv) == 3 else SSH_PUBLIC_KEY.read_text()
    ).strip()

    format_users_nix(public_key)

    wait_for_ssh(ip, "Waiting for SSH...", user=user)

    install_nixos(target)

    wait_for_ssh(ip, "Waiting for NixOS to boot...", user="developer")

    sync(ip)

    print("NixOS is up.")
    print(f"Connect with: ssh developer@{ip}")


if __name__ == "__main__":
    main()
