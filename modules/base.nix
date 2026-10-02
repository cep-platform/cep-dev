{ ... }:
{
    system.stateVersion = "25.11";

    boot.initrd.availableKernelModules = [ "virtio_pci" "virtio_scsi" "virtio_blk" "virtio_net" ];

    time.timeZone = "Europe/Amsterdam";
    i18n.defaultLocale = "en_US.UTF-8";

    nix.settings.experimental-features = [ "nix-command" "flakes" ];

    services.openssh.enable = true;

    security.sudo.enable = true;
    security.sudo.wheelNeedsPassword = false;
}
