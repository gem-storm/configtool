from constants import YES, ENC_PRESETS
import configparser


def bool_value(config, category, key):
    if config.has_option(category, key):
        if config.get(category, key) in YES:
            return "true"
    return "false"


def float_value(config, category, key):
    if config.has_option(category, key):
        return config.get(category, key)
    return "1.0"


def category_enabled(config, category):
    if config.has_section(category):
        if config.has_option(category, "enabled"):
            if config.get(category, "enabled") in YES:
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
    if config.has_option("interpolation", "fps"):
        if "x" not in config.get("interpolation", "fps"):
            return int(config.get("interpolation", "fps"))
        return config.get("interpolation", "fps")
    return 1920


def interp_speed(config):
    if config.has_option("interpolation", "speed"):
        return config.get("interpolation", "speed")
    return "medium"


def interp_tuning(config):
    if config.has_option("interpolation", "tuning"):
        return config.get("interpolation", "tuning")
    return "weak"


def interp_algorithm(config):
    if config.has_option("interpolation", "algorithm"):
        return config.get("interpolation", "algorithm")
    return "23"


def interp_area(config):
    if config.has_option("interpolation", "area"):
        return config.get("interpolation", "area")
    return "0"


def blending_fps(config):
    if config.has_option("frame blending", "fps"):
        return int(config.get("frame blending", "fps"))
    return 60


def blending_intensity(config):
    if config.has_option("frame blending", "intensity"):
        return float(config.get("frame blending", "intensity"))
    return 1.0


def convert_weighting(config):
    raw_weighting = config.get("frame blending", "weighting")
    weighting = raw_weighting.split(";")[0]
    if weighting == "vegas":
        if category_enabled(config, category="interpolation") == "true" and isinstance(
            interp_fps(config), int
        ):
            blurframes = int(
                interp_fps(config) / blending_fps(config) * blending_intensity(config)
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
    if config.has_option("frame blending", "weighting"):
        return convert_weighting(config)
    return "equal"


def blending_std_dev(config):
    if config.has_option("frame blending", "weighting"):
        weighting_split = config.get("frame blending", "weighting").split(";")
        for value in weighting_split:
            if "std_dev" in value:
                return value.split("=")[1].strip()
    return "1"


def blending_bound(config):
    if config.has_option("frame blending", "weighting"):
        weighting_split = config.get("frame blending", "weighting").split(";")
        for value in weighting_split:
            if "bound" in value:
                return value.split("=")[1].strip()
    return "[0,2]"


def blending_apex(config):
    if config.has_option("frame blending", "weighting"):
        weighting_split = config.get("frame blending", "weighting").split(";")
        for value in weighting_split:
            if "apex" in value:
                return value.split("=")[1].strip()
    return "[0,2]"


def reverse_weights(config):
    if config.has_option("frame blending", "weighting"):
        if config.get("frame blending", "weighting") == "descending":
            return "true"
    return "false"


def output_encoding_args(config):
    enc_arg_presets = configparser.ConfigParser()
    enc_arg_presets.read_string(ENC_PRESETS)

    if config.has_option("output", "enc args"):
        input_enc_args = config.get("output", "enc args")
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
    if config.has_option("output", "container"):
        return config.get("output", "container").removeprefix(".").lower()
    return "mp4"


def misc_deduplicate(config):
    if config.has_option("miscellaneous", "dedup threshold"):
        if float(config.get("miscellaneous", "dedup threshold")) > 0.0:
            return "true"
    return "false"


def color(config, key):
    if config.has_option("color grading", "enabled"):
        if config.get("color grading", "enabled") in YES:
            float_value(config, category="color grading", key=key)
    return "1.0"


def make_18_config(config):
    return f"""- blur
blur: {category_enabled(config, category="frame blending")}
blur amount: {blending_intensity(config)}
blur output fps: {blending_fps(config)}
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
interpolation speed: {interp_speed(config)}
interpolation tuning: {interp_tuning(config)}
interpolation algorithm: {interp_algorithm(config)}"""


def make_192_config(config):
    return f"""[blur v1.9]
- blur
blur: {category_enabled(config, category="frame blending")}
blur amount: {blending_intensity(config)}
blur output fps: {blending_fps(config)}
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
interpolation preset: {interp_tuning(config)}
interpolation algorithm: {interp_algorithm(config)}
interpolation block size: 8
interpolation speed: {interp_speed(config)}
interpolation mask area: {interp_area(config)}"""


def choose_program(config):
    blur_version = input(
        """
Convert to:
    (1) Blur v1.8
    (2) Blur v1.92
"""
    ).lower()
    if blur_version in ["1", "(1)", "1.8", "blur v1.8"]:
        return make_18_config(config)
    if blur_version in ["2", "(2)", "1.92", "blur v1.92"]:
        return make_192_config(config)
    print("Not recognized as an option!")
    return choose_program(config)


def shorten(config):
    shortened_config = []
    if category_enabled(config, category="interpolation") == "true":
        shortened_config.append("[interpolation]")
        if category_masking(config, category="interpolation"):
            shortened_config.append("masking: yes")
        shortened_config.append(f"fps: {interp_fps(config)}")
        shortened_config.append(f"speed: {interp_speed(config)}")
        shortened_config.append(f"tuning: {interp_tuning(config)}")
        shortened_config.append(f"algorithm: {interp_algorithm(config)}")
        area = interp_area(config)
        if area != "0":
            shortened_config.append(f"area: {area}")

    if category_enabled(config, category="frame blending") == "true":
        shortened_config.append("\n[frame blending]")
        shortened_config.append(f"fps: {blending_fps(config)}")
        shortened_config.append(f"intensity: {blending_intensity(config)}")
        shortened_config.append(f"weighting: {blending_weighting(config)}")
        bright_blend = bool_value(config, category="frame blending", key="bright blend")
        if bright_blend in YES:
            shortened_config.append(f"bright blend: {bright_blend}")

    if category_enabled(config, category="flowblur") == "true":
        shortened_config.append("\n[flowblur]")
        if category_masking(config, category="flowblur"):
            shortened_config.append("masking: yes")
        if config.has_option("flowblur", "amount"):
            shortened_config.append(f"amount: {config.get('flowblur', 'amount')}")
        if config.has_option("flowblur", "do blending"):
            shortened_config.append(
                f"do blending: {config.get('flowblur', 'do blending')}"
            )

    if category_enabled(config, category="artifact masking") == "true":
        shortened_config.append("\n[artifact masking]")
        if bool_value(config, category="artifact masking", key="feathering") == "true":
            shortened_config.append("feathering: yes")
        if config.has_option("artifact masking", "file name"):
            shortened_config.append(
                f"file name: {config.get('artifact masking', 'file name')}"
            )

    in_time = float(float_value(config, category="timescale", key="in"))
    out_time = float(float_value(config, category="timescale", key="out"))
    if in_time != 1.0 or out_time != 1.0:
        shortened_config.append("\n[timescale]")
        if in_time != 1.0:
            shortened_config.append(f"in: {in_time}")
        if out_time != 1.0:
            shortened_config.append(f"out: {in_time}")

    if category_enabled(config, category="pre-interp") == "true":
        shortened_config.append("\n[pre-interp]")
        if category_masking(config, category="pre-interp"):
            shortened_config.append("masking: yes")
        shortened_config.append(f"factor: {config.get('pre-interp', 'factor')}")
    return "\n".join(shortened_config)


# this is a mess
