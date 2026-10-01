{ ... }:
{
    time.timeZone = "Europe/Amsterdam";
    i18n.defaultLocale = "en_US.UTF-8";

    nix.settings.experimental-features = [ "nix-command" "flakes" ];

    services.openssh.enable = true;

    security.sudo.enable = true;
    security.sudo.wheelNeedsPassword = false;
}
