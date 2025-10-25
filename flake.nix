{
  description = "seekers-api";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        stdenv = pkgs.stdenv;
        lib = import nixpkgs.lib;
        shell = nixpkgs.legacyPackages."${system}".callPackage ./shell.nix {
          pkgs = pkgs;
          lib = lib;
        };
      in
      {
        # enables use of `nix shell`
        devShell = shell;
      }
    );
}
