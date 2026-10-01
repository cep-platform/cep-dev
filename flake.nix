{
  description = "Cep development instance";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

  outputs = { self, nixpkgs, ... }:
  let
    system = "x86_64-linux";
  in {
    nixosConfigurations.cep-dev = nixpkgs.lib.nixosSystem {
      inherit system;

      modules = [
        /etc/nixos/configuration.nix

        ./modules/base.nix
        ./modules/users.nix
        ./modules/networking.nix
        ./modules/packages.nix
        ./modules/programs.nix
        ./modules/aliases.nix

        ./modules/incus.nix
        ./modules/docker.nix
      ];
    };
  };
}
