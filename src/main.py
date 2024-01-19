import configparser
import pyperclip

import blur_192
import blur_18
import smoothie

from constants import LOGO


# todo:
# convert smoothie's custom weight namespace to blur's


def split_config(path):
    with open(path, "r") as file:
        config_contents = file.read()
    return config_contents.split("\n")


def config_type(config_lines, path):
    if "interpolation program (svp/rife/rife-ncnn)" in config_lines:
        print("Blur v1.8 config detected")
        return "blur_1.8"
    elif "interpolation block size" in config_lines:
        print("Blur v1.92 config detected")
        return "blur_1.92"
    else:
        if path.endswith(".ini"):
            print("Smoothie config detected")
            return "smoothie"
        else:
            print(
                """Your config doesn't match any support blur config and isn't in the .ini container (Smoothie).
                Ensure that your input path is a support config format. (Blur v1.8, Blur v1.92, or Smoothie)"""
            )
            return "invalid"


def parse_config(config_lines):
    dict_config = {}
    for line in config_lines:
        if ": " in line:
            split_line = line.split(": ", 1)
            dict_config[split_line[0]] = split_line[1]
    return dict_config


print(LOGO)
config_path = input("Paste the input config/recipe's path here: ").replace('"', "")
config_lines = split_config(config_path)

while True:
    operation = input(
        """
    Do you want to:
        (1) Convert
        (2) Calculate VEGAS Weights
        (3) Shorten
        (4) Use a different input config
        (5) Exit
    """
    ).lower()

    program = config_type(config_lines)

    if operation in ["1", "convert"]:
        match program:
            case "blur_1.8":
                config = parse_config(config_lines)
                pyperclip.copy(blur_18.choose_program(config))
                print("Result copied to clipboard.")

            case "blur_1.92":
                config = parse_config(config_lines)
                pyperclip.copy(blur_192.choose_program(config))
                print("Result copied to clipboard.")

            case "smoothie":
                config = configparser.ConfigParser()
                config.read(config_path)
                pyperclip.copy(smoothie.choose_program(config))
                print("Result copied to clipboard.")
    elif operation in ["2", "vegas", "vegas weights", "calculate vegas weights"]:
        match program:
            case "blur_1.8":
                config = parse_config(config_lines)
                with open(config_path, "w") as file:
                    file.write(blur_18.calculate_vegas(config))
                print("Weights have been successfully applied.")

            case "blur_1.92":
                config = parse_config(config_lines)
                with open(config_path, "w") as file:
                    file.write(blur_192.calculate_vegas(config))
                print("Weights have been successfully applied.")

            case "smoothie":
                print(
                    "dawg smoothie has vegas weights built in...\n(it's just 'weighting: vegas')"
                )

    elif operation in ["3", "shorten"]:
        match program:
            case "blur_1.8":
                config = parse_config(config_lines)
                pyperclip.copy(blur_18.shorten(config))
                print("Result copied to clipboard.")
            case "blur_1.92":
                config = parse_config(config_lines)
                pyperclip.copy(blur_192.shorten(config))
                print("Result copied to clipboard.")
            case "smoothie":
                config = configparser.ConfigParser()
                config.read(config_path)
                pyperclip.copy(smoothie.shorten(config))
                print("Result copied to clipboard.")

    elif operation in ["4", "config", "use a different input config"]:
        config_path = input("Paste the new path here: ").replace('"', "")
    elif operation in ["5", "exit"]:
        exit()
    else:
        print("Not recognized as an option")
