{
  description = "Cep development instance";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

    disko.url = "github:nix-community/disko";
    disko.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, disko, ... }:
  let
    system = "x86_64-linux";
  in {
    nixosConfigurations.cep-dev = nixpkgs.lib.nixosSystem {
      inherit system;

      modules = [
        ./modules/base.nix
        ./modules/users.nix
        ./modules/networking.nix
        ./modules/packages.nix
        ./modules/programs.nix
        ./modules/aliases.nix

        ./modules/disk.nix
        ./modules/incus.nix
        ./modules/docker.nix

        disko.nixosModules.disko
      ];
    };
  };
}
