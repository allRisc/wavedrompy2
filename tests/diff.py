
from __future__ import annotations

import io
import pathlib
import re
import xml.etree.ElementTree as ET
from collections import namedtuple
from dataclasses import dataclass
from xml.etree.ElementTree import Element

import cairosvg
from PIL import Image, ImageChops

UpdateAttribx = namedtuple("UpdateAttribx", 'node name value old')
MoveNodex = namedtuple("MoveNodex", 'node target position nodex targetx')


@dataclass
class DiffMismatch:
    node: Element

    def __str__(self):
        return f"{type(self).__name__}(node={self.node.tag}, attrib={self.node.attrib})"

@dataclass
class DiffTagMismatch(DiffMismatch):
    lhs_tag: str
    rhs_tag: str

    def __str__(self):
        return f"{type(self).__name__}(node={self.node.tag}, lhs_tag={self.lhs_tag}, rhs_tag={self.rhs_tag})"

@dataclass
class DiffAttrMismatch(DiffMismatch):
    attr: str
    lhs_value: str
    rhs_value: str

    def __str__(self):
        return f"{type(self).__name__}(node={self.node.tag}, attr={self.attr}, lhs_value={self.lhs_value}, rhs_value={self.rhs_value})"

@dataclass
class DiffTextMismatch(DiffMismatch):
    lhs_text: str
    rhs_text: str

    def __str__(self):
        return f"{type(self).__name__}(node={self.node.tag}, lhs_text={self.lhs_text}, rhs_text={self.rhs_text})"

@dataclass
class DiffChildMissing(DiffMismatch):
    child: DiffElement

    def __str__(self):
        return f"{type(self).__name__}(node={self.node.tag}, child={self.child})"


IGNORED_ATTRS: list[str] = ["baseProfile", "version"]
IGNORED_TAGS: list[str] = []


def same_attr_text(attr: str, lhs: str, rhs: str) -> bool:
    if attr in IGNORED_ATTRS:
        return True
    if attr == "viewBox":
        # The viewBox format differs, both are legal notations (space vs. comma-separated)
        return re.sub(r"\s+", ",", lhs) == re.sub(r"\s+", ",", rhs)

    if attr in ['d']:
        lhs = lhs.replace(".0", "").replace(", ", ",")
        rhs = rhs.replace(".0", "").replace(", ", ",")
        return lhs == rhs

    if attr in ['transform', 'x', 'y']:
        pattern_float = re.compile(r'(.*?)([\d\.,]+)(.*)')
        lhs_match = re.fullmatch(pattern_float, lhs)
        rhs_match = re.fullmatch(pattern_float, rhs)

        if lhs_match is not None and rhs_match is not None:
            if lhs_match.group(1) != rhs_match.group(1):
                return False
            if lhs_match.group(3) != rhs_match.group(3):
                return False

            lhs_numbers = [float(val) for val in lhs_match.group(2).split(",")]
            rhs_numbers = [float(val) for val in rhs_match.group(2).split(",")]
            if len(lhs_numbers) > len(rhs_numbers):
                rhs_numbers.extend([0.0] * (len(lhs_numbers) - len(rhs_numbers)))
            elif len(rhs_numbers) > len(lhs_numbers):
                lhs_numbers.extend([0.0] * (len(rhs_numbers) - len(lhs_numbers)))

            if lhs_numbers != rhs_numbers:
                return False
            return True

    return re.sub(r"\s+", "", lhs) == re.sub(r"\s+", "", rhs)


