{ pkgs, ... }:
let
    # incus-compose is not in nixpkgs: use the official static release
    # binary (same approach as /root/cep/image/image.nix)
    incus-compose = pkgs.stdenv.mkDerivation {
        pname = "incus-compose";
        version = "1.3.5";
        src = pkgs.fetchurl {
            url = "https://github.com/lxc/incus-compose/releases/download/v1.3.5/incus-compose_1.3.5_linux_amd64.tar.gz";
            sha256 = "0ed925b152ec5cea08b72f2f2ffbaa167619103a9aefb2582285920d5931facb";
        };
        # The release tarball is flat (no directory entries), which trips
        # unpackPhase's sourceRoot auto-detection - unpack it by hand.
        dontUnpack = true;
        nativeBuildInputs = [ pkgs.gnutar ];
        installPhase = ''
            runHook preInstall
            tar -xzf "$src" incus-compose
            install -Dm 0755 incus-compose $out/bin/incus-compose
            runHook postInstall
        '';
    };
in
{
    environment.systemPackages = [ incus-compose ];

    virtualisation.incus.enable = true;
    virtualisation.incus.package = pkgs.incus;
    virtualisation.incus.ui.enable = true;
    networking.nftables.enable = true;
    users.users.developer.extraGroups = ["incus-admin"];

    virtualisation.incus.preseed = {
        config = {
            "core.https_address" = ":8443";
        };

        # incus-compose keeps built/pulled images in a private cache project
        # (`--image-cache`, default "incus-compose-cache") and creates it on
        # its first command; cep's image/build.sh imports into it before any
        # incus-compose command has run on a fresh host, though, so preseed
        # the project instead of a manual post-deploy step. The config must be
        # explicit: omitted config marshals as `null` and disables the
        # daemon's default project features (features.images among them).
        # This mirrors what incus-compose itself ends up creating (daemon
        # defaults + its "incus-compose: <name>" description); a pre-existing
        # project is adopted unchanged by incus-compose.
        projects = [
        {
            name = "incus-compose-cache";
            description = "incus-compose: incus-compose-cache";
            config = {
                "features.images" = "true";
                "features.profiles" = "true";
                "features.storage.volumes" = "true";
                "features.storage.buckets" = "true";
            };
        }
        ];
        networks = [
        {
            config = {
                "ipv4.address" = "10.0.100.1/24";
                "ipv4.nat" = "true";
            };
            name = "incusbr0";
            type = "bridge";
        }
        ];
        profiles = [
        {
            devices = {
                eth0 = {
                    name = "eth0";
                    network = "incusbr0";
                    type = "nic";
                };
                root = {
                    path = "/";
                    pool = "default";
                    size = "10GiB";
                    type = "disk";
                };
            };
            name = "default";
        }
        ];
        storage_pools = [
        {
            config = {
                source = "/var/lib/incus/storage-pools/default";
            };
            driver = "dir";
            name = "default";
        }
        ];
    };

}
