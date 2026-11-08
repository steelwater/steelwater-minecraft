# Underground Tech Pack conventions

Milestone 0 implementation conventions, 6 October 2026. Product scope remains in the [canonical Crew Brief](https://docs.google.com/document/d/1WGthGOh2_vrdjSrjwmkx6YfAtmFI9gC1AgpEYUUmZ-k/edit).

## Identity and versions

- Add-on slug: `underground-tech-pack`.
- Namespace: `steelwater_utp`. Treat it and the block identifier as stable once worlds use them.
- Prototype: **UTP Navy Metal**, identifier `steelwater_utp:navy_metal`.
- Initial development label: **v0.1**. Manifest representation: `[0, 1, 0]`; package filename: `0.1.0`.
- Keep header/module/dependency versions synchronized. Increment patch for corrective pack updates, minor for later approved milestones, major for approved incompatible changes.
- Keep pack UUIDs stable on updates; do not generate replacements to solve import problems. New block identifiers must not replace existing saved-world IDs.
- The initial block format and minimum engine are **1.21.80**, a documented implementation baseline, not a tested Android compatibility claim. The Captain confirmed Android **1.26.52.3** as the target build on 6 October 2026; Dan reported Android acceptance passed on 9 October 2026 (see validation notes). No experiments or scripts are requested.
- Distribution licensing has not been selected. The brief says free, which does not itself grant redistribution or reuse rights; no license has been invented.

| Pack | Header UUID | Module UUID |
| --- | --- | --- |
| Behavior | `8f4306b2-c16d-403c-93cc-f07adf8dc560` | `c6223be1-d729-40d3-bafc-0d5e55371708` |
| Resources | `b2409bcb-ec4c-4b74-94fa-a3fb045a9ad8` | `663ff5ea-7906-468a-bdaf-688e1b576351` |
| Lab (development only) | `1beaa4f5-8967-407b-a32b-68698669d9a5` | `8766c159-746f-4dbb-9f05-01cfa0b58a4f` |

The behavior pack depends on the resource header UUID. The optional lab depends on the behavior header UUID. All six UUIDs are different.

## Source layout

The collection repository lives directly in `steelwater-minecraft/`. The supplied `starter repo/` contents were promoted to this root rather than retaining a redundant nested repository. The starter documentation was preserved in the initial `main` commit.

- `addons/underground-tech-pack/behavior-pack/`: the one full-cube block definition. A behavior pack is necessary to register a custom block; it adds no interactive machinery.
- `addons/underground-tech-pack/resource-pack/`: texture atlas, compiled 16×16 PNG, sounds, English label, manifest.
- `addons/underground-tech-pack/art/`: editable palette JSON and pixel-grid source, plus the SVG palette sheet.
- `addons/underground-tech-pack/docs/`: implementation conventions and originality rules.
- `addons/underground-tech-pack/tests/`: observed validation and device playtest checklist.
- `worlds/underground-tech-pack-lab/`: instructions and a separate development-only behavior pack with a manually invoked setup function. A saved world still needs to be created in Minecraft.
- `tools/utp.py`, `tests/test_utp.py`: standard-library build/validation and regression tests; Python 3.12+.
- `dist/`: ignored local packages and checksums; never the canonical release archive. No release is authorized by this milestone implementation alone.

Use lowercase `snake_case` for asset names and files, lowercase hyphens for top-level project folders. Texture atlas keys include the `steelwater_utp_` prefix. Resource paths omit the PNG extension; filesystem names and references must match case exactly. Locale keys follow `tile.<namespace>:<block>.name`.

Keep future assets inside the relevant `blocks/`, `textures/`, and `art/` folders. Add models or other asset-type folders when needed; do not create speculative systems now.

## Visual foundation

See [palette sheet](../art/palette.svg) and [editable colors](../art/palette.json). Navy is the identity, gunmetal frames the panel, dull steel marks sparse fasteners, dark trim separates tiles. Cyan, green, amber, and red are reserved accents for later approved assets. They are palette colors only, not emissive materials or implemented display assets.

`navy_metal.pixels` is the editable 16×16 design: `N` navy, `G` gunmetal, `S` dull steel, `T` trim. All six cube faces use the same texture. Run `python3 tools/utp.py render` after editing palette or pixels, then validate and review the output. The PNG is committed as required runtime source content; release archives are ignored.

The prototype uses a one-metre full cube with full collision and selection, opaque rendering, metal sound, and ordinary break/place behavior. It has no direction state, rotation interaction, light emission, crafting recipe, or survival progression contract. Creative placement is the Milestone 0 test path.

## Technical references

Consulted 6 October 2026:

- [Microsoft: simplest custom block](https://learn.microsoft.com/en-us/minecraft/creator/documents/addcustomdieblock?view=minecraft-bedrock-stable)
- [Microsoft: block description and Creative menu category](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockdescription?view=minecraft-bedrock-stable)
- [Microsoft: geometry component](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_geometry?view=minecraft-bedrock-stable)

The validator checks this small project's contracts and references. It is not a full Bedrock schema validator and cannot prove runtime compatibility, UI discovery, collision, or persistence.
