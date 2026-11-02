# TEMPORARY: Docker is enabled on cep-dev only to work around DNS issues.
# Once the DNS issues are resolved, remove the "./modules/docker.nix" entry
# from flake.nix and delete this file.
{ pkgs, ... }:
{
    virtualisation.docker.enable = true;
    virtualisation.docker.package = pkgs.docker_29;
}