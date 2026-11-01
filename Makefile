SSH_PUBLIC_KEY ?= $(shell cat $(HOME)/.ssh/id_ed25519.pub)

.PHONY: help ssh_deploy hetzner_create hetzner_deploy hetzner_destroy copy_repo

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

ssh_deploy: ## Install NixOS on an SSH host: make ssh_deploy HOST=<user@host>
	@test -n "$(HOST)" || { echo "Usage: make ssh_deploy HOST=<user@host>"; exit 1; }
	uv run ssh_deploy.py $(HOST) "$(SSH_PUBLIC_KEY)"

hetzner_create: ## Create the Hetzner VPS without installing NixOS
	uv run hetzner_create.py "$(SSH_PUBLIC_KEY)"

hetzner_deploy: ## Create the Hetzner VPS and install NixOS
	uv run create_vps.py "$(SSH_PUBLIC_KEY)"

hetzner_destroy: ## Delete the Hetzner VPS
	uv run delete_vps.py

copy_repo: ## Copy the repository to the VPS
	uv run copy_repo.py
