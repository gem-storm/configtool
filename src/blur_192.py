def weighting(config):
    weighting = config["blur weighting"]

    if config["interpolate"] == "true" and "x" not in config["interpolated fps"]:
        blurframes = int(
            int(config["interpolated fps"]) / int(config["blur output fps"])
        )
        if blurframes % 2 == 0:
            vegas = "[1," + "2," * (blurframes - 1) + "1]"
            if weighting == vegas:
                return "vegas"
    match weighting:
        case "pyramid":
            if config["blur weighting triangle reverse"] == "true":
                return "descending"
            return "ascending"
        case "pyramid_sym":
            return "pyramid"
        case "gaussian_sym":
            std_dev = f"std_dev = {config['blur weighting gaussian std dev']}"
            bound = f"bound = {config['blur weighting bound']}"
            return f"gaussian_sym; {std_dev}; {bound}"
    return weighting


def deduplicate(config):
    match config["deduplicate"]:
        case "true":
            return "0.001"
    return "0.0"


def make_config(config):
    return f"""- blur
blur: {config["blur"]}
blur amount: {config["blur amount"]}
blur output fps: {config["blur output fps"]}
blur weighting: {config["blur weighting"]}

- interpolation
interpolate: {config["interpolate"]}
interpolated fps: {config["interpolated fps"]}

- rendering
quality: 18
preview: {config["preview"]}
detailed filenames: {config["detailed filenames"]}

- timescale
input timescale: {config["input timescale"]}
output timescale: {config["output timescale"]}
adjust timescaled audio pitch: {config["adjust timescaled audio pitch"]}

- filters
brightness: {config["brightness"]}
saturation: {config["saturation"]}
contrast: {config["contrast"]}

- advanced rendering
gpu: {config["gpu rendering"]}
gpu type (nvidia/amd/intel): {config["gpu type (nvidia/amd/intel)"]}
deduplicate: {config["deduplicate"]}
custom ffmpeg filters: {config["custom ffmpeg filters"]}

- advanced blur
blur weighting gaussian std dev: {config["blur weighting gaussian std dev"]}
blur weighting triangle reverse: {config["blur weighting triangle reverse"]}
blur weighting bound: {config["blur weighting bound"]}

- advanced interpolation
interpolation program (svp/rife/rife-ncnn): svp
interpolation speed: {config["interpolation speed"]}
interpolation tuning: {config["interpolation preset"]}
interpolation algorithm: {config["interpolation algorithm"]}"""


def make_recipe(config):
    """
    Makes the converted smoothie recipe.
    """
    return f"""[interpolation]
enabled: {config["interpolate"]}
masking: false
fps: {config["interpolated fps"]}
speed: {config["interpolation speed"]}
tuning: {config["interpolation preset"]}
algorithm: {config["interpolation algorithm"]}
use gpu: {config["gpu interpolation"]}
area: {config["interpolation mask area"]}

[frame blending]
enabled: {config["blur"]}
fps: {config["blur output fps"]}
intensity: {config["blur amount"]}
weighting: {weighting(config)}
bright blend: false

[flowblur]
enabled: false
masking: false
amount: 100
do blending: after

[output]
process: ffmpeg
enc args: {config["custom ffmpeg filters"]}
file format: %FILENAME%
container: .{config["video container"]}

[preview window]
enabled: {config["preview"]}
process: ffplay
output args: -f yuv4mpegpipe -

[artifact masking]
enabled: false
feathering: false
folder path:
file name:

[miscellaneous]
play ding: false
always verbose: false
dedup threshold: {deduplicate(config)}
global output folder:
source indexing: false
ffmpeg options: -loglevel error -i - -hide_banner -stats -stats_period 0.15
ffplay options: -loglevel quiet -i - -autoexit -window_title smoothie.preview

[console]
stay on top: false
borderless: true
position: top left
width: 900
height: 350

[timescale]
in: {config["input timescale"]}
out: {config["output timescale"]}

[color grading]
enabled: true
brightness: {config["brightness"]}
saturation: {config["saturation"]}
contrast: {config["contrast"]}
hue: 0
coring: false

[lut]
enabled: false
path:
opacity: 0.2

[pre-interp]
enabled: false
masking: false
factor: 2x
model: rife-v4.6"""


