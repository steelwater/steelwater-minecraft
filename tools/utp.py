#!/usr/bin/env python3
"""Validate and package Milestone 0 using only Python's standard library."""

import argparse
import binascii
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import uuid
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
PACK = Path("addons/underground-tech-pack")
LAB = Path("worlds/underground-tech-pack-lab/behavior-pack")
IDENTIFIER = "steelwater_utp:navy_metal"
SYMBOLS = {"N": "navy_metal", "G": "gunmetal", "S": "dull_steel", "T": "dark_trim"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def texture_bytes(root=ROOT):
    palette = read_json(root / PACK / "art/palette.json")
    rows = (root / PACK / "art/navy_metal.pixels").read_text().splitlines()
    require(len(rows) == 16 and all(len(row) == 16 for row in rows), "Texture must be 16×16")
    require(set("".join(rows)) <= SYMBOLS.keys(), "Unknown texture pixel symbol")
    for color in palette.values():
        require(re.fullmatch(r"#[0-9A-Fa-f]{6}", color), "Invalid palette hex color")
    raw = b"".join(b"\x00" + b"".join(bytes.fromhex(palette[SYMBOLS[pixel]][1:])
                                  for pixel in row) for row in rows)

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", binascii.crc32(kind + data)))

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", 16, 16, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def palette_svg(root=ROOT):
    palette = read_json(root / PACK / "art/palette.json")
    elements = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="440" viewBox="0 0 800 440">',
                '<rect width="800" height="440" fill="#101820"/>',
                '<g font-family="sans-serif" fill="#E2E9EE">',
                '<text x="28" y="40" font-size="24">Underground Tech Pack · v0.1 palette</text>',
                '<text x="28" y="67" font-size="14">Navy metal first. Status accents reserved for future assets.</text>']
    for i, (name, color) in enumerate(palette.items()):
        x, y = 28 + (i % 4) * 194, 94 + (i // 4) * 154
        elements.extend([f'<rect x="{x}" y="{y}" width="166" height="86" fill="{color}" stroke="#607080"/>',
                         f'<text x="{x}" y="{y+109}" font-size="15">{name.replace("_", " ").title()}</text>',
                         f'<text x="{x}" y="{y+130}" font-size="13">{color}</text>'])
    elements.extend(['<text x="28" y="419" font-size="13">Original industrial palette · no emissive material in the prototype</text>', '</g></svg>'])
    return "\n".join(elements) + "\n"


def render(root=ROOT):
    (root / PACK / "resource-pack/textures/blocks/navy_metal.png").write_bytes(texture_bytes(root))
    (root / PACK / "art/palette.svg").write_text(palette_svg(root), encoding="utf-8")


def validate(root=ROOT):
    pack = root / PACK
    manifests = [read_json(root / folder / "manifest.json") for folder in
                 (PACK / "behavior-pack", PACK / "resource-pack", LAB)]
    identifiers = []
    for manifest, kind in zip(manifests, ("data", "resources", "data")):
        require(manifest["format_version"] == 2, "Expected manifest format 2")
        header, modules = manifest["header"], manifest["modules"]
        require(len(modules) == 1 and modules[0]["type"] == kind, "Wrong pack module")
        require(header["version"] == modules[0]["version"] == [0, 1, 0], "Version mismatch")
        require(header["min_engine_version"] == [1, 21, 80], "Engine baseline changed")
        for value in (header["uuid"], modules[0]["uuid"]):
            require(str(uuid.UUID(value)) == value, "Invalid UUID")
            identifiers.append(value)
    require(len(set(identifiers)) == 6, "Pack UUIDs must be unique")
    for dependent, dependency in ((manifests[0], manifests[1]), (manifests[2], manifests[0])):
        require(dependent["dependencies"] == [{"uuid": dependency["header"]["uuid"],
                                               "version": dependency["header"]["version"]}],
                "Pack dependency mismatch")
    for folder in (PACK / "behavior-pack", PACK / "resource-pack", LAB):
        for path in (root / folder).rglob("*.json"):
            read_json(path)
    blocks = list((pack / "behavior-pack/blocks").glob("*.json"))
    require(len(blocks) == 1, "Milestone 0 must have exactly one block")
    block_file = read_json(blocks[0])
    require(block_file["format_version"] == "1.21.80", "Unexpected block format")
    block = block_file["minecraft:block"]
    require(block["description"]["identifier"] == IDENTIFIER, "Block identifier changed")
    require(block["description"]["menu_category"]["category"] == "construction", "Block missing from Construction")
    components = block["components"]
    require(set(components) == {"minecraft:geometry", "minecraft:material_instances", "minecraft:collision_box",
                                "minecraft:selection_box", "minecraft:destructible_by_mining",
                                "minecraft:destructible_by_explosion", "minecraft:light_dampening"},
            "Unexpected prototype component; review decorative-only scope")
    require(components["minecraft:geometry"] == "minecraft:geometry.full_block", "Expected full cube")
    require(components["minecraft:collision_box"] is True and components["minecraft:selection_box"] is True,
            "Prototype must have full-cube collision and selection")
    require(not (pack / "behavior-pack/functions").exists() and not (pack / "behavior-pack/scripts").exists(),
            "Player pack must not include test functions or scripts")
    material = components["minecraft:material_instances"]["*"]
    require(material["render_method"] == "opaque", "Prototype should be opaque")
    atlas = read_json(pack / "resource-pack/textures/terrain_texture.json")
    texture = atlas["texture_data"][material["texture"]]["textures"]
    require(texture == "textures/blocks/navy_metal", "Unexpected atlas texture reference")
    require((pack / "resource-pack" / (texture + ".png")).read_bytes() == texture_bytes(root),
            "Texture missing, corrupt, or stale; run render")
    require((pack / "art/palette.svg").read_text() == palette_svg(root), "Palette sheet stale; run render")
    require(f"tile.{IDENTIFIER}.name=UTP Navy Metal" in (pack / "resource-pack/texts/en_US.lang").read_text(),
            "Missing display name")
    require(read_json(pack / "resource-pack/blocks.json")[IDENTIFIER]["sound"] == "metal", "Missing metal sound")
    require(not (root / LAB / "functions/tick.json").exists(), "Lab setup must be manual")


def archive(entries):
    """Stable archive metadata lets checksums identify exactly the tested package."""
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
    return output.getvalue()


def pack_bytes(path):
    allowed = {".json", ".png", ".lang", ".mcfunction"}
    return archive((p.relative_to(path).as_posix(), p.read_bytes()) for p in path.rglob("*")
                   if p.is_file() and p.suffix in allowed and not any(part.startswith(".") for part in p.relative_to(path).parts))


def build(root=ROOT):
    validate(root)
    destination = root / "dist"
    destination.mkdir(exist_ok=True)
    runtime = [("underground-tech-pack-bp.mcpack", pack_bytes(root / PACK / "behavior-pack")),
               ("underground-tech-pack-rp.mcpack", pack_bytes(root / PACK / "resource-pack"))]
    bundles = {"underground-tech-pack-0.1.0.mcaddon": runtime,
               "underground-tech-pack-0.1.0-dev.mcaddon": runtime + [("utp-lab.mcpack", pack_bytes(root / LAB))]}
    checksums = []
    for name, entries in bundles.items():
        data = archive(entries)
        (destination / name).write_bytes(data)
        checksums.append(f"{hashlib.sha256(data).hexdigest()}  {name}")
    (destination / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
    print("\n".join(checksums))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("render", "validate", "build"))
    args = parser.parse_args()
    try:
        {"render": render, "validate": validate, "build": build}[args.command]()
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"UTP {args.command} failed: {error}\n")
    print(f"UTP {args.command}: passed")
