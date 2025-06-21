# Nix shell for LaTeX

{
  pkgs ? import <nixpkgs> { },
}:

let
in
pkgs.mkShellNoCC {
  packages = with pkgs; [
    android-tools
    python312
    python312Packages.pure-python-adb
    python312Packages.pyqt6
    scrcpy
  ];
}
