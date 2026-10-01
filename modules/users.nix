{ pkgs, ... }:
{
    environment.enableAllTerminfo = true;
    users.users.developer = {
        isNormalUser = true;
        home = "/home/developer";
        description = "developer";
        extraGroups = [ "wheel" "networkmanager" "docker" ];
        openssh.authorizedKeys.keys = [
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICD6jKjzmbaiORhA9DHu3ieCE3AcdDoiKTCrosFlW+i6 sven@nixos"
        ];
        shell = pkgs.zsh;
    };
}
