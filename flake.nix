{
  description = "Cep development instance";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

    # Unstable is only used for fast-moving development tooling
    # (pi-coding-agent, opencode, uv, lazydocker). Everything that
    # powers the system (kernel, systemd, services) stays on stable.
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";

    disko.url = "github:nix-community/disko";
    disko.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, nixpkgs-unstable, disko, ... }:
  let
    system = "x86_64-linux";
  in {
    nixosConfigurations.cep-dev = nixpkgs.lib.nixosSystem {
      inherit system;

      specialArgs.unstable = nixpkgs-unstable;

      modules = [
        ./modules/base.nix
        ./modules/users.nix
        ./modules/networking.nix
        ./modules/unstable.nix
        ./modules/packages.nix
        ./modules/programs.nix
        ./modules/aliases.nix

        ./modules/disk.nix
        ./modules/incus.nix

        # TEMP: Docker is only enabled to work around DNS issues.
        # Remove this entry (and modules/docker.nix) once the DNS issues
        # are resolved.
        ./modules/docker.nix

        disko.nixosModules.disko
      ];
    };
  };
}
