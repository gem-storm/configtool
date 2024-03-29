from constants import VERSION
import main

from tkinter import *


window = Tk()
window.title(f"configtool v{VERSION}")
window.minsize(width=530, height=750)
window.iconbitmap("../assets/logo.ico")


input_box_label = Label(text="Paste input config contents here:")
output_box_label = Label(text="Output appears here:")

input_box_label.grid(column=0, row=0, pady=10)
output_box_label.grid(column=1, row=0, pady=10)


input_box = Text(height=30, width=30)
output_box = Text(height=30, width=30)
input_box.grid(column=0, row=1, padx=10)
output_box.grid(column=1, row=1, padx=10)


def output_format():
    match output.get():
        case 0:
            return "smoothie"
        case 1:
            return "blur_1.8"
        case 2:
            return "blur_1.92"


format_label = Label(text="Output format:")
format_label.grid(column=1, row=3, sticky=W, padx=50)

output = IntVar()

smoothie_button = Radiobutton(text="Smoothie (Latest)", value=0, variable=output)
blur_18_button = Radiobutton(text="Blur (1.8)", value=1, variable=output)
blur_192_button = Radiobutton(text="Blur (1.92)", value=2, variable=output)

smoothie_button.grid(column=1, row=4, sticky=W, padx=50)
blur_18_button.grid(column=1, row=5, sticky=W, padx=50)
blur_192_button.grid(column=1, row=6, sticky=W, padx=50)


input_fps_label = Label(text="Input FPS (if needed):")
input_fps_text = Entry(width=5)


def input_fps():
    if vegas_var.get() == 1:
        input_fps_label.grid(column=0, row=8, sticky=W, padx=10)
        input_fps_text.grid(column=0, row=9, sticky=W, padx=15)
    else:
        input_fps_label.grid_forget()
        input_fps_text.grid_forget()


vegas_var = IntVar()
vegas_check = Checkbutton(
    text="Calculate VEGAS weights", variable=vegas_var, command=input_fps
)
vegas_check.grid(column=0, row=7, stick=W, padx=10)


shorten_var = IntVar()
shorten_check = Checkbutton(text="Shorten", variable=shorten_var)
shorten_check.grid(column=0, row=4, stick=W, padx=10)


path_text = Entry(width=40)


def path():
    if path_var.get() == 1:
        path_text.grid(column=0, row=6, sticky=W, padx=10)
    else:
        path_text.grid_forget()


path_var = IntVar()
path_check = Checkbutton(text="Use path instead", variable=path_var, command=path)
path_check.grid(column=0, row=5, sticky=W, padx=10)


def config_type(config):
    if "interpolation program (svp/rife/rife-ncnn)" in config:
        return "blur_1.8"
    elif "interpolation block size" in config:
        return "blur_1.92"
    return "smoothie"


def parse_config():
    if path_var.get() == 1:
        with open(path_text.get()) as file:
            config = file.read()
    else:
        config = input_box.get("1.0", END)
    config_lines = config.split("\n")

    if config_type(config) in ["blur_1.8", "blur_1.92"]:
        dict_config = {}
        for line in config_lines:
            if ": " in line:
                split_line = line.split(": ", 1)
                dict_config[split_line[0]] = split_line[1]
        return dict_config
    else:
        cfgparse = main.configparser.RawConfigParser()
        cfgparse.read_string(config)
        dict = {}
        for section in cfgparse.sections():
            dict[section] = {}
            for item in cfgparse.items(section):
                dict[section][item[0]] = item[1]
        return dict


def convert_config():
    config = parse_config()
    output = output_format()
    input_type = config_type(input_box.get("1.0", END))

    if input_type == output:
        return input_box.get("1.0", END)

    match input_type:
        case "blur_1.8":
            converted_config = main.blur_18.convert(config, output)
        case "blur_1.92":
            converted_config = main.blur_192.convert(config, output)
        case "smoothie":
            converted_config = main.smoothie.convert(config, output)

    if vegas_var.get() == 1:
        match input_type:
            case "blur_1.8":
                converted_config = main.blur_18.calculate_vegas(
                    config, input_fps_text.get()
                )
            case "blur_1.92":
                converted_config = main.blur_192.calculate_vegas(
                    config, input_fps_text.get()
                )
            case "smoothie":
                converted_config = main.smoothie.calculate_vegas(config)
    if shorten_var.get() == 1:
        match input_type:
            case "blur_1.8":
                converted_config = main.blur_18.shorten(config)
            case "blur_1.92":
                converted_config = main.blur_192.shorten(config)
            case "smoothie":
                converted_config = main.smoothie.shorten(config)
    return converted_config


def paste_config():
    converted_config = convert_config()
    output_box.delete("1.0", END)
    output_box.insert(1.0, converted_config)


def copy_config():
    main.pyperclip.copy(output_box.get("1.0", END))


convert_button = Button(text="Convert", command=paste_config)
convert_button.config(width=10, height=1)

copy_button = Button(text="Copy", command=copy_config)
copy_button.config(width=10, height=1)

convert_button.grid(column=0, row=2, pady=10)
copy_button.grid(column=1, row=2, pady=10)

window.mainloop()
