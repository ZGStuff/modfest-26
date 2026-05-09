{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      forAllSystems =
        function:
        nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed (
          system: function nixpkgs.legacyPackages.${system}
        );
    in
    {
      devShells = forAllSystems (pkgs: {

        default = pkgs.mkShell {
          packages = with pkgs; [
            packwiz
            jdk25
            (python3.withPackages (python-pkgs: [
              python-pkgs.tomli-w
              python-pkgs.requests
            ]))
          ];
        };
      });
    };
}
