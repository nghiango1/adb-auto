{
  pkgs ? import <nixpkgs> { },
}:
pkgs.mkShellNoCC {
  packages = with pkgs; [
    python312
    python312Packages.pure-python-adb
    python312Packages.flask
    python312Packages.flasgger
    python312Packages.pytesseract
    python312Packages.numpy
    python312Packages.opencv-python
    python312Packages.gunicorn
    python312Packages.python-dotenv
    python312Packages.redis

    redis
    tailwindcss_4
    android-tools
    scrcpy
  ];

  shellHook = ''
    export PYTHONPATH=$PYTHONPATH:src
    
    alias get_devices_ip='adb shell ip a | grep 192 | python -c "import sys; print(sys.stdin.read().split()[1][:-3])"'
  '';
}
