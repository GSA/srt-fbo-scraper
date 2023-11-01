from argparse import ArgumentParser
import sys
from pathlib import Path

base_dir = sys.prefix


def make_parser():
    parser = ArgumentParser()

    parser.add_argument(
        "-c",
        "--config",
        dest="_config",
        default=Path(base_dir, "conf", "config.yml"),
        required=False,
        help="Define general configuration with yaml file",
    )

    return parser
