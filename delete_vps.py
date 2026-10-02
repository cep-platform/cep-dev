#!/usr/bin/env python3

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API = "https://api.hetzner.cloud/v1"
TOKEN = os.environ["HCLOUD_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
}


def main():
    response = requests.get(
        f"{API}/servers",
        headers=HEADERS,
        params={"name": "cep-dev"},
    )
    response.raise_for_status()

    servers = response.json()["servers"]

    if not servers:
        print("No server named 'cep-dev' found.")
        return

    for server in servers:
        print(
            f"Found {server['name']} "
            f"(id={server['id']}, ip={server['public_net']['ipv4']['ip']})"
        )

    answer = input("Delete this server? [y/N] ").strip().lower()
    if answer != "y":
        print("Aborted.")
        return

    for server in servers:
        response = requests.delete(
            f"{API}/servers/{server['id']}",
            headers=HEADERS,
        )
        response.raise_for_status()
        print(f"Deleted {server['name']} (id={server['id']}).")


if __name__ == "__main__":
    main()