def choose_program(config):
    choice = input(
        """
Convert to:
    (1) Blur 1.8
    (2) Smoothie
"""
    ).lower()

    if choice in ["1", "(1)", "blur", "1.8", "blur 1.8"]:
        return make_config(config)
    if choice in ["2", "(2)", "smoothie"]:
        return make_recipe(config)

    print("Not an option!")
    return choose_program(config)


def calculate_vegas(config):
    match config["interpolate"]:
        case "true":
            blurframes = int(
                int(config["interpolated fps"])
                / int(config["blur output fps"])
                * float(config["blur amount"])
            )
        case "false":
            blurframes = int(
                int(input("Interpolation is disabled, what's the input video's fps?: "))
                / int(config["blur output fps"])
                * int(config["blur amount"])
            )
    if blurframes % 2 == 0:
        weighting = "[1," + "2," * (blurframes - 1) + "1]"
    else:
        weighting = "equal"
    return f"""[blur v1.9]
- blur
blur: {config["blur"]}
blur amount: {config["blur amount"]}
blur output fps: {config["blur output fps"]}
blur weighting: {weighting}

- interpolation
interpolate: {config["interpolate"]}
interpolated fps: {config["interpolated fps"]}

- rendering
quality: {config["quality"]}
deduplicate: {config["deduplicate"]}
preview: {config["preview"]}
detailed filenames: {config["detailed filenames"]}

- timescale
input timescale: {config["input timescale"]}
output timescale: {config["output timescale"]}
adjust timescaled audio pitch: {config["adjust timescaled audio pitch"]}

- filters
brightness: {config["brightness"]}
saturation: {config["saturation"]}
contrast: {config["contrast"]}

- advanced rendering
gpu interpolation: {config["gpu interpolation"]}
gpu rendering: {config["gpu rendering"]}
gpu type (nvidia/amd/intel): {config["gpu type (nvidia/amd/intel)"]}
video container: {config["video container"]}
custom ffmpeg filters: {config["custom ffmpeg filters"]}

- advanced blur
blur weighting gaussian std dev: {config["blur weighting gaussian std dev"]}
blur weighting triangle reverse: {config["blur weighting triangle reverse"]}
blur weighting bound: {config["blur weighting bound"]}

- advanced interpolation
interpolation preset: {config["interpolation preset"]}
interpolation algorithm: {config["interpolation algorithm"]}
interpolation block size: {config["interpolation block size"]}
interpolation speed: {config["interpolation speed"]}
interpolation mask area: {config["interpolation mask area"]}
"""


def shorten(config):
    shortened_config = []
    if config["blur"] == "true":
        shortened_config.append(
            f"""- blur")
blur amount: {config['blur amount']}
blur output fps: {config['blur output fps']}
blur weighting: {config['blur weighting']}"""
        )

    if config["interpolate"] == "true":
        shortened_config.append(
            f"""\n- interpolation
interpolated fps: {config['interpolated fps']}"""
        )

    in_time = float(config["input timescale"])
    out_time = float(config["output timescale"])
    if in_time != 1.0 or out_time != 1.0:
        shortened_config.append("\n- timescale")
        if in_time != 1.0:
            shortened_config.append(f"input timescale: {config['input timescale']}")
        if out_time != 1.0:
            shortened_config.append(f"output timescale: {config['output timescale']}")

    if config["blur weighting"] in ["gaussian", "gaussian_sym", "pyramid"]:
        shortened_config.append("\n- advanced blur")
        if config["blur weighting"].startswith("gaussian"):
            shortened_config.append(
                f"""blur weighting gaussian std dev: {config['blur weighting gaussian std dev']}
blur weighting bound: {config['blur weighting bound']}"""
            )
        if config["blur weighting"] == "pyramid":
            shortened_config.append(
                f"blur weighting triangle reverse: {config['blur weighting triangle reverse']}"
            )

    if config["interpolate"] == "true":
        shortened_config.append(
            f"""\n- advanced interpolation
interpolation preset: {config['interpolation preset']}
interpolation algorithm: {config['interpolation algorithm']}"""
        )
        if config["interpolation block size"] != "8":
            shortened_config.append(
                f"interpolation block size: {config['interpolation block size']}"
            )
        shortened_config.append(f"interpolation speed: {config['interpolation speed']}")
        if config["interpolation mask area"] != "0":
            shortened_config.append(
                f"interpolation mask area: {config['interpolation mask area']}"
            )
    return "\n".join(shortened_config)
