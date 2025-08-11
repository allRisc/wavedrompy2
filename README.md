# WaveDromPy2

This is a python module and command line fully compatible with [WaveDrom](https://wavedrom.com/), which is originally implemented in JavaScript. It is useful if you want to generate wavedrom diagrams from a python environment or simply don't want to install the _Node.js_ environment just to use WaveDrom as simple command line.

WaveDromPy2 is a fork of the previous [WaveDromPy](https://github.com/wallento/wavedrompy/) which appears to be no-longer maintained.

This tool is a direct translation of original Javascript file _WaveDrom.js_ to Python. No extra feature added. We seek to have it fully compatible.

The tool _WaveDromPy2_ directly converts _WaveDrom_ compatible JSON files into SVG format.

[![Build Status](https://travis-ci.org/allrisc/wavedrompy2.svg?branch=main)](https://travis-ci.org/allrisc/wavedrompy2)
[![PyPI version](https://badge.fury.io/py/wavedrom2.svg)](https://badge.fury.io/py/wavedrom2)

## Installation

It is most easy to just install wavedrom2 via pip/pypi:

    pip install wavedrom2

Alternatively you can install the latest version from this repository:

    pip install git+https://github.com/allrisc/wavedrompy2

or from your local copy:

    pip install .

## Usage

You can either use the tool from Python:

    import wavedrom2
    svg = wavedrom2.render("""
    { "signal": [
     { "name": "CK",   "wave": "P.......",                                              "period": 2  },
     { "name": "CMD",  "wave": "x.3x=x4x=x=x=x=x", "data": "RAS NOP CAS NOP NOP NOP NOP", "phase": 0.5 },
     { "name": "ADDR", "wave": "x.=x..=x........", "data": "ROW COL",                     "phase": 0.5 },
     { "name": "DQS",  "wave": "z.......0.1010z." },
     { "name": "DQ",   "wave": "z.........5555z.", "data": "D0 D1 D2 D3" }
    ]}""")
    svg.saveas("demo1.svg")

This will render a waveform as:

![Example 1](https://raw.githubusercontent.com/allrisc/wavedrompy2/2e8568d50561f534133d036fee3bd35756f416d9/doc/demo1.svg?sanitize=true "Example 1")

You can find more examples [in the WaveDrom tutorial](https://wavedrom.com/tutorial.html).

A second feature is that WaveDrom can render logic circuit diagrams:

    import wavedrom2
    svg = wavedrom2.render("""
    { "assign":[
      ["out",
        ["|",
          ["&", ["~", "a"], "b"],
          ["&", ["~", "b"], "a"]
        ]
      ]
    ]}""")
    svg.saveas("demo2.svg")

This will render a as:

![Example 2](https://raw.githubusercontent.com/allrisc/wavedrompy2/2e8568d50561f534133d036fee3bd35756f416d9/doc/demo2.svg?sanitize=true "Example 2")

You can find more examples [in the WaveDrom tutorial2](https://wavedrom.com/tutorial2.html).

Finally, wavedrom2 can draw registers as bitfields:

    import wavedrom2
    svg = wavedrom2.render("""
    {"reg": [
      { "name": "IPO",   "bits": 8, "attr": "RO" },
      {                  "bits": 7 },
      { "name": "<o>B</o><b>R<i>K</i></b>",   "bits": 5, "attr": "RW", "type": 4 },
      { "name": "CPK",   "bits": 1 },
      { "name": "Clear", "bits": 3 },
      { "bits": 8 }
      ]
    ]}""")
    svg.saveas("demo3.svg")


This will render as:

![Example 3](https://raw.githubusercontent.com/allrisc/wavedrompy2/2e8568d50561f534133d036fee3bd35756f416d9/doc/demo3.svg?sanitize=true "Example 3")

This mode is documented as part of the [bit-field](https://www.npmjs.com/package/bit-field) JavaScript package.

Alternatively, wavedrompy2 can be called from the command line:

    wavedrompy2 --input input.json --svg output.svg

## Important notice

The command line uses Python's JSON interpreter that is more restrictive (coherent with the JSOC spec), while the JavaScript json is more relaxed:

 * All strings have to be written between quotes (""),
 * Extra comma (,) not supported at end of lists or dictionaries

## AsciiDoctor example

An _AsciiDoctor_ example is provided to directly generate timing diagrams from _AsciiDoctor_ formatted documents.

