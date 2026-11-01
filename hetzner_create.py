#!/usr/bin/env python3

"""Create the Hetzner Cloud server for cep-dev (without installing NixOS)."""

import os
import sys

import requests
from dotenv import load_dotenv
from rich import print

from ssh_deploy import wait_for_ssh

load_dotenv()

API = "https://api.hetzner.cloud/v1"
TOKEN = os.environ["HCLOUD_TOKEN"]

SSH_KEY_NAME = "cep-local"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


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


def create(public_key):
    """Register the SSH key, create the server, wait for SSH, return its IP."""
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

    return ip


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: {sys.argv[0]} <ssh-public-key>")

    public_key = sys.argv[1].strip()

    ip = create(public_key)

    print(f"Connect with: ssh root@{ip}")
    print(f"Deploy NixOS with: make ssh_deploy HOST=root@{ip}")


if __name__ == "__main__":
    main()
