from constants import YES, ENC_PRESETS
import configparser


def has_section(config, category):
    if category in config:
        return True
    return False


def has_key(config, category, key):
    if has_section(config, category):
        if key in config[category]:
            return True
    return False


def basic_value(config, category, key, default):
    if has_key(config, category, key):
        return config[category][key]
    return default


def bool_value(config, category, key):
    if has_key(config, category, key):
        if config[category][key] in YES:
            return "true"
    return "false"


def category_enabled(config, category):
    if has_section(config, category):
        if has_key(config, category, "enabled"):
            if config[category]["enabled"] in YES:
                return "true"
            return "false"
        return "true"
    return "false"


def category_masking(config, category):
    if category_enabled(config, "artifact masking") == "true":
        if bool_value(config, category, "masking") == "true":
            return True
    return False


def interp_fps(config):
    if has_key(config, "interpolation", "fps"):
        if "x" not in config["interpolation"]["fps"]:
            return int(config["interpolation"]["fps"])
        return config["interpolation"]["fps"]
    return 1920


def convert_weighting(config):
    raw_weighting = config["frame blending"]["weighting"]
    weighting = raw_weighting.split(";")[0]
    if weighting == "vegas":
        if category_enabled(config, category="interpolation") == "true" and isinstance(
            interp_fps(config), int
        ):
            blurframes = int(
                interp_fps(config) / int(basic_value(config, "frame blending", "fps", 60)) * float(basic_value(config, "frame blending", "intensity", 1.0))
            )
            if blurframes % 2 == 1:
                return "equal"
            return "[1," + "2," * (blurframes - 1) + "1]"
        return "equal"
    if weighting in ["ascending", "descending"]:
        return "pyramid"
    if weighting == "pyramid":
        return "pyramid_sym"
    if weighting == "gaussian":
        apex = blending_apex(config)
        std_dev = blending_std_dev(config)
        return f"1 / ((m := __import__('math')).sqrt(2 * m.pi) * {std_dev}) * m.exp(-((x - {apex}) / {std_dev}) ** 2 / 2)"
    if weighting == "custom":
        print(
            "Custom weight functions are not fully supported, do not expect them to work after conversion."
        )
        stripped_custom = raw_weighting.replace(" ", "").removeprefix("custom;func=")
        converted_custom = []
        for value in stripped_custom.split(";").strip():
            if "bound" not in value and "std_dev" not in value:
                converted_custom.append(value)
        return " ".join(converted_custom)
    return weighting


def blending_weighting(config):
    if has_key(config, "frame blending", "weighting"):
        return convert_weighting(config)
    return "equal"



def blending_std_dev(config):
    if has_key(config, "frame blending", "weighting"):
        weighting_split = config["frame blending"]["weighting"].split(";")
        for value in weighting_split:
            if "std_dev" in value:
                return value.split("=")[1].strip()
    return "1"


def blending_bound(config):
    if has_key(config, "frame blending", "weighting"):
        weighting_split = config["frame blending"]["weighting"].split(";")
        for value in weighting_split:
            if "bound" in value:
                return value.split("=")[1].strip()
    return "[0,2]"


def blending_apex(config):
    if has_key(config, "frame blending", "weighting"):
        weighting_split = config["frame blending"]["weighting"].split(";")
        for value in weighting_split:
            if "apex" in value:
                return value.split("=")[1].strip()
    return "[0,2]"


def reverse_weights(config):
    if has_key(config, "frame blending", "weighting"):
        if config["frame blending"]["weighting"] == "descending":
            return "true"
    return "false"


def output_encoding_args(config):
    enc_arg_presets = configparser.ConfigParser()
    enc_arg_presets.read_string(ENC_PRESETS)

    if has_key(config, "output", "enc args"):
        input_enc_args = config["output"]["enc args"]
        split_args = input_enc_args.split(" ")
        sections = enc_arg_presets.sections()
        parsed_args = []
        for index, word in enumerate(split_args):
            if word.isupper():
                if word.lower() in dict(enc_arg_presets.items("MACROS")):
                    parsed_args.append(enc_arg_presets.get("MACROS", word.lower()))
                    continue
                for section in sections:
                    if word in section.split("/"):
                        next_word = split_args[index + 1]
                        parsed_args.append(enc_arg_presets.get(section, next_word))
            else:
                parsed_args.append(word)
        return " ".join(parsed_args)
    return "-c:v libx264 -preset slow -aq-mode 3 -crf 16"


def output_container(config):
    if has_key(config, "output", "container"):
        return config["output"]["container"].removeprefix(".").lower()
    return "mp4"


def misc_deduplicate(config):
    if has_key(config, "miscellaneous", "dedup threshold"):
        if float(config["miscellaneous"]["dedup threshold"]) > 0.0:
            return "true"
    return "false"


def color(config, key):
    if has_key(config, "color grading", "enabled"):
        if config["color grading"]["enabled"] in YES:
            return basic_value(config, "color grading", key, 1.0)
    return "1.0"


