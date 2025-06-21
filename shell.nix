{
  pkgs ? import <nixpkgs> { },
}:
let
  adb_auto = pkgs.callPackage ./derivation.nix { };
in
pkgs.mkShellNoCC {
  packages = with pkgs; [
    adb_auto

    android-tools
    scrcpy
  ];

  shellHook = ''
    export PYTHONPATH=$PYTHONPATH:src
  '';
}
