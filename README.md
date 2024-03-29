## configtool
a python program for converting and modifying config files for [blur](https://github.com/f0e/blur) and [smoothie](https://github.com/couleur-tweak-tips/smoothie-rs).

## supported programs/versions:
- blur v1.8
- blur v1.92
- the latest version of smoothie-rs

In the future, [teres](https://github.com/animafps/teres) *may* be supported.

## features
- convert configs to another program/version
- calculate & apply [vegas weights](https://github.com/unknownopponent/Editing-Software-Frame-Blending-Weights-Estimation/blob/main/Vegas.md) for blur
- shorten config to not flood the chat

## installation

### dependencies
- python
- [pyperclip](https://pypi.org/project/pyperclip/)

### installation

download the [latest release](https://github.com/gem-storm/configtool/releases/latest) and unzip it.

## usage
run `main.py` to start the program and paste the path to your config/recipe when prompted. the rest should be self-explanatory.

## cli args (v0.3+)
`--help`
shows basic help message and exits.

`--input [PATH]`
input config path, this can be used for sendto shortcuts.

`--output [FORMAT]`
output config format ('blur_1.8', 'blur_1.92', or 'smoothie').

`--shorten`
shortens the output config.

`--vegas`
calculates and applies vegas weights (copies result if multiple operations are specified).

`--verbose`
prints extra information for debugging.

> you can also use multiple operations (e.g. `$ python main.py --vegas --shorten`).
