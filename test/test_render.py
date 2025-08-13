import os
import subprocess
import sys
from glob import glob
from os.path import splitext, basename

import xml.dom.minidom

import wavedrom2
import pytest
from diff import diff_raster, diff_xml

files_basic = glob("test/files/signal_*.json")
# files_subcycle = glob("test/files/subcycle_*.json")
# files_assign = glob("test/files/assign_*.json")
# files_bitfield = glob("test/files/bitfield_*.json")
files_tutorial = glob("test/files/tutorial_*.json")
files_issues = glob("test/files/issue_*.json")

files = files_basic + files_tutorial + files_issues


def pytest_generate_tests(metafunc):
    metafunc.parametrize("file", files)


def test_render(file):
    jinput = open(file).read()
    wavedrom2.render(jinput)


@pytest.fixture(scope="session")
def wavedromdir(tmpdir_factory):
    if "WAVEDROMDIR" in os.environ:
        return os.environ["WAVEDROMDIR"]
    else:
        wavedromdir = tmpdir_factory.mktemp("wavedrom")
        subprocess.check_call("git clone https://github.com/wavedrom/cli.git {}".format(wavedromdir), shell=True)
        subprocess.check_call("git reset --hard bf95544a52f5c23e98917255df2017759fcd18da", cwd=str(wavedromdir), shell=True)
        subprocess.check_call("npm install", cwd=str(wavedromdir), shell=True)
        subprocess.check_call("npm install wavedrom@3.5.0", shell=True)
        return wavedromdir


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test_upstream(tmpdir,wavedromdir,file):
    base = splitext(basename(file))[0]
    f_out = "{}/{}.svg".format(tmpdir, base)
    f_out_py = "{}/{}_py.svg".format(tmpdir, base)

    subprocess.check_call("node {}/wavedrom-cli.js -i {} > {}".format(wavedromdir, file, f_out), shell=True)
    wavedrom2.render_file(file, f_out_py, strict_js_features=True)

    dom = xml.dom.minidom.parse(f_out)
    with open(f_out, "w") as f:
        f.write(dom.toprettyxml())

    dom = xml.dom.minidom.parse(f_out_py)
    with open(f_out_py, "w") as f:
        f.write(dom.toprettyxml())

    unknown = diff_xml(f_out, f_out_py)

    if len(unknown) > 0:
        msg = "{} mismatch(es)\n".format(len(unknown))
        msg += "js file: {}\npy file: {}\n".format(f_out, f_out_py)
        msg += "\n".join([str(action) for action in unknown])
        pytest.fail(msg)

    img = diff_raster(f_out, f_out_py)

    if img.getbbox() is not None:
        img.save("{}/{}_diff.png".format(tmpdir, base))
        pytest.fail("Raster image comparison failed for " + file)

    # assert False
