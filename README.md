# swaypresent

Small script to setup sway for a presentation using wl-mirror.

## Usage

```
usage: swaypresent.py [-h] [-s SOURCE] [-d DESTINATION] [-w WORKSPACE] [-o] [-r]

Launch wl-mirror on a new workspace in fullscreen

options:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        The output to mirror (default: first)
  -d DESTINATION, --destination DESTINATION
                        The output where the mirror is displayed (default: second)
  -w WORKSPACE, --workspace WORKSPACE
                        Name of workspace where mirror will be displayed
  -o, --fix-overlapping
                        Fix overlapping outputs
  -r, --match-ratio     Set aspect ratio of source output to match destination output
```

Once launched, you can select a different region with `wl-present set-region` or output with `wl-present set-output`.

## Dependencies

Arch Linux Packages: `sway`, `python-i3ipc`, `wl-mirror` (AUR), `pipectl` (AUR), `slurp`