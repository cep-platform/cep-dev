{ ... }:
{
    programs = {
        zoxide = {
            enable = true;
        };

        tmux = {
            enable = true;
            keyMode = "vi";
        };
        zsh = {
            enable = true;
            shellInit = "bindkey -v";
            autosuggestions.enable = true;
            syntaxHighlighting.enable = true;
            ohMyZsh = {
                enable = true;
                theme = "flazz";
                plugins = [
                    "git"
                    "docker"
                ];
            };
        };
    };
}
