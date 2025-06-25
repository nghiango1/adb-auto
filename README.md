# ADB automation

> Short form project name adb_auto

I want this, with AI later, may be with MCP so LLM can help with automate task

Intended feature: Automation with some expected event handling

- [ ] Simple UI for quicky create automated task
- [ ] Handle image/text found from device screen and trigger automation event
- [ ] Time trigger event (Date/time/week/month)
- [ ] Background event - Will alway run when no higher priority event is executed

**Extra:** First I will just hard code all of the event in python, may want to:

- [ ] Create seperated event file type to describing Trigger (may reuse some existed framework, idk, or reuse `yml`/`json` format)
- [ ] Create a core event handling instead, which run base the event type I have descripbed

## Notes

Setup enviroment: I use nix, so other either put `default.nix`, `derivation.nix` and `pyproject.toml` content into some LLM chat box to find the exact pip-package-build/system tools required to run the application. Or you will want to install `nix-shell`, still need to provide nix-pkg rev tho (as I use NixOS so there no need for me to do that). Other than that, here is how

## Development environment

Setup system tools and python dependancy: No need for `pip install` or `apt install`, just `nix-shell`

```sh
nix-shell
```

Then we can run the module directly for every local change (sort of)

```sh
python -m src/adb_auto/main.py
```

You can build python pacakge normally using this evironment also, which is nesseary to publish this pacakge

```sh
python -m build
# python -m twine upload -r pypi dist/*
```

## Build/Prod "environment"

> This build is for nix-os, that how I can use the tools

It just `nix-build`, there no need to have any setup

```sh
nix-build
```

Running the tools

```sh
./result/bin/adb_auto
```

> I also added the built nix-pacakge into `shell.nix`, so we also expect `adb_auto` is available for running when setup dev environment. It not update to development change though
