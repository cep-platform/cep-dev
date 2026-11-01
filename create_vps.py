#!/usr/bin/env python3

"""Create a Hetzner Cloud server and install NixOS on it."""

import sys

from rich import print

from hetzner_create import create
from ssh_deploy import format_users_nix, install_nixos, wait_for_ssh


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: {sys.argv[0]} <ssh-public-key>")

    public_key = sys.argv[1].strip()

    format_users_nix(public_key)

    ip = create(public_key)

    install_nixos(ip)

    wait_for_ssh(ip, "Waiting for NixOS to boot...", user="developer")

    print("NixOS is up.")
    print(f"Connect with: ssh developer@{ip}")


if __name__ == "__main__":
    main()
