from arguments import args
import configparser
import pyperclip

import blur_192
import blur_18
import smoothie

from constants import LOGO


def verbose(string):
    if args.verbose:
        print(string)


def parse_config(path):
    if path.endswith(".cfg"):
        verbose("opening config...")
        with open(path, "r") as file:
            config_contents = file.read()
        verbose("parsing config...")
        config_lines = config_contents.split("\n")
        verbose("parsing config...")
        dict_config = {}
        for line in config_lines:
            if ": " in line:
                split_line = line.split(": ", 1)
                dict_config[split_line[0]] = split_line[1]
        return dict_config
    verbose("opening recipe...")
    config = configparser.RawConfigParser()
    config.read(path)
    verbose("parsing recipe...")
    dict = {}
    for section in config.sections():
        dict[section] = {}
        for item in config.items(section):
            dict[section][item[0]] = item[1]
    return dict


def config_type(path):
    config = parse_config(path)
    verbose("detecting config type...")
    if path.endswith(".cfg"):
        if "interpolation program (svp/rife/rife-ncnn)" in config:
            verbose("blur 1.8 config detected")
            return "blur_1.8"
        verbose("blur 1.92 config detected")
        return "blur_1.92"
    verbose("smoothie recipe detected")
    return "smoothie"


def convert(config, path, output):
    match config_type(path):
        case "blur_1.8":
            return blur_18.convert(config, output)
        case "blur_1.92":
            return blur_192.convert(config, output)
        case "smoothie":
            return smoothie.convert(config, output)


def shorten(config, path):
    match config_type(path):
        case "blur_1.8":
            return blur_18.shorten(config)
        case "blur_1.92":
            return blur_192.shorten(config)
        case "smoothie":
            return smoothie.shorten(config)


def vegas(config, path):
    match config_type(path):
        case "blur_1.8":
            return blur_18.calculate_vegas(config)
        case "blur_1.92":
            return blur_192.calculate_vegas(config)
        case "smoothie":
            return smoothie.calculate_vegas(config)


if __name__ == "__main__":
    if args.input:
        verbose("input argument received")
        config_path = args.input.replace('"')
    else:
        print(LOGO)
        config_path = input("paste the path to your config/recipe here: ").replace(
            '"', ""
        )

    config = parse_config(config_path)

    if not args.shorten and not args.vegas and not args.output:
        operation = input(
            """would you like to:
    (1) convert
    (2) shorten
    (3) calculate vegas weights
    """
        )
        match operation:
            case "1" | "convert":
                verbose("copying...")
                pyperclip.copy(convert(config, config_path, "input"))
            case "2" | "shorten":
                verbose("copying...")
                pyperclip.copy(shorten(config))
            case "3" | "vegas":
                verbose("applying weights...")
                with open(config_path, "w") as file:
                    file.write(vegas(config))
        input("done! (press enter to exit)")
    else:
        if args.shorten:
            verbose("shorten argument received")
            if args.output and args.output != config_type(config_path):
                verbose("output (convert) argument received")
                if args.vegas:
                    verbose("vegas argument received")
                    config = vegas(config)
                config = convert(config, config_path, args.output)
            config = shorten(config)
        if not args.output and not args.shorten:
            verbose("applying weights...")
            with open(config, "w") as file:
                file.write(vegas(config))
        else:
            verbose("copying...")
            pyperclip.copy(config)
        input("done! (press enter to exit)")