def convert(config, output):
    if output == "input":
        output = input(
            """convert to:
(1) blur_1.8
(2) blur_1.92
"""
        )
        if output == "1":
            output = "blur_1.8"
        elif output == "2":
            output = "blur_1.92"
    match output:
        case "blur_1.8":
            return make_18_config(config)
        case "blur_1.92":
            return make_192_config(config)


def make_18_config(config):
    return f"""- blur
blur: {category_enabled(config, category="frame blending")}
blur amount: {basic_value(config, "frame blending", "intensity", "1.0")}
blur output fps: {basic_value(config, "frame blending", "fps", "60")}
blur weighting: {blending_weighting(config)}

- interpolation
interpolate: {category_enabled(config, category="interpolation")}
interpolated fps: {interp_fps(config)}

- rendering
quality: 18
preview: {bool_value(config, category="preview window", key="enabled")}
detailed filenames: false

- timescale
input timescale: {bool_value(config, category="timescale", key="in")}
output timescale: {bool_value(config, category="timescale", key="out")}
adjust timescaled audio pitch: false

- filters
brightness: {color(config, key="brightness")}
saturation: {color(config, key="saturation")}
contrast: {color(config, key="contrast")}

- advanced rendering
gpu: false
gpu type (nvidia/amd/intel): nvidia
deduplicate: {misc_deduplicate(config)}
custom ffmpeg filters: {output_encoding_args(config)}

- advanced blur
blur weighting gaussian std dev: {blending_std_dev(config)}
blur weighting triangle reverse: {reverse_weights(config)}
blur weighting bound: {blending_bound(config)}

- advanced interpolation
interpolation program (svp/rife/rife-ncnn): svp
interpolation speed: {basic_value(config, "interpolation", "speed", "medium")}
interpolation tuning: {basic_value(config, "interpolation", "tuning", "weak")}
interpolation algorithm: {basic_value(config, "interpolation", "algorithm", "23")}"""


def make_192_config(config):
    return f"""[blur v1.9]
- blur
blur: {category_enabled(config, category="frame blending")}
blur amount: {basic_value(config, "frame blending", "intensity", "1.0")}
blur output fps: {basic_value(config, "frame blending", "fps", "60")}
blur weighting: {blending_weighting(config)}

- interpolation
interpolate: {category_enabled(config, category="interpolation")}
interpolated fps: {interp_fps(config)}

- rendering
quality: 18
deduplicate: {misc_deduplicate(config)}
preview: {bool_value(config, category="preview window", key="enabled")}
detailed filenames: false

- timescale
input timescale: {bool_value(config, category="timescale", key="in")}
output timescale: {bool_value(config, category="timescale", key="out")}
adjust timescaled audio pitch: false

- filters
brightness: {color(config, key="brightness")}
saturation: {color(config, key="saturation")}
contrast: {color(config, key="contrast")}

- advanced rendering
gpu interpolation: {bool_value(config, category="interpolation", key="use gpu")}
gpu rendering: false
gpu type (nvidia/amd/intel): nvidia
video container: {output_container(config)}
custom ffmpeg filters: {output_encoding_args(config)}

- advanced blur
blur weighting gaussian std dev: {blending_std_dev(config)}
blur weighting triangle reverse: {reverse_weights(config)}
blur weighting bound: {blending_bound(config)}

- advanced interpolation
interpolation preset: {basic_value(config, "interpolation", "tuning", "weak")}
interpolation algorithm: {basic_value(config, "interpolation", "algorithm", "23")}
interpolation block size: 8
interpolation speed: {basic_value(config, "interpolation", "speed", "medium")}
interpolation mask area: {basic_value(config, "interpolation", "area", "0")}"""


def shorten(config):
    shortened_config = []
    if category_enabled(config, "interpolation") == "true":
        shortened_config.append("[interpolation]")
        if category_masking(config, "interpolation"):
            shortened_config.append("masking: yes")
        shortened_config.append(f"fps: {interp_fps(config)}")
        shortened_config.append(f"speed: {basic_value(config, "interpolation", "speed", "medium")}")
        shortened_config.append(f"tuning: {basic_value(config, "interpolation", "tuning", "weak")}")
        shortened_config.append(f"algorithm: {basic_value(config, "interpolation", "algorithm", "23")}")
        area = basic_value(config, "interpolation", "area", "0")
        if area != "0":
            shortened_config.append(f"area: {area}")

    if category_enabled(config, "frame blending") == "true":
        shortened_config.append("\n[frame blending]")
        shortened_config.append(f"fps: {basic_value(config, "frame blending", "fps", "60")}")
        shortened_config.append(f"intensity: {basic_value(config, "frame blending", "intensity", "1.0")}")
        shortened_config.append(f"weighting: {blending_weighting(config)}")
        bright_blend = bool_value(config, "frame blending", key="bright blend")
        if bright_blend in YES:
            shortened_config.append(f"bright blend: {bright_blend}")

    if category_enabled(config, "flowblur") == "true":
        shortened_config.append("\n[flowblur]")
        if category_masking(config, "flowblur"):
            shortened_config.append("masking: yes")
        if has_key(config, "flowblur", "amount"):
            shortened_config.append(f"amount: {config['flowblur']['amount']}")
        if has_key(config, "flowblur", "do blending"):
            shortened_config.append(
                f"do blending: {config['flowblur']['do blending']}"
            )

    if category_enabled(config, "artifact masking") == "true":
        shortened_config.append("\n[artifact masking]")
        if bool_value(config, "artifact masking", key="feathering") == "true":
            shortened_config.append("feathering: yes")
        if has_key(config, "artifact masking", "file name"):
            shortened_config.append(
                f"file name: {config['artifact masking']['file name']}"
            )

    in_time = float(basic_value(config, "timescale", "in", "1.0"))
    out_time = float(basic_value(config, "timescale", "in", "1.0"))
    if in_time != 1.0 or out_time != 1.0:
        shortened_config.append("\n[timescale]")
        if in_time != 1.0:
            shortened_config.append(f"in: {in_time}")
        if out_time != 1.0:
            shortened_config.append(f"out: {in_time}")

    if category_enabled(config, "pre-interp") == "true":
        shortened_config.append("\n[pre-interp]")
        if category_masking(config, "pre-interp"):
            shortened_config.append("masking: yes")
        shortened_config.append(f"factor: {config['pre-interp']['factor']}")
    return "\n".join(shortened_config)


