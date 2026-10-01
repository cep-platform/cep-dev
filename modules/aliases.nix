{ ... }:
{
    environment.shellAliases = {
        his = "history | fzf | sed \"s/^[[:space:]]*[[:digit:]]*[[:space:]]*//g\"";

        l = "ls";
        ll = "ls -l";
        lt = "ls -lrts";
        lla = "ls -la";

        gpu = "nvidia-smi | less";

        pva = "source .venv/bin/activate";
        pipr = "pip install -r requirements.txt";

        pdva = "eval $(pdm venv activate in-project)";

        vim = "$(which nvim)";

        gi = "vim $(git rev-parse --show-toplevel)/.gitignore";
        ge = "vim $(git rev-parse --show-toplevel)/.git/info/exclude";
        ga = "git add";
        gaa = "git add -A";
        gl = "git log --graph --oneline --decorate --all";
        gll = "git log --graph --decorate --all";
        gs = "git status";
        gc = "git commit";
        gcm = "git commit -m";
        gb = "git branch";
        gco = "git checkout";
        gcob = "git checkout -b";
    };
}
