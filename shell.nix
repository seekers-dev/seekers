{
  pkgs ? import <nixpkgs> { },
  lib ? import <nixpkgs/lib> { },
  ...
}:

pkgs.mkShell {
  packages = with pkgs; [
    nixfmt-rfc-style
  ];

  nativeBuildInputs = with pkgs; [
    python312Packages.pygame
    python312Packages.grpcio
    python312Packages.protobuf
  ];
}
