# MIT License
#
# Copyright (c) 2011-2019 Aliaksei Chapyzhenka, BreizhGeek, Kazuki Yamamoto,
#                         MutantPlatypus, Stefan Wallentowitz, Benjamin Davis
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.

# Originally translated to Python from original file:
# https://github.com/drom/wavedrom/blob/master/src/WaveDrom.js
# Now many parts have been rewritten and diverged

from __future__ import annotations

from math import floor

import svgwrite

from wavedrom2 import svg

from .tspan import TspanParser


class Options:
    def __init__(
        self,
        vspace=80,
        hspace=800,
        lanes=1,
        bits=32,
        hflip=False,
        vflip=False,
        fontsize=14,
        fontfamily="sans-serif",
        fontweight="normal",
    ):
        self.vspace = vspace if vspace > 19 else 80
        self.hspace = hspace if hspace > 39 else 800
        self.lanes = lanes if lanes > 0 else 1
        self.bits = bits if bits > 4 else 32
        self.hflip = hflip
        self.vflip = vflip
        self.fontsize = fontsize if fontsize > 5 else 14
        self.fontfamily = fontfamily
        self.fontweight = fontweight


colors = {2: "FF0000", 3: "AAFF00", 4: "00FFD5", 5: "FFBF00", 6: "00FF1A", 7: "006AFF"}


def type_style(t):
    if t in colors.keys():
        return f";fill:#{colors[t]}"
    else:
        return ""


