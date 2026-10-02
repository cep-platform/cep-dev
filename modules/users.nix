{ pkgs, ... }:
{
    environment.enableAllTerminfo = true;
    users.users.developer = {
        isNormalUser = true;
        home = "/home/developer";
        description = "developer";
        extraGroups = [ "wheel" "networkmanager" "docker" ];
        openssh.authorizedKeys.keys = [
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIESWe4Oc5z2ett0H8YWPVVbJdl+AfDU4QQTQH5zeBza3 cep-dev-local"
        ];
        shell = pkgs.zsh;
    };
}
