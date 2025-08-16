# MIT License
#
# Copyright (c) 2011-2025 Aliaksei Chapyzhenka, BreizhGeek, Kazuki Yamamoto,
#                         MutantPlatypus, Stefan Wallentowitz, Benjamin Davis
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
"""Module which contains the information about wave-skin styles"""

from __future__ import annotations

from .dark import DARK_CSS, DARK_WAVESKIN
from .default import DEFAULT_CSS, DEFAULT_WAVESKIN
from .lowkey import LOWKEY_CSS, LOWKEY_WAVESKIN
from .narrow import NARROW_CSS, NARROW_WAVESKIN
from .narrower import NARROWER_CSS, NARROWER_WAVESKIN
from .narrowerer import NARROWERER_CSS, NARROWERER_WAVESKIN
from .typing import WaveSkin, _WaveSkinElement

__all__ = [
    "DARK_CSS",
    "DARK_WAVESKIN",
    "DEFAULT_CSS",
    "DEFAULT_WAVESKIN",
    "LOWKEY_CSS",
    "LOWKEY_WAVESKIN",
    "NARROW_CSS",
    "NARROW_WAVESKIN",
    "NARROWER_CSS",
    "NARROWER_WAVESKIN",
    "NARROWERER_CSS",
    "NARROWERER_WAVESKIN",
    "get_waveskin",
]


SVG_IDX = 0
"""Index of the 'svg' string in the waveskin"""

SVG_HEADER_ATTRS_IDX = 1
"""Index of the SVG header attributes in the waveskin (such as xmlns, id=svg, etc.)"""

SVG_STYLE_IDX = 2
"""Index of the SVG style element in the waveskin"""

SVG_DEFS_IDX = 3
"""Index of the SVG definitions element in the waveskin"""
SVG_DEFS_SOCKET_GROUP_IDX = 1
"""Index of the SVG socket group element in the waveskin"""
SVG_DEFS_SOCKET_GROUP_RECT_IDX = 2
"""Index of the SVG socket group rectangle element in the waveskin"""
SVG_DEFS_SOCKET_GROUP_RECT_ATTRS_IDX = 1
"""Index of the SVG socket group rectangle attributes element in the waveskin"""

SVG_GROUP_IDX = 4
"""Index of the SVG group element in the waveskin"""


def get_waveskin(style_name: str) -> WaveSkin:
    """Get the wave skin by name."""
    if style_name == "dark":
        return DARK_WAVESKIN
    elif style_name == "default":
        return DEFAULT_WAVESKIN
    elif style_name == "lowkey":
        return LOWKEY_WAVESKIN
    elif style_name == "narrow":
        return NARROW_WAVESKIN
    elif style_name == "narrower":
        return NARROWER_WAVESKIN
    elif style_name == "narrowerer":
        return NARROWERER_WAVESKIN
    else:
        raise ValueError(f"Unknown wave skin style: {style_name}")


def get_waveskin_css(style_name: str) -> str:
    """Get the CSS for the wave skin by name."""
    if style_name == "dark":
        return DARK_CSS
    elif style_name == "default":
        return DEFAULT_CSS
    elif style_name == "lowkey":
        return LOWKEY_CSS
    elif style_name == "narrow":
        return NARROW_CSS
    elif style_name == "narrower":
        return NARROWER_CSS
    elif style_name == "narrowerer":
        return NARROWERER_CSS
    else:
        raise ValueError(f"Unknown wave skin style: {style_name}")


def _get_waveskin_socket_attr(waveskin: WaveSkin, waveskin_attr: str) -> str | int | float:
    """Get the width of the socket in the wave skin."""
    defs = waveskin[SVG_DEFS_IDX]
    if not isinstance(defs, list) or len(defs) < SVG_DEFS_SOCKET_GROUP_IDX:
        raise ValueError("Invalid waveskin: missing socket group definition")

    socket_group = defs[SVG_DEFS_SOCKET_GROUP_IDX]
    if not isinstance(socket_group, list) or len(socket_group) < SVG_DEFS_SOCKET_GROUP_RECT_IDX:
        raise ValueError("Invalid waveskin: missing socket group rectangle definition")

    socket_rect = socket_group[SVG_DEFS_SOCKET_GROUP_RECT_IDX]
    if not isinstance(socket_rect, list) or len(socket_rect) < SVG_DEFS_SOCKET_GROUP_RECT_ATTRS_IDX:
        raise ValueError("Invalid waveskin: missing socket group rectangle attributes definition")

    socket_rect_attrs = socket_rect[SVG_DEFS_SOCKET_GROUP_RECT_ATTRS_IDX]
    if not isinstance(socket_rect_attrs, dict) or "width" not in socket_rect_attrs:
        raise ValueError("Invalid waveskin: missing socket width attribute")

    return socket_rect_attrs[waveskin_attr]


def get_waveskin_socket_width(waveskin: WaveSkin) -> int:
    """Get the width of the socket in the wave skin."""
    return int(_get_waveskin_socket_attr(waveskin, "width"))


def get_waveskin_socket_height(waveskin: WaveSkin) -> int:
    """Get the height of the socket in the wave skin."""
    return int(_get_waveskin_socket_attr(waveskin, "height"))


def get_waveskin_socket_x(waveskin: WaveSkin) -> int:
    """Get the x position of the socket in the wave skin."""
    return int(_get_waveskin_socket_attr(waveskin, "x"))


def get_waveskin_socket_y(waveskin: WaveSkin) -> int:
    """Get the y position of the socket in the wave skin."""
    return int(_get_waveskin_socket_attr(waveskin, "y"))


def get_waveskin_defs(waveskin: WaveSkin) -> list[_WaveSkinElement]:
    """Get the definitions from the wave skin."""
    defs = waveskin[SVG_DEFS_IDX]
    if not isinstance(defs, list):
        raise ValueError("Invalid waveskin: missing definitions")
    return defs[1:]  # Skip the first element which is the 'defs' tag itself