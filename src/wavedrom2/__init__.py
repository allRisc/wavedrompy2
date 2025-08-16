# MIT License
#
# Copyright (c) 2011-2019 Aliaksei Chapyzhenka, BreizhGeek, Kazuki Yamamoto,
#                         MutantPlatypus, Stefan Wallentowitz, Benjamin Davis
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import IO, AnyStr

import svgwrite
import yaml

from .assign import Assign
from .bitfield import BitField
from .waveform import WaveDrom


def fix_quotes(bad_string: str) -> str:
    # fix double quotes in the input file. opening with yaml and dumping with json fix the issues.
    yaml_code = yaml.load(bad_string, Loader=yaml.FullLoader)
    fixed_string = json.dumps(yaml_code, indent=4)
    return fixed_string


def render(
    source: str = "",
    output: list | None = None,
    strict_js_features: bool = False
) -> svgwrite.Drawing:
    """Render a WaveDrom diagram from the provided string definition.

    Args:
        source (str, optional): The source string to use. Defaults to "".
        output (list | None, optional): The output list to use. Defaults to None.
        strict_js_features (bool, optional): Whether to use strict JavaScript features.
            Defaults to False.

    Raises:
        TypeError: If the source is not a dictionary.
        ValueError: If the source is an empty dictionary or it contains invalid data.

    Returns:
        svgwrite.Drawing: The rendered SVG drawing.
    """
    if output is None:
        output = []

    source_dict = json.loads(fix_quotes(source))
    if not isinstance(source_dict, dict):
        raise TypeError("Source must be a dictionary")

    if "signal" in source_dict:
        return WaveDrom().render_waveform(0, source_dict, output, strict_js_features)
    elif "assign" in source_dict:
        return Assign().render(0, source_dict, output)
    elif "reg" in source_dict:
        return BitField().renderJson(source_dict)
    else:
        raise ValueError("Invalid WaveDrom source")


def render_write(source: IO[str], output: IO[AnyStr], strict_js_features: bool = False) -> None:
    jinput = source.read()
    out = render(jinput, strict_js_features=strict_js_features)
    out.write(output)


def render_file(source: os.PathLike, output: os.PathLike, strict_js_features: bool = False) -> None:
    out = open(output, "w")
    render_write(open(source), out, strict_js_features=strict_js_features)
    out.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--input",
        "-i",
        help="<input wavedrom source filename>",
        required=True,
        type=argparse.FileType("r"),
    )
    parser.add_argument(
        "--svg",
        "-s",
        help="<output SVG image file name>",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    args = parser.parse_args()

    render_write(args.input, args.svg, False)
