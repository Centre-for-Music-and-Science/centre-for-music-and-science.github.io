"""Shared Hugo site build for smoke tests."""

from __future__ import annotations

import atexit
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

_tmpdir: tempfile.TemporaryDirectory[str] | None = None
_public: Path | None = None


def hugo_public_dir() -> Path:
    """Return the site ``public/`` directory, building once per process."""
    global _tmpdir, _public
    if _public is not None:
        return _public

    if not shutil.which("hugo"):
        raise RuntimeError("hugo not installed")

    _tmpdir = tempfile.TemporaryDirectory()
    public = Path(_tmpdir.name) / "public"
    result = subprocess.run(
        [
            "hugo",
            "--destination",
            str(public),
            "--minify",
            "--cleanDestinationDir",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        _tmpdir.cleanup()
        _tmpdir = None
        raise AssertionError(
            "hugo build failed:\n"
            f"{result.stdout}\n{result.stderr}"
        )

    _public = public
    atexit.register(_cleanup)
    return _public


def _cleanup() -> None:
    global _tmpdir, _public
    if _tmpdir is not None:
        _tmpdir.cleanup()
    _tmpdir = None
    _public = None


@unittest.skipUnless(shutil.which("hugo"), "hugo not installed")
class HugoSiteSmokeTest(unittest.TestCase):
    """Base class that reuses one Hugo build across smoke-test classes."""

    public: Path

    @classmethod
    def setUpClass(cls) -> None:
        cls.public = hugo_public_dir()

    def _read(self, relative: str) -> str:
        path = self.public / relative
        self.assertTrue(path.is_file(), f"missing build output: {relative}")
        return path.read_text(encoding="utf-8")
