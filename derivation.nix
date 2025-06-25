{ lib, python312Packages }:
with python312Packages;
buildPythonApplication {
  pname = "adb_auto";
  version = "0.0.1";

  format = "pyproject";
  propagatedBuildInputs = [
    build
    setuptools

    pure-python-adb
    flasgger
    flask
  ];

  src = ./.;

}
