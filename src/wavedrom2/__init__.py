# MIT License
#
# Copyright (c) 2011-2019 Aliaksei Chapyzhenka, BreizhGeek, Kazuki Yamamoto,
#                         MutantPlatypus, Stefan Wallentowitz, Benjamin Davis
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.

from __future__ import annotations
from typing import Optional, IO, AnyStr

import argparse
import json
import yaml
import sys
import os

import svgwrite

from .waveform import WaveDrom
from .assign import Assign
from .bitfield import BitField


def fix_quotes(bad_string: str) -> str:
    # fix double quotes in the input file. opening with yaml and dumping with json fix the issues.
    yaml_code = yaml.load(bad_string, Loader=yaml.FullLoader)
    fixed_string = json.dumps(yaml_code, indent=4)
    return fixed_string


def render(
    source: str = "",
    output: Optional[list] = None,
    strict_js_features: bool = False
) -> svgwrite.Drawing:
    if output is None:
        output = []

    source = json.loads(fix_quotes(source))
    if not isinstance(source, dict):
        raise TypeError("Source must be a dictionary")

    if source.get("signal"):
        return WaveDrom().render_waveform(0, source, output, strict_js_features)
    elif source.get("assign"):
        return Assign().render(0, source, output)
    elif source.get("reg"):
        return BitField().renderJson(source)


def render_write(source: IO[str], output: IO[AnyStr], strict_js_features: bool = False) -> None:
    jinput = source.read()
    out = render(jinput, strict_js_features=strict_js_features)
    out.write(output)


def render_file(source: os.PathLike, output: os.PathLike, strict_js_features: bool = False) -> None:
    out = open(output, "w")
    render_write(open(source, "r"), out, strict_js_features=strict_js_features)
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