# this is a mess


def calculate_vegas(config):
    return f"""[interpolation]
enabled: {category_enabled(config, category="interpolation")}
masking: {bool_value(config, "interpolation", "masking")}
fps: {interp_fps(config)}
speed: {basic_value(config, "interpolation", "speed", "medium")}
tuning: {basic_value(config, "interpolation", "tuning", "weak")}
algorithm: {basic_value(config, "interpolation", "algorithm", "23")}
use gpu: {bool_value(config, "interpolation", "use gpu")}
area: {basic_value(config, "interpolation", "area", "0")}

[frame blending]
enabled: {category_enabled(config, "frame blending")}
fps: {basic_value(config, "frame blending", "fps", "60")}
intensity: {basic_value(config, "frame blending", "intensity", "1.0")}
weighting: vegas
bright blend: {bool_value(config, "frame blending", "bright blend")}

[flowblur]
enabled: {category_enabled(config, "flowblur")}
masking: {bool_value(config, "flowblur", "masking")}
amount: {basic_value(config, "flowblur", "amount", "125")}
do blending: {basic_value(config, "flowblur", "do blending", "after")}

[output]
process: {basic_value(config, "output", "process", "ffmpeg")}
enc args: {basic_value(config, "output", "enc args", "H264 CPU")}
file format: {basic_value(config, "output", "file format", r"%FILENAME% ~ %FRUIT%")}
container: {basic_value(config, "output", "container", ".MP4")}

[preview window]
enabled: {category_enabled(config, "preview window")}
process: {basic_value(config, "preview window", "process", "ffplay")}
output args: {basic_value(config, "preview window", "output args", "-f yuv4mpegpipe -")}

[artifact masking]
enabled: {category_enabled(config, "artifact masking")}
feathering: {bool_value(config, "artifact masking", "feathering")}
folder path: {basic_value(config, "artifact masking", "folder path", "")}
file name: {basic_value(config, "artifact masking", "file name", "")}

[miscellaneous]
play ding: {bool_value(config, "miscellaneous", "play ding")}
always verbose: {bool_value(config, "miscellaneous", "always verbose")}
dedup threshold: {basic_value(config, "miscellaneous", "dedup threshold", "0.0")}
global output folder: {basic_value(config, "miscellaneous", "global output folder", "")}
source indexing: {bool_value(config, "miscellaneous", "source indexing")}
ffmpeg options: {basic_value(config, "miscellaneous", "ffmpeg options", "-loglevel error -i - -hide_banner -stats -stats_period 0.15")}
ffplay options: {basic_value(config, "miscellaneous", "ffplay options", "-loglevel quiet -i - -autoexit -window_title smoothie.preview")}

[console]
stay on top: {bool_value(config, "console", "stay on top")}
borderless: {bool_value(config, "console", "borderless")}
position: {basic_value(config, "console", "position", "top left")}
width: {basic_value(config, "console", "width", "900")}
height: {basic_value(config, "console", "height", "350")}

[timescale]
in: {basic_value(config, "timescale", "in", "1.0")}
out: {basic_value(config, "timescale", "out", "1.0")}

[color grading]
enabled: {category_enabled(config, "color grading")}
brightness: {basic_value(config, "color grading", "brightness", "1.0")}
saturation: {basic_value(config, "color grading", "saturation", "1.0")}
contrast: {basic_value(config, "color grading", "contrast", "1.0")}
hue: {basic_value(config, "color grading", "hue", "0")}
coring: {bool_value(config, "color grading", "coring")}

[lut]
enabled: {category_enabled(config, "lut",)}
path: {basic_value(config, "lut", "path", "")}
opacity: {basic_value(config, "lut", "opacity", "0.2")}

[pre-interp]
enabled: {category_enabled(config, "pre-interp")}
masking: {bool_value(config, "pre-interp", "masking")}
factor: {basic_value(config, "pre-interp", "factor", "3x")}
model: {basic_value(config, "pre-interp", "model", "rife-v4.4")}"""
