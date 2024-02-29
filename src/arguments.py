import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    help="input config/recipe's path",
)
parser.add_argument(
    "--output",
    help="output config format. options: 'blur_1.8', 'blur_1.92', 'smoothie'",
)
parser.add_argument(
    "--shorten",
    help="shortens the config provided from --input",
    action="store_true",
)
parser.add_argument(
    "--vegas",
    help="calculates & applies vegas weights to the input config",
    action="store_true",
)
parser.add_argument(
    "--verbose",
    help="prints extra information for debugging",
    action="store_true",
)

args = parser.parse_args()