class BitField:
    def tspan_parse(self, text):
        parser = TspanParser()
        parser.feed(text)
        return parser.get_text()

    def hline(self, len, x=0, y=0):
        return svg.Line(start=(x, y), end=(x + len, y))

    def vline(self, len, x=0, y=0):
        return svg.Line(start=(x, y), end=(x, y + len))

    def get_text(self, body, x, y=None):
        x_list = None
        if x:
            x_list = [x]
        y_list = None
        if y:
            y_list = [y]
        text = svg.Text("", x=x_list, y=y_list)
        for t in self.tspan_parse(str(body)):
            text.add(t)
        return text

    def get_label(self, attr, x, y, step=0, length=0):
        if isinstance(attr, int):
            attr = int(attr)
            res = []
            for i in range(length):
                val = (attr >> i) & 1
                xi = x + step * (length / 2 - i - 0.5)
                res.append(self.get_text(val, xi, y))
            return res
        else:
            if "\n" in attr:
                names = attr.split("\n")
                count = len(names)
                return [
                    self.get_text(
                        name, x, y + (-(count - 1) / 2 + i) * self.opt.fontsize
                    )
                    for (i, name) in enumerate(names)
                ]
            return [self.get_text(attr, x, y)]

    def get_attrs(self, e, step, lsbm, msbm):
        if self.opt.vflip:
            x = step * (msbm + lsbm) / 2
        else:
            x = step * (self.mod - ((msbm + lsbm) / 2) - 1)
        attr = e["attr"]
        bits = e["bits"]
        attrs = [attr]
        # 'attr' supports both a scalar and a list.
        if isinstance(attr, list):
            attrs = attr
        return [self.get_label(a, x, 16 * i, step, bits) for (i, a) in enumerate(attrs)]

    def labelArr(self, desc):
        step = self.opt.hspace / self.mod
        bits = svg.Group(
            transform=f"translate({step / 2},{self.opt.vspace / 5})"
        )
        names = svg.Group(
            transform=f"translate({step / 2},{self.opt.vspace / 2 + 4})"
        )
        attrs = svg.Group(
            transform=f"translate({step / 2},{self.opt.vspace})"
        )
        blanks = svg.Group(
            transform=f"translate(0,{self.opt.vspace / 4})"
        )

        for e in desc:
            lsbm = 0
            msbm = self.mod - 1
            lsb = self.index * self.mod
            msb = (self.index + 1) * self.mod - 1

            if floor(e["lsb"] / self.mod) == self.index:
                lsbm = e["lsbm"]
                lsb = e["lsb"]
                if floor(e["msb"] / self.mod) == self.index:
                    msb = e["msb"]
                    msbm = e["msbm"]
            else:
                if floor(e["msb"] / self.mod) == self.index:
                    msb = e["msb"]
                    msbm = e["msbm"]
                else:
                    continue

            if self.opt.vflip:
                bits.add(self.get_text(lsb, x=[step * lsbm]))
            else:
                bits.add(self.get_text(lsb, x=[step * (self.mod - lsbm - 1)]))
            if lsbm != msbm:
                if self.opt.vflip:
                    bits.add(self.get_text(msb, x=[step * msbm]))
                else:
                    bits.add(self.get_text(msb, x=[step * (self.mod - msbm - 1)]))
            if e.get("name"):
                if self.opt.vflip:
                    x = step * (msbm + lsbm) / 2
                else:
                    x = step * (self.mod - ((msbm + lsbm) / 2) - 1)
                for n in self.get_label(e["name"], x, 0):
                    names.add(n)

            if not e.get("name") or e.get("type"):
                style = "fill-opacity:0.1" + type_style(e.get("type", 0))
                if self.opt.vflip:
                    insert_x = lsbm
                else:
                    insert_x = self.mod - msbm - 1
                insert = [step * insert_x, 0]
                size = [step * (msbm - lsbm + 1), self.opt.vspace / 2]
                blanks.add(svg.Rect(insert=insert, size=size, style=style))
            if e.get("attr") is not None:
                for attr in self.get_attrs(e, step, lsbm, msbm):
                    for a in attr:
                        attrs.add(a)

        g = svg.Group()
        g.add(blanks)
        g.add(bits)
        g.add(names)
        g.add(attrs)
        return g

    def labels(self, desc):
        g = svg.Group(text_anchor="middle")
        g.add(self.labelArr(desc))
        return g

    def cage(self, desc):
        hspace = self.opt.hspace
        vspace = self.opt.vspace
        mod = self.mod

        g = svg.Group(
            stroke="black",
            stroke_width=1,
            stroke_linecap="round",
            transform=f"translate(0,{vspace / 4})",
        )

        g.add(self.hline(hspace))
        if self.opt.vflip:
            g.add(self.vline(0))
        else:
            g.add(self.vline(vspace / 2))
        g.add(self.hline(hspace, 0, vspace / 2))

        i = self.index * mod
        if self.opt.vflip:
            r = range(0, mod + 1)
        else:
            r = range(mod, 0, -1)
        for j in r:
            if j == mod or any([(e["lsb"] == i) for e in desc]):
                g.add(self.vline((vspace / 2), j * (hspace / mod)))
            else:
                g.add(self.vline((vspace / 16), j * (hspace / mod)))
                g.add(self.vline((vspace / 16), j * (hspace / mod), vspace * 7 / 16))
            i += 1

        return g

    def lane(self, desc):
        x = 4.5
        if self.opt.hflip:
            i = self.index
        else:
            i = self.opt.lanes - self.index - 1
        y = i * self.opt.vspace + 0.5
        g = svg.Group(
            transform=f"translate({x},{y})",
            text_anchor="middle",
            font_size=self.opt.fontsize,
            font_family=self.opt.fontfamily,
            font_weight=self.opt.fontweight,
        )

        g.add(self.cage(desc))
        g.add(self.labels(desc))
        return g

    def get_max_attrs(self, desc):
        max_count = 0
        for e in desc:
            if "attr" in e:
                if isinstance(e["attr"], list):
                    max_count = max(max_count, len(e["attr"]))
                else:
                    max_count = max(max_count, 1)
        return max_count

    def render(self, desc, opt: Options | None = None):
        if opt is None:
            opt = Options()

        self.opt = opt

        # Compute extra per-lane space needed if there are more than one attr
        # for any field.  This spaces all lanes uniformly, matching the lane
        # with the most attr's.
        extra_attrs = 0
        max_attrs = self.get_max_attrs(desc)
        if max_attrs > 1:
            extra_attrs = max_attrs - 1
        self.extra_attr_space = extra_attrs * 16

        width = opt.hspace + 9
        height = (opt.vspace + self.extra_attr_space) * opt.lanes + 5

        template = svgwrite.Drawing()
        template["width"] = width
        template["height"] = height
        template["class"] = "WaveDrom"
        template.viewbox(0, 0, width, height)

        lsb = 0
        self.mod = int(opt.bits / opt.lanes)

        for e in desc:
            e["lsb"] = lsb
            e["lsbm"] = lsb % self.mod
            lsb += e["bits"]
            e["msb"] = lsb - 1
            e["msbm"] = e["msb"] % self.mod

        for i in range(opt.lanes):
            self.index = i
            template.add(self.lane(desc))

        return template

    def renderJson(self, source) -> svgwrite.Drawing:
        opt = Options()
        if "config" in source:
            opt = Options(**source["config"])

        if "reg" in source:
            return self.render(source["reg"], opt)

        raise ValueError("Invalid WaveDrom source for BitField rendering")
