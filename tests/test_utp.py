"""Packaging and boundary regressions; Minecraft playtesting remains mandatory."""

import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from tools import utp


class CoreMetalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in (utp.PACK, utp.LAB):
            shutil.copytree(utp.ROOT / folder, self.root / folder)

    def test_all_cataloged_blocks_ship_in_repeatable_packages(self):
        """Player downloads exclude the lab, and identical sources produce identical bytes."""
        utp.build(self.root)
        destination = self.root / "dist"
        first = {p.name: p.read_bytes() for p in destination.iterdir()}
        utp.build(self.root)
        self.assertEqual(first, {p.name: p.read_bytes() for p in destination.iterdir()})
        for name, expected in (("underground-tech-pack-0.1.2.mcaddon", 2),
                               ("underground-tech-pack-0.1.2-dev.mcaddon", 3)):
            with zipfile.ZipFile(destination / name) as outer:
                self.assertEqual(len(outer.namelist()), expected)
                self.assertIsNone(outer.testzip())
                for entry in outer.namelist():
                    with zipfile.ZipFile(io.BytesIO(outer.read(entry))) as inner:
                        self.assertIn("manifest.json", inner.namelist())
                        self.assertIsNone(inner.testzip())
                        if entry != "utp-lab.mcpack":
                            self.assertFalse(any(p.endswith(".mcfunction") for p in inner.namelist()))
                        else:
                            self.assertIn("functions/utp/m2.mcfunction", inner.namelist())
                        if entry.endswith("-bp.mcpack"):
                            self.assertEqual({p for p in inner.namelist() if p.startswith("blocks/")},
                                             {f"blocks/{asset}.json" for asset in utp.ASSETS})
                        if entry.endswith("-rp.mcpack"):
                            for asset in utp.PIPE_PROTOTYPES:
                                self.assertIn(f"models/blocks/{asset}.geo.json", inner.namelist())
                            for asset in utp.ASSETS:
                                self.assertEqual(inner.read(f"textures/blocks/{asset}.png"),
                                                 utp.texture_bytes(self.root, asset))

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

    def test_missing_piece_blocks_packaging(self):
        """A download cannot silently omit one of the eight building pieces."""
        (self.root / utp.PACK / "behavior-pack/blocks/vent_panel.json").unlink()
        with self.assertRaisesRegex(ValueError, "all eight M1 blocks"):
            utp.build(self.root)

    def test_missing_display_name_blocks_packaging(self):
        """Every piece has exactly one understandable inventory name."""
        path = self.root / utp.PACK / "resource-pack/texts/en_US.lang"
        path.write_text(path.read_text().replace("tile.steelwater_utp:vent_panel.name=UTP Vent Panel", ""))
        with self.assertRaisesRegex(ValueError, "display name"):
            utp.build(self.root)

    def test_wrong_texture_reference_blocks_packaging(self):
        """A new piece cannot accidentally display another piece's artwork."""
        path = self.root / utp.PACK / "resource-pack/textures/terrain_texture.json"
        atlas = utp.read_json(path)
        atlas["texture_data"]["steelwater_utp_vent_panel"]["textures"] = "textures/blocks/navy_metal"
        path.write_text(json.dumps(atlas))
        with self.assertRaisesRegex(ValueError, "atlas texture"):
            utp.build(self.root)

    def test_original_prototype_remains_unchanged(self):
        """Existing worlds retain the original navy panel pixels and behavior."""
        self.assertEqual(hashlib.sha256(utp.texture_bytes(self.root)).hexdigest(),
                         "8c53e62c71942cf2fb8bf8aca7b75d53162e321474c84e0bce4d8a3771784bfd")
        block = self.root / utp.PACK / "behavior-pack/blocks/navy_metal.json"
        self.assertEqual(hashlib.sha256(block.read_bytes()).hexdigest(),
                         "2c19579de1d39f178e7915ed5caccf01394fc9605db91d2ad7c12d7f6e845f11")
        expected_ids = [
            ("8f4306b2-c16d-403c-93cc-f07adf8dc560", "c6223be1-d729-40d3-bafc-0d5e55371708"),
            ("b2409bcb-ec4c-4b74-94fa-a3fb045a9ad8", "663ff5ea-7906-468a-bdaf-688e1b576351"),
            ("1beaa4f5-8967-407b-a32b-68698669d9a5", "8766c159-746f-4dbb-9f05-01cfa0b58a4f"),
        ]
        for folder, expected in zip((utp.PACK / "behavior-pack", utp.PACK / "resource-pack", utp.LAB), expected_ids):
            manifest = utp.read_json(self.root / folder / "manifest.json")
            self.assertEqual((manifest["header"]["uuid"], manifest["modules"][0]["uuid"]), expected)

    def test_each_piece_has_distinct_artwork(self):
        """The eight inventory choices have distinct visible surface designs."""
        self.assertEqual(len({utp.texture_bytes(self.root, asset) for asset in utp.CORE_METALS}), 8)

    def test_pipe_end_faces_share_a_centered_six_pixel_profile(self):
        """Adjacent pipe ends meet at the block boundary with matching cross sections."""
        grid = [(-8, 8), (0, 16), (-8, 8)]
        for name, expected in (("straight_pipe", {(2, -8), (2, 8)}),
                               ("elbow_pipe", {(2, -8), (0, 8)})):
            with self.subTest(name=name):
                path = self.root / utp.PACK / f"resource-pack/models/blocks/{name}.geo.json"
                model, = utp.read_json(path)["minecraft:geometry"]
                ends = set()
                for cube in model["bones"][0]["cubes"]:
                    for axis, (low, high) in enumerate(grid):
                        start = cube["origin"][axis]
                        end = start + cube["size"][axis]
                        self.assertTrue(low <= start < end <= high)
                        for boundary in {start, end} & {low, high}:
                            ends.add((axis, boundary))
                            for transverse in set(range(3)) - {axis}:
                                center = sum(grid[transverse]) // 2
                                self.assertEqual(cube["origin"][transverse], center - 3)
                                self.assertEqual(cube["size"][transverse], 6)
                self.assertEqual(ends, expected)


if __name__ == "__main__":
    unittest.main()
