# MIT License
#
# Copyright (c) 2011-2025 Aliaksei Chapyzhenka, BreizhGeek, Kazuki Yamamoto,
#                         MutantPlatypus, Stefan Wallentowitz, Benjamin Davis
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.

from __future__ import annotations

from collections.abc import Sequence

from svgwrite.base import BaseElement, Title
from svgwrite.container import Defs, Group, Marker, Style, Use
from svgwrite.path import Path
from svgwrite.shapes import Line, Rect
from svgwrite.text import Text, TSpan

from wavedrom2.waveskin.typing import _WaveSkinElement  # TODO: Move to a more common place

__all__ = [
    "Defs",
    "Group",
    "Marker",
    "Use",
    "Style",
    "Rect",
    "Path",
    "Text",
    "TSpan",
    "Title",
    "Line",
]


def get_container(ctype: str) -> BaseElement:
    """Get the container based on the string name.
    """
    if ctype in ['g', 'group']:
        return Group()

    if ctype == "defs":
        return Defs()

    if ctype == "marker":
        return Marker()

    if ctype == "style":
        return Style()

    raise ValueError(f"Unknown container type: {ctype}")


def _get_container_child(child_def: Sequence[_WaveSkinElement]) -> BaseElement:
    """Get the SVG container for a child element definition."""
    if not child_def:
        raise ValueError("Invalid child definition: empty list")

    ctype = child_def[0]

    if ctype == "path":
        child_attrs = child_def[1]
        if not isinstance(child_attrs, dict):
            raise ValueError(f"Invalid attributes for path element {ctype}: {child_attrs}")
        child = Path(d=child_attrs["d"])
        child.attribs = child_attrs
        return child

    if ctype == "rect":
        child_attrs = child_def[1]
        if not isinstance(child_attrs, dict):
            raise ValueError(f"Invalid attributes for rect element {ctype}: {child_attrs}")
        child = Rect(
            insert=(child_attrs["x"], child_attrs["y"]),
            size=(child_attrs["width"], child_attrs["height"])
        )
        child.attribs = child_attrs
        return child

    raise ValueError(f"Unknown child element type: {ctype}")


def get_container_element(element_def: Sequence[_WaveSkinElement]) -> BaseElement:
    """Get the SVG container for a list of element definitions."""
    ctype = element_def[0]
    if not isinstance(ctype, str):
        raise ValueError(f"Invalid container type: {ctype}")

    container = get_container(ctype)

    if not isinstance(element_def[1], dict):
        raise ValueError(f"Invalid attributes for container {ctype}: {element_def[1]}")
    container.attribs = element_def[1]

    for elem in element_def[2:]:
        if not isinstance(elem, list):
            raise ValueError(f"Invalid element definition: {elem}")
        container.add(_get_container_child(elem))
    return container
