{ unstable, ... }:
{
    # Exposes the nixpkgs-unstable input as pkgs.unstable.* so that
    # packages.nix can pull fast-moving development tools from it.
    # Only leaf CLI tools should come from here; the system core
    # (kernel, systemd, services) stays on the stable nixpkgs input.
    nixpkgs.overlays = [
        (final: prev: {
            unstable = import unstable {
                system = final.hostPlatform.system;
            };
        })
    ];
}
