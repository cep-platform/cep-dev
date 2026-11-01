#!/usr/bin/env python3

"""Clone or update the repositories listed in repos.txt on the dev machine."""

import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API = "https://api.hetzner.cloud/v1"

SSH_PRIVATE_KEY = Path.home() / ".ssh" / "id_ed25519"
REPO_DIR = Path(__file__).resolve().parent
REPOS_FILE = REPO_DIR / "repos.txt"
REMOTE_USER = "developer"


def repo_name(url):
    name = url.rstrip("/").split("/")[-1]

    if name.endswith(".git"):
        name = name[: -len(".git")]

    if not name:
        raise SystemExit(f"Cannot derive repository name from URL: {url}")

    return name


def parse_repos():
    if not REPOS_FILE.exists():
        raise SystemExit(f"{REPOS_FILE} not found.")

    repos = []

    for line in REPOS_FILE.read_text().splitlines():
        url = line.split("#", 1)[0].strip()

        if not url:
            continue

        repos.append((repo_name(url), url))

    names = [name for name, _ in repos]

    if len(names) != len(set(names)):
        raise SystemExit(f"{REPOS_FILE} lists two repositories with the same name.")

    return repos


def build_script(repos):
    entries = "\n".join(f"{name} {url}" for name, url in repos)

    return f"""set -u
status=0
while read -r name url; do
    if [ -d "$HOME/$name/.git" ]; then
        echo "==> $name: git pull --ff-only"
        git -C "$HOME/$name" pull --ff-only || status=1
    else
        echo "==> $name: git clone"
        git clone "$url" "$HOME/$name" || status=1
    fi
done <<EOF
{entries}
EOF
exit $status"""


def find_server_ip():
    token = os.environ["HCLOUD_TOKEN"]

    response = requests.get(
        f"{API}/servers",
        headers={"Authorization": f"Bearer {token}"},
        params={"name": "cep-dev"},
    )
    response.raise_for_status()

    servers = response.json()["servers"]

    if not servers:
        raise SystemExit("No server named 'cep-dev' found.")

    return servers[0]["public_net"]["ipv4"]["ip"]


def sync(host, user=REMOTE_USER):
    repos = parse_repos()

    if not repos:
        print("No repositories listed in repos.txt.")
        return

    print(f"Syncing repositories to {user}@{host}...")

    result = subprocess.run(
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
            f"{user}@{host}",
            "bash",
            "-s",
        ],
        input=build_script(repos),
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Repository sync failed with exit code {result.returncode}")


def main():
    if len(sys.argv) > 2:
        raise SystemExit(
            f"Usage: {sys.argv[0]} [user@host]\n"
            f"       Without arguments, finds the Hetzner server named 'cep-dev'."
        )

    target = sys.argv[1] if len(sys.argv) == 2 else find_server_ip()

    user, _, host = target.rpartition("@")
    user = user or REMOTE_USER

    sync(host, user)

    print("Done.")
    print(f"Connect with: ssh {user}@{host}")


if __name__ == "__main__":
    main()
