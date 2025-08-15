# MIT License
#
# Copyright (c) 2011-2025 Aliaksei Chapyzhenka, BreizhGeek, Kazuki Yamamoto,
#                         MutantPlatypus, Stefan Wallentowitz, Benjamin Davis
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
"""Module which contains the information about wave-skin styles"""

from .dark import DARK_CSS, DARK_WAVESKIN
from .default import DEFAULT_CSS, DEFAULT_WAVESKIN
from .lowkey import LOWKEY_CSS, LOWKEY_WAVESKIN
from .narrow import NARROW_CSS, NARROW_WAVESKIN
from .narrower import NARROWER_CSS, NARROWER_WAVESKIN
from .narrowerer import NARROWERER_CSS, NARROWERER_WAVESKIN

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
]


def get_wave_skin(style_name: str) -> list:
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
