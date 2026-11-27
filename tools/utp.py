#!/usr/bin/env python3
"""Validate and package the core metal building set using only Python's standard library."""

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
VERSION = (0, 1, 2)
CORE_METALS = {
    "navy_metal": "UTP Navy Metal",
    "smooth_navy_metal": "UTP Smooth Navy Metal",
    "reinforced_panel": "UTP Reinforced Gunmetal",
    "grated_floor": "UTP Grated Floor",
    "ceiling_panel": "UTP Industrial Ceiling",
    "metal_trim": "UTP Metal Trim",
    "vent_panel": "UTP Vent Panel",
    "hazard_panel": "UTP Warning Accent",
}
PIPE_PROTOTYPES = {
    "straight_pipe": "UTP Straight Pipe",
    "elbow_pipe": "UTP Elbow Pipe",
}
ASSETS = CORE_METALS | PIPE_PROTOTYPES
SYMBOLS = {"N": "navy_metal", "G": "gunmetal", "S": "dull_steel", "T": "dark_trim", "A": "amber"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def texture_bytes(root=ROOT, asset="navy_metal"):
    palette = read_json(root / PACK / "art/palette.json")
    rows = (root / PACK / "art" / (asset + ".pixels")).read_text().splitlines()
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
                '<text x="28" y="40" font-size="24">Underground Tech Pack · core metal palette</text>',
                '<text x="28" y="67" font-size="14">Navy metal first. Amber marks restrained warning details.</text>']
    for i, (name, color) in enumerate(palette.items()):
        x, y = 28 + (i % 4) * 194, 94 + (i // 4) * 154
        elements.extend([f'<rect x="{x}" y="{y}" width="166" height="86" fill="{color}" stroke="#607080"/>',
                         f'<text x="{x}" y="{y+109}" font-size="15">{name.replace("_", " ").title()}</text>',
                         f'<text x="{x}" y="{y+130}" font-size="13">{color}</text>'])
    elements.extend(['<text x="28" y="419" font-size="13">Original industrial palette · no emissive materials</text>', '</g></svg>'])
    return "\n".join(elements) + "\n"


def asset_sheet(root=ROOT):
    """Source-art contact sheet, not a Minecraft screenshot."""
    palette = read_json(root / PACK / "art/palette.json")
    elements = ['<svg xmlns="http://www.w3.org/2000/svg" width="840" height="480" viewBox="0 0 840 480">',
                '<rect width="840" height="480" fill="#101820"/>',
                '<g font-family="sans-serif" fill="#E2E9EE">',
                '<text x="20" y="28" font-size="18">Core Metal Building Set · source artwork (not in-game evidence)</text>']
    for i, (asset, label) in enumerate(CORE_METALS.items()):
        x, y = 20 + (i % 4) * 210, 48 + (i // 4) * 210
        rows = (root / PACK / "art" / (asset + ".pixels")).read_text().splitlines()
        for row, pixels in enumerate(rows):
            for run in re.finditer(r"(.)\1*", pixels):
                color = palette[SYMBOLS[run.group()[0]]]
                elements.append(f'<rect x="{x + run.start() * 10}" y="{y + row * 10}" width="{len(run.group()) * 10}" height="10" fill="{color}"/>')
        elements.append(f'<text x="{x}" y="{y + 181}" font-size="14">{label}</text>')
    return "\n".join(elements + ['</g></svg>']) + "\n"


def render(root=ROOT):
    for asset in ASSETS:
        (root / PACK / "resource-pack/textures/blocks" / (asset + ".png")).write_bytes(texture_bytes(root, asset))
    (root / PACK / "art/palette.svg").write_text(palette_svg(root), encoding="utf-8")
    (root / PACK / "art/blocks.svg").write_text(asset_sheet(root), encoding="utf-8")


def validate(root=ROOT):
    pack = root / PACK
    manifests = [read_json(root / folder / "manifest.json") for folder in
                 (PACK / "behavior-pack", PACK / "resource-pack", LAB)]
    identifiers = []
    for manifest, kind in zip(manifests, ("data", "resources", "data")):
        require(manifest["format_version"] == 2, "Expected manifest format 2")
        header, modules = manifest["header"], manifest["modules"]
        require(len(modules) == 1 and modules[0]["type"] == kind, "Wrong pack module")
        require(header["version"] == modules[0]["version"] == list(VERSION), "Version mismatch")
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
    require(CORE_METALS.keys() <= {path.stem for path in blocks}, "Expected all eight M1 blocks")
    require({path.stem for path in blocks} == set(ASSETS), "Expected exactly the cataloged blocks")
    atlas = read_json(pack / "resource-pack/textures/terrain_texture.json")
    sounds = read_json(pack / "resource-pack/blocks.json")
    labels = (pack / "resource-pack/texts/en_US.lang").read_text().splitlines()
    require(set(atlas["texture_data"]) == {"steelwater_utp_" + name for name in ASSETS}, "Unexpected atlas entries")
    require(set(sounds) == {"format_version"} | {"steelwater_utp:" + name for name in ASSETS}, "Unexpected sound entries")
    for path in blocks:
        asset = path.stem
        identifier = "steelwater_utp:" + asset
        block_file = read_json(path)
        require(block_file["format_version"] == "1.21.80", "Unexpected block format")
        block = block_file["minecraft:block"]
        prototype = asset in PIPE_PROTOTYPES
        expected_keys = {"description", "components"}
        if prototype:
            expected_keys.add("permutations")
        require(set(block) == expected_keys, "Unexpected block behavior; review decorative-only scope")
        description = block["description"]
        require(description["identifier"] == identifier and description["menu_category"] == {"category": "construction"},
                "Block identifier or Creative discovery changed")
        components = block["components"]
        require(set(components) == {"minecraft:geometry", "minecraft:material_instances", "minecraft:collision_box",
                                    "minecraft:selection_box", "minecraft:destructible_by_mining",
                                    "minecraft:destructible_by_explosion", "minecraft:light_dampening"},
                "Unexpected component; review decorative-only scope")
        if prototype:
            validate_pipe(pack, asset, block)
        else:
            require(set(description) == {"identifier", "menu_category"}, "Unexpected core metal states")
            require(components["minecraft:geometry"] == "minecraft:geometry.full_block", "Expected full cube")
            require(components["minecraft:collision_box"] is True and components["minecraft:selection_box"] is True,
                    "Core metals must have full-cube collision and selection")
        require(components["minecraft:destructible_by_mining"] == {"seconds_to_destroy": 3}
                and components["minecraft:destructible_by_explosion"] == {"explosion_resistance": 6}
                and components["minecraft:light_dampening"] == (0 if prototype else 15), "Unexpected physical behavior")
        texture_key = "steelwater_utp_" + asset
        require(components["minecraft:material_instances"] == {"*": {"texture": texture_key, "render_method": "opaque"}},
                "Expected one opaque material on all faces")
        texture = atlas["texture_data"][texture_key]["textures"]
        require(texture == "textures/blocks/" + asset, "Unexpected atlas texture reference")
        require((pack / "resource-pack" / (texture + ".png")).read_bytes() == texture_bytes(root, asset),
                "Texture missing, corrupt, or stale; run render")
        require(labels.count(f"tile.{identifier}.name={ASSETS[asset]}") == 1, "Missing or duplicate display name")
        require(sounds[identifier] == {"sound": "metal"}, "Missing metal sound")
    require(not (pack / "behavior-pack/functions").exists() and not (pack / "behavior-pack/scripts").exists(),
            "Player pack must not include test functions or scripts")
    require((pack / "art/palette.svg").read_text() == palette_svg(root), "Palette sheet stale; run render")
    require((pack / "art/blocks.svg").read_text() == asset_sheet(root), "Asset sheet stale; run render")
    require(not (root / LAB / "functions/tick.json").exists(), "Lab setup must be manual")


def validate_pipe(pack, asset, block):
    components = block["components"]
    model_path = pack / "resource-pack/models/blocks" / (asset + ".geo.json")
    model, = read_json(model_path)["minecraft:geometry"]
    geometry = "geometry.steelwater_utp." + asset
    require(components["minecraft:geometry"] == model["description"]["identifier"] == geometry,
            "Pipe geometry reference mismatch")
    require(model["description"]["texture_width"] == model["description"]["texture_height"] == 16,
            "Expected a 16×16 pipe texture")
    position = {"minecraft:placement_position": {"enabled_states": ["minecraft:block_face"]}}
    direction = {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"]}}
    expected = position if asset == "straight_pipe" else position | direction
    require(block["description"]["traits"] == expected, "Unexpected pipe placement states")
    require(set(block["description"]) == {"identifier", "menu_category", "traits"},
            "Unexpected pipe description")
    rules = block["permutations"]
    require(len(rules) == len({rule["condition"] for rule in rules}) == 6, "Missing pipe orientations")
    for rule in rules:
        transform = rule["components"]
        require(set(transform) == {"minecraft:transformation"}, "Pipe orientations must only rotate the block")
        rotation = transform["minecraft:transformation"]
        require(set(rotation) == {"rotation"} and len(rotation["rotation"]) == 3
                and all(angle % 90 == 0 for angle in rotation["rotation"]), "Invalid pipe rotation")
    box = components["minecraft:collision_box"]
    require(box == components["minecraft:selection_box"], "Pipe collision and selection must match")
    cubes = [cube for bone in model["bones"] for cube in bone["cubes"]]
    for axis in range(3):
        start = min(cube["origin"][axis] for cube in cubes)
        end = max(cube["origin"][axis] + cube["size"][axis] for cube in cubes)
        require(box["origin"][axis] == start and box["size"][axis] == end - start,
                "Pipe bounds must enclose the geometry")


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
    version = ".".join(map(str, VERSION))
    bundles = {f"underground-tech-pack-{version}.mcaddon": runtime,
               f"underground-tech-pack-{version}-dev.mcaddon": runtime + [("utp-lab.mcpack", pack_bytes(root / LAB))]}
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
