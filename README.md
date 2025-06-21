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

- Development environment

  ```sh
  nix-shell
  python -m build
  # python -m twine upload -r pypi dist/*
  ```

- Build "environment": It just build, there no need to have any setup

  ```sh
  nix-build
  ```
