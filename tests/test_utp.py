"""Packaging and boundary regressions; Minecraft playtesting remains mandatory."""

import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from tools import utp


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in (utp.PACK, utp.LAB):
            shutil.copytree(utp.ROOT / folder, self.root / folder)

    def test_valid_foundation_and_repeatable_packages(self):
        """Player downloads exclude the lab, and identical sources produce identical bytes."""
        utp.build(self.root)
        destination = self.root / "dist"
        first = {p.name: p.read_bytes() for p in destination.iterdir()}
        utp.build(self.root)
        self.assertEqual(first, {p.name: p.read_bytes() for p in destination.iterdir()})
        for name, expected in (("underground-tech-pack-0.1.0.mcaddon", 2),
                               ("underground-tech-pack-0.1.0-dev.mcaddon", 3)):
            with zipfile.ZipFile(destination / name) as outer:
                self.assertEqual(len(outer.namelist()), expected)
                self.assertIsNone(outer.testzip())
                for entry in outer.namelist():
                    with zipfile.ZipFile(io.BytesIO(outer.read(entry))) as inner:
                        self.assertIn("manifest.json", inner.namelist())
                        self.assertIsNone(inner.testzip())
                        if entry != "utp-lab.mcpack":
                            self.assertFalse(any(p.endswith(".mcfunction") for p in inner.namelist()))

    def test_unresolved_resource_dependency_blocks_packaging(self):
        """A pack with a broken resource dependency cannot be distributed."""
        path = self.root / utp.PACK / "behavior-pack/manifest.json"
        manifest = utp.read_json(path)
        manifest["dependencies"][0]["uuid"] = manifest["header"]["uuid"]
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "dependency mismatch"):
            utp.build(self.root)

    def test_corrupt_texture_blocks_packaging(self):
        """A missing or corrupt texture cannot silently ship."""
        path = self.root / utp.PACK / "resource-pack/textures/blocks/navy_metal.png"
        path.write_bytes(b"broken")
        with self.assertRaisesRegex(ValueError, "Texture missing, corrupt, or stale"):
            utp.build(self.root)

    def test_interactive_component_requires_scope_review(self):
        """Unexpected behavior fails the decorative-only guardrail."""
        path = self.root / utp.PACK / "behavior-pack/blocks/navy_metal.json"
        block = utp.read_json(path)
        block["minecraft:block"]["components"]["minecraft:custom_components"] = ["test:interactive"]
        path.write_text(json.dumps(block))
        with self.assertRaisesRegex(ValueError, "decorative-only"):
            utp.validate(self.root)


if __name__ == "__main__":
    unittest.main()
