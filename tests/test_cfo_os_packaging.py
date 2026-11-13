"""An installed `cfo-os` carries the template, so it deploys with no clone on disk. Fixtures
are fictional."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import shutil
import subprocess
import sys
import tomllib
import zipfile

import pytest

from .cfo_os_paths import ROOT, TEMPLATE
import cfo_os.common as common
from cfo_os.common import FOLDER_NAME, TemplateError, find_template, template_files

PACKAGED = "cfo_os/_template"


def _setuptools() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["setuptools"]


def test_every_package_under_src_is_listed_for_install():
    on_disk = {".".join(p.parent.relative_to(ROOT / "src").parts)
               for p in (ROOT / "src" / "cfo_os").rglob("__init__.py")}
    config = _setuptools()
    assert set(config["packages"]) == on_disk | {"cfo_os._template"}
    assert config["package-dir"]["cfo_os._template"] == "template"
    assert config["package-data"]["cfo_os._template"] == ["**/*"]


def test_the_installed_copy_of_the_template_is_found_away_from_a_clone(tmp_path, monkeypatch):
    package = tmp_path / "site-packages" / "cfo_os"
    shutil.copytree(TEMPLATE, package / "_template" / FOLDER_NAME)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.setattr(common, "PACKAGE", package)
    monkeypatch.delenv("CFO_OS_TEMPLATE", raising=False)
    monkeypatch.chdir(elsewhere)
    assert find_template() == (package / "_template" / FOLDER_NAME).resolve()


def test_no_template_anywhere_says_how_to_get_one(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "PACKAGE", tmp_path / "site-packages" / "cfo_os")
    monkeypatch.delenv("CFO_OS_TEMPLATE", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(TemplateError, match="reinstall cfo-ai-os"):
        find_template()


def _can_build() -> bool:
    """pip and a setuptools new enough for pyproject.toml, without downloading either."""
    if importlib.util.find_spec("pip") is None or importlib.util.find_spec("setuptools") is None:
        return False
    major = importlib.metadata.version("setuptools").split(".")[0]
    return major.isdigit() and int(major) >= 77


@pytest.mark.skipif(not _can_build(), reason="building a wheel needs pip and setuptools 77 or later")
def test_the_built_wheel_holds_every_template_file(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    for name in ("pyproject.toml", "README.md", "LICENSE", "NOTICE"):
        shutil.copy2(ROOT / name, source / name)
    for name in ("src", "template"):
        shutil.copytree(ROOT / name, source / name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    built = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", str(source), "--no-deps", "--no-build-isolation",
         "--quiet", "--wheel-dir", str(tmp_path / "wheels")],
        capture_output=True, text=True)
    assert built.returncode == 0, built.stderr[-2000:]
    wheel, = (tmp_path / "wheels").glob("cfo_ai_os-*.whl")
    with zipfile.ZipFile(wheel) as z:
        names = set(z.namelist())
    wanted = {f"{PACKAGED}/{FOLDER_NAME}/{rel}" for rel in template_files(TEMPLATE)}
    assert wanted and not wanted - names
    assert {"cfo_os/placeholders.yaml", "cfo_os/ownership.yaml", "cfo_os/catalogue/build.py",
            "cfo_os/catalogue/adapters/datarails_mcp.py"} <= names
