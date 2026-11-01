#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API = "https://api.hetzner.cloud/v1"
TOKEN = os.environ["HCLOUD_TOKEN"]

SSH_PRIVATE_KEY = Path.home() / ".ssh" / "id_ed25519"
REPO_DIR = Path(__file__).resolve().parent
REMOTE_USER = "developer"
REMOTE_DIR = "cep-dev"

EXCLUDES = [".env", ".venv", "__pycache__", "result"]


def find_server_ip():
    response = requests.get(
        f"{API}/servers",
        headers={"Authorization": f"Bearer {TOKEN}"},
        params={"name": "cep-dev"},
    )
    response.raise_for_status()

    servers = response.json()["servers"]

    if not servers:
        raise SystemExit("No server named 'cep-dev' found.")

    return servers[0]["public_net"]["ipv4"]["ip"]


def copy_repo(ip):
    tar = subprocess.Popen(
        [
            "tar",
            "czf",
            "-",
            *[f"--exclude={pattern}" for pattern in EXCLUDES],
            "-C",
            str(REPO_DIR),
            ".",
        ],
        stdout=subprocess.PIPE,
    )

    ssh = subprocess.run(
        [
            "ssh",
            "-i",
            str(SSH_PRIVATE_KEY),
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=10",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            f"{REMOTE_USER}@{ip}",
            f"mkdir -p {REMOTE_DIR} && tar xzf - -C {REMOTE_DIR}",
        ],
        stdin=tar.stdout,
    )

    tar.stdout.close()
    tar.wait()

    if tar.returncode != 0:
        raise RuntimeError(f"tar failed with exit code {tar.returncode}")

    if ssh.returncode != 0:
        raise RuntimeError(f"ssh failed with exit code {ssh.returncode}")


def main():
    ip = find_server_ip()

    print(f"Copying repository to {REMOTE_USER}@{ip}:~/{REMOTE_DIR}...")

    copy_repo(ip)

    print("Done.")
    print(f"Connect with: ssh {REMOTE_USER}@{ip}")

    if (REPO_DIR / ".env").exists():
        print(
            "Note: .env was not copied (contains HCLOUD_TOKEN). "
            f"Copy it manually if needed: "
            f"scp -i {SSH_PRIVATE_KEY} {REPO_DIR}/.env "
            f"{REMOTE_USER}@{ip}:~/{REMOTE_DIR}/.env"
        )


if __name__ == "__main__":
    main()