class DiffElement:

    def __init__(self, el: Element):
        self._el = el

        self.tag = el.tag
        self.attrib = el.attrib
        self.text = el.text.strip() if el.text else ""
        self.tail = el.tail.strip() if el.tail else ""
        self.children = [DiffElement(child) for child in el]

        self._id_children: dict[str, DiffElement] = {}
        self._tag_children: dict[str, list] = {}

        for child in self.children:
            if "id" not in child.attrib:
                if child.tag not in self._tag_children:
                    self._tag_children[child.tag] = []
                self._tag_children[child.tag].append(child)
            else:
                self._id_children[child.attrib["id"]] = child

    def compare(self, rhs: DiffElement) -> list[DiffMismatch]:

        if self.tag != rhs.tag:
            return [DiffTagMismatch(self._el, self.tag, rhs.tag)]

        if self.tag in IGNORED_TAGS:
            return []

        for attr in self.attrib:
            if attr in IGNORED_ATTRS:
                continue
            if attr not in rhs.attrib:
                if attr in ['x', 'y'] and self.attrib[attr] == "0":
                    continue
                return [DiffAttrMismatch(self._el, attr, self.attrib[attr], "")]
            if not same_attr_text(attr, self.attrib[attr], rhs.attrib[attr]):
                return [DiffAttrMismatch(self._el, attr, self.attrib[attr], rhs.attrib[attr])]

        for attr in rhs.attrib:
            if attr in IGNORED_ATTRS:
                continue
            if attr not in self.attrib :
                if attr in ['x', 'y'] and rhs.attrib[attr] == "0":
                    continue
                return [DiffAttrMismatch(self._el, attr, "", rhs.attrib[attr])]

        if re.sub(r"\s+", "", self.text) != re.sub(r"\s+", "", rhs.text):
            return [DiffTextMismatch(self._el, self.text, rhs.text)]

        ret_val: list[DiffMismatch] = []
        for child in self.children:
            if "id" in child.attrib:
                rhs_child = rhs._id_children.get(child.attrib.get("id"), None)
                if rhs_child is None:
                    ret_val.append(DiffChildMissing(self._el, child))
                    continue
                else:
                    ret_val.extend(child.compare(rhs_child))
            elif child.tag in rhs._tag_children:
                best_rhs_child = None
                for rhs_child in rhs._tag_children[child.tag]:
                    rhs_child_ret_val = child.compare(rhs_child)
                    if best_rhs_child is None:
                        best_rhs_child = rhs_child_ret_val
                    elif len(rhs_child_ret_val) < len(best_rhs_child):
                        best_rhs_child = rhs_child_ret_val

                if best_rhs_child is None:
                    ret_val.append(DiffChildMissing(self._el, child))
                else:
                    ret_val.extend(best_rhs_child)
            else:
                ret_val.append(DiffChildMissing(self._el, child))

        return ret_val

    def match_child(self, child: DiffElement) -> DiffElement | None:
        for self_child in self.children:
            if self_child.tag != child.tag:
                continue
            if not self_child.same_attributes(child):
                continue
            return self_child
        return None

    def same_attributes(self, rhs: DiffElement) -> bool:
        for attr in self.attrib:
            if attr not in rhs.attrib:
                if attr in ['x', 'y'] and self.attrib[attr] == "0":
                    continue
                return False

            if not same_attr_text(attr, self.attrib[attr], rhs.attrib[attr]):
                return False

        for attr in rhs.attrib:
            if attr not in self.attrib:
                if attr in ['x', 'y'] and rhs.attrib[attr] == "0":
                    continue
                return False

        return True

    def __str__(self):
        return f"DiffElement(tag={self.tag}, attrib={self.attrib})"


def diff_xml(f_out_js: str | pathlib.Path, f_out_py: str | pathlib.Path) -> list[DiffMismatch]:
    """Perform a diff between the JS and Python XML WaveDrom renders.

    Args:
        f_out_js (str | pathlib.Path): The path to the JS output file.
        f_out_py (str | pathlib.Path): The path to the Python output file.

    Returns:
        _type_: _description_
    """
    f_tree_js = ET.parse(f_out_js)
    f_root_js = f_tree_js.getroot()

    f_tree_py = ET.parse(f_out_py)
    f_root_py = f_tree_py.getroot()

    diff = DiffElement(f_root_js).compare(DiffElement(f_root_py))

    unknown = []

    for action in diff:
        if isinstance(action, DiffChildMissing):
            if action.child.tag.endswith("}g") and len(action.child.attrib) == 0:
                continue
        unknown.append(action)

    return unknown


def diff_raster(f_out_js: str | pathlib.Path, f_out_py: str | pathlib.Path) -> Image:
    """Compare the raster output of the JavaScript and Python WaveDrom renderers.

    Args:
        f_out_js (str | pathlib.Path): The path to the JS output file.
        f_out_py (str | pathlib.Path): The path to the Python output file.

    Returns:
        Image: The image showing the differences between the two outputs. This will have a
            empty bounding box if there are no differences.
    """
    with open(f_out_js, encoding="utf-8") as fileObj_svg_js:
        svg_js = fileObj_svg_js.read()

    with open(f_out_py, encoding="utf-8") as fileObj_svg_py:
        svg_py = fileObj_svg_py.read()

    png_js = cairosvg.svg2png(svg_js)
    png_py = cairosvg.svg2png(svg_py)

    image_js = Image.open(io.BytesIO(png_js))
    image_py = Image.open(io.BytesIO(png_py))

    return ImageChops.difference(image_js, image_py)
