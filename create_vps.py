#!/usr/bin/env python3

import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from rich import print

load_dotenv()

API = "https://api.hetzner.cloud/v1"
TOKEN = os.environ["HCLOUD_TOKEN"]

SSH_KEY_NAME = "cep-local"
SSH_PRIVATE_KEY = Path.home() / ".ssh" / "id_ed25519"
REPO_DIR = Path(__file__).resolve().parent
FLAKE = f"{REPO_DIR}#cep-dev"
USERS_NIX = REPO_DIR / "modules" / "users.nix"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


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


def install_nixos(ip):
    print("Installing NixOS with nixos-anywhere...")

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
            f"root@{ip}",
        ],
        cwd=REPO_DIR,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"nixos-anywhere failed with exit code {result.returncode}"
        )


def get_ssh_key(public_key):
    response = requests.get(
        f"{API}/ssh_keys",
        headers=headers,
        params={"name": SSH_KEY_NAME},
    )
    response.raise_for_status()

    keys = response.json()["ssh_keys"]

    if keys:
        key = keys[0]

        if key["public_key"].strip() == public_key:
            return key

        response = requests.delete(
            f"{API}/ssh_keys/{key['id']}",
            headers=headers,
        )
        response.raise_for_status()

        print(f"Overwrote Hetzner SSH key: {SSH_KEY_NAME}")

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


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: {sys.argv[0]} <ssh-public-key>")

    public_key = sys.argv[1].strip()

    format_users_nix(public_key)

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

    install_nixos(ip)

    wait_for_ssh(ip, "Waiting for NixOS to boot...", user="developer")

    print("NixOS is up.")
    print(f"Connect with: ssh developer@{ip}")


if __name__ == "__main__":
    main()

