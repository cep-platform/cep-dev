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
	# Fast-moving dev tooling comes from nixpkgs-unstable (pkgs.unstable.*).
	unstable.uv
    unstable.lazydocker
    unstable.opencode
    bind
    htop
    gnumake
    unstable.pi-coding-agent
    ];
}
