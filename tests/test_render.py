import os
import subprocess
import sys
import xml.dom.minidom
from glob import glob
from os.path import basename, splitext

import pytest
from diff import diff_raster, diff_xml

import wavedrom2

files_basic = glob("tests/files/signal_*.json")
# TODO: files_subcycle = glob("tests/files/subcycle_*.json")
# TODO: files_assign = glob("tests/files/assign_*.json")
# TODO: files_bitfield = glob("tests/files/bitfield_*.json")
files_tutorial = glob("tests/files/tutorial_*.json")
files_issues = glob("tests/files/issue_*.json")

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
        if "WAVEDROM_REPO" in os.environ:
            wavedrom_repo = os.environ["WAVEDROM_REPO"]
        else:
            wavedrom_repo = "https://github.com/wavedrom/cli.git"

        wavedromdir = tmpdir_factory.mktemp("wavedrom")
        subprocess.check_call(
            f"git clone {wavedrom_repo} {wavedromdir}", shell=True
        )
        subprocess.check_call(
            "git reset --hard bf95544a52f5c23e98917255df2017759fcd18da",
            cwd=str(wavedromdir), shell=True
        )
        subprocess.check_call("npm install", cwd=str(wavedromdir), shell=True)
        subprocess.check_call("npm install wavedrom@3.5.0", shell=True)
        return wavedromdir


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test_upstream(tmpdir,wavedromdir,file):
    base = splitext(basename(file))[0]
    f_out = f"{tmpdir}/{base}.svg"
    f_out_py = f"{tmpdir}/{base}_py.svg"

    subprocess.check_call(f"node {wavedromdir}/wavedrom-cli.js -i {file} > {f_out}", shell=True)
    wavedrom2.render_file(file, f_out_py, strict_js_features=True)

    dom = xml.dom.minidom.parse(f_out)
    with open(f_out, "w") as f:
        f.write(dom.toprettyxml())

    dom = xml.dom.minidom.parse(f_out_py)
    with open(f_out_py, "w") as f:
        f.write(dom.toprettyxml())

    unknown = diff_xml(f_out, f_out_py)

    if len(unknown) > 0:
        msg = f"{len(unknown)} mismatch(es)\n"
        msg += f"js file: {f_out}\npy file: {f_out_py}\n"
        msg += "\n".join([str(action) for action in unknown])
        pytest.fail(msg)

    img = diff_raster(f_out, f_out_py)

    if img.getbbox() is not None:
        img.save(f"{tmpdir}/{base}_diff.png")
        pytest.fail("Raster image comparison failed for " + file)

    # assert False
