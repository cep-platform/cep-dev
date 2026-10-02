#!/usr/bin/env python3

import os
import subprocess
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from rich import print

load_dotenv()

API = "https://api.hetzner.cloud/v1"
TOKEN = os.environ["HCLOUD_TOKEN"]

SSH_KEY_NAME = "cep-local"
SSH_PUBLIC_KEY = Path.home() / ".ssh" / "id_ed25519.pub"
SSH_PRIVATE_KEY = Path.home() / ".ssh" / "id_ed25519"

EXPECTED_DEVELOPER_KEY = (
    "ssh-ed25519 "
    "AAAAC3NzaC1lZDI1NTE5AAAAICD6jKjzmbaiORhA9DHu3ieCE3AcdDoiKTCrosFlW+i6 "
    "sven@nixos"
)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


def ssh(ip, *command, timeout=5, check=False, input=None):
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
            f"root@{ip}",
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


def wait_for_ssh(ip, message, timeout=300):
    print(message)

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        result = ssh(ip, "true")

        if result.returncode == 0:
            print("SSH is ready.")
            return

        time.sleep(2)

    raise RuntimeError(f"Timed out waiting for SSH on {ip}")


def get_ssh_key(public_key):
    response = requests.get(
        f"{API}/ssh_keys",
        headers=headers,
        params={"name": SSH_KEY_NAME},
    )
    response.raise_for_status()

    keys = response.json()["ssh_keys"]

    for key in keys:
        if key["public_key"].strip() == public_key:
            return key

    if keys:
        raise RuntimeError(
            f"Hetzner SSH key {SSH_KEY_NAME!r} exists but contains "
            "a different public key"
        )

    response = requests.post(
        f"{API}/ssh_keys",
        headers=headers,
        json={
            "name": SSH_KEY_NAME,
            "public_key": public_key,
        },
    )
    response.raise_for_status()

    return response.json()["ssh_key"]


def create_server(ssh_key):
    response = requests.post(
        f"{API}/servers",
        headers=headers,
        json={
            "name": "cep-dev",
            "server_type": "cx23",
            "image": "ubuntu-22.04",
            "location": "nbg1",
            "ssh_keys": [ssh_key["id"]],
        },
    )
    response.raise_for_status()

    return response.json()["server"]


def boot_nixos_installer(ip):
    print("Booting NixOS installer...")

    script = r"""
set -eux

curl -L \
  https://github.com/nix-community/nixos-images/releases/latest/download/nixos-kexec-installer-noninteractive-x86_64-linux.tar.gz |
  tar -xzf- -C /root

/root/kexec/run
"""

    result = run_remote_script(
        ip,
        script,
        timeout=30,
    )

    # kexec intentionally terminates SSH.
    if result.returncode not in (0, 255):
        raise RuntimeError(
            f"kexec command failed with exit code {result.returncode}"
        )

    wait_for_ssh(
        ip,
        "Waiting for NixOS installer after kexec...",
    )


def install_nixos(ip):
    print("Installing cep-dev NixOS configuration...")

    script = r"""
set -eux

export PATH="/run/current-system/sw/bin:/run/wrappers/bin:/root/.nix-profile/bin:$PATH"

echo "Nix: $(command -v nix)"
echo "Nix version: $(nix --version)"

nix run 'github:nix-community/disko/latest#disko-install' -- \
  --flake 'github:cep-platform/cep-dev#cep-dev' \
  --disk main /dev/sda

reboot
"""

    result = run_remote_script(
        ip,
        script,
        timeout=30,
    )

    # Reboot intentionally terminates SSH.
    if result.returncode not in (0, 255):
        raise RuntimeError(
            f"NixOS installation failed with exit code {result.returncode}"
        )

    wait_for_ssh(
        ip,
        "Waiting for installed NixOS...",
    )


def main():
    if not SSH_PUBLIC_KEY.exists():
        raise SystemExit(
            f"SSH public key not found: {SSH_PUBLIC_KEY}"
        )

    public_key = SSH_PUBLIC_KEY.read_text().strip()

    if public_key != EXPECTED_DEVELOPER_KEY:
        raise SystemExit(
            "Local SSH public key does not match the developer key "
            "declared in cep-dev/modules/users.nix."
        )

    ssh_key = get_ssh_key(public_key)

    print(
        f"Using Hetzner SSH key: "
        f"{ssh_key['name']} ({ssh_key['id']})"
    )

    server = create_server(ssh_key)

    ip = server["public_net"]["ipv4"]["ip"]

    print(f"Created cep-dev: {ip}")

    wait_for_ssh(
        ip,
        "Waiting for initial SSH...",
    )

    print("Initial Ubuntu SSH works.")

    boot_nixos_installer(ip)

    install_nixos(ip)

    result = ssh(
        ip,
        "id",
        "developer",
        timeout=10,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Developer user was not created successfully"
        )

    print("NixOS is back.")
    print("cep-dev is ready.")
    print(f"SSH: ssh developer@{ip}")


if __name__ == "__main__":
    main()

