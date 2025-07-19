{
  description = "Reddit comment fetcher using PRAW";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          praw
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [ 
            pythonEnv
          ];
          
          shellHook = ''
            echo "Reddit PRAW environment activated"
            echo "Python version: $(python --version)"
            echo "PRAW version: $(python -c 'import praw; print(praw.__version__)')"
          '';
        };
      });
}