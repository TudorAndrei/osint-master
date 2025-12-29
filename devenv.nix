
{ pkgs, config, ... }: {
  # Python configuration with uv
  languages.python = {
    enable = true;
    version = "3.11";
    venv.enable = true;
    uv.enable = true;
  };

  # Install Bun
  packages = with pkgs; [
    bun
    git
  ];

  enterShell = ''
    alias openspec='bunx @fission-ai/openspec@latest'
  '';
}