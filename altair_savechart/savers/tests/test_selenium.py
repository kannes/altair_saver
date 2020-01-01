import io
import json
import os
from typing import Any, Dict, IO, Iterator, Tuple

import pytest
from PIL import Image

from altair_savechart.savers import SeleniumSaver


def get_testcases() -> Iterator[Tuple[str, Dict[str, Any]]]:
    directory = os.path.join(os.path.dirname(__file__), "testcases")
    cases = set(f.split(".")[0] for f in os.listdir(directory))
    f: IO
    for case in sorted(cases):
        with open(os.path.join(directory, f"{case}.vl.json")) as f:
            vl = json.load(f)
        with open(os.path.join(directory, f"{case}.vg.json")) as f:
            vg = json.load(f)
        with open(os.path.join(directory, f"{case}.svg")) as f:
            svg = f.read()
        with open(os.path.join(directory, f"{case}.png"), "rb") as f:
            png = f.read()
        yield case, {"vega-lite": vl, "vega": vg, "svg": svg, "png": png}


@pytest.mark.parametrize("name,data", get_testcases())
@pytest.mark.parametrize("mode", ["vega", "vega-lite"])
@pytest.mark.parametrize("fmt", SeleniumSaver.valid_formats)
@pytest.mark.parametrize("offline", [True, False])
def test_selenium_mimebundle(
    name: str, data: Any, mode: str, fmt: str, offline: bool
) -> None:
    saver = SeleniumSaver(data[mode], mode=mode, offline=offline)
    if mode == "vega" and fmt == "vega-lite":
        with pytest.raises(ValueError):
            out = saver.mimebundle(fmt).popitem()[1]
        return
    out = saver.mimebundle(fmt).popitem()[1]
    if fmt == "png":
        assert isinstance(out, bytes)
        im = Image.open(io.BytesIO(out))
        assert im.format == "PNG"

        im_expected = Image.open(io.BytesIO(data[fmt]))
        assert abs(im.size[0] - im_expected.size[0]) < 5
        assert abs(im.size[1] - im_expected.size[1]) < 5
    elif fmt == "svg":
        assert out == data[fmt]
    else:
        assert out == data[fmt]


def test_enabled() -> None:
    assert SeleniumSaver.enabled()
