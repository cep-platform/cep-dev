{ pkgs, ... }:
{
    environment.systemPackages = with pkgs; [
        neovim
        gcc
        git
        gnupg
        curl
        wget
        gh
        tmux
        fzf
        ripgrep
        tree
        mlocate
	python3
	uv
    lazydocker
    opencode
    bind
    htop
    ];
}
