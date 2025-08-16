# MIT License
#
# Copyright (c) 2025 WaveDromPy2 Contributors
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.

from __future__ import annotations

from typing import Dict, List, Union

_WaveSkinElement = Union[str, Dict[str, Union[str, int, float]], List["_WaveSkinElement"]]

WaveSkin = List[_WaveSkinElement]
