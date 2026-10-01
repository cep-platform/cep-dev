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

ssh_pubkey = Path.home() / ".ssh" / "id_ed25519.pub"
ssh_private_key = Path.home() / ".ssh" / "id_ed25519"

public_key = ssh_pubkey.read_text().strip()

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


def ssh(ip, *command, timeout=5):
    return subprocess.run(
        [
            "ssh",
            "-i", str(ssh_private_key),
            "-o", "BatchMode=yes",
            "-o", f"ConnectTimeout={timeout}",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            f"root@{ip}",
            *command,
        ],
        check=False,
    )


def get_ssh_key():
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
            f"Hetzner SSH key {SSH_KEY_NAME!r} exists "
            "but contains a different public key"
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
            "name": "cep-test",
            "server_type": "cx23",
            "image": "ubuntu-22.04",
            "location": "nbg1",
            "ssh_keys": [ssh_key["id"]],
        },
    )
    response.raise_for_status()

    return response.json()["server"]


def wait_for_ssh(ip, message):
    print(message)

    while True:
        result = ssh(ip, "true")

        if result.returncode == 0:
            print("SSH is ready.")
            return

        time.sleep(2)


def boot_nixos_installer(ip):
    print("Booting NixOS installer...")

    command = """
curl -L https://github.com/nix-community/nixos-images/releases/latest/download/nixos-kexec-installer-noninteractive-x86_64-linux.tar.gz |
  tar -xzf- -C /root &&
/root/kexec/run
"""

    # The machine disappears while kexec'ing, so don't treat the
    # resulting SSH error as a failure.
    ssh(ip, "sh", "-c", command, timeout=10)

    print("Waiting for machine to come back...")

    # The original SSH connection is expected to die during kexec.
    wait_for_ssh(ip, "Polling for NixOS installer SSH...")


def main():
    ssh_key = get_ssh_key()
    print(f"Using Hetzner SSH key: {ssh_key['name']} ({ssh_key['id']})")

    server = create_server(ssh_key)
    ip = server["public_net"]["ipv4"]["ip"]

    print(f"Created {server['name']}: {ip}")

    wait_for_ssh(ip, "Waiting for initial SSH...")
    
    print("Initial SSH connection works.")

    boot_nixos_installer(ip)

    print("Running command in NixOS installer:")
    result = ssh(ip, "echo", "hello world", timeout=10)

    if result.returncode != 0:
        raise RuntimeError("SSH connection to NixOS installer failed")


if __name__ == "__main__":
    main()
