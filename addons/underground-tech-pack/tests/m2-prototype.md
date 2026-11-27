# Milestone 2 pipe prototype

Status on 27 November 2026 is **In Progress**. The straight pipe and elbow are ready for device verification as development build 0.1.2. The remaining six families and the final M2 PR depend on verifying the prototype in Minecraft. [Issue #5](https://github.com/steelwater/steelwater-minecraft/issues/5) · [Roadmap](https://docs.google.com/document/d/1CPZ1EgoX2-QF5DlEAsDjBctHagWDV2a0npEUHUG3n9c/edit)

The prototype retains the 1.21.80 format/minimum, the six pack UUIDs and all M1 definitions and textures. It uses block placement traits and quarter-turn transformations, centered 6×6 pipe ends, 16×16 textures and one bounding box per piece. Build 0.1.2 identifies the interim test packages ahead of the planned v0.2 grouping. [Microsoft block traits](https://learn.microsoft.com/en-us/minecraft/creator/documents/intro-block-traits) · [Microsoft block transformations](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_transformation)

## Reproduction and observed checks

From the repository root:

```sh
python3 tools/utp.py render
python3 tools/utp.py validate
python3 -m unittest discover -s tests -v
python3 tools/utp.py build
python3 -m compileall -q tools tests
git diff --check
(cd dist && shasum -a 256 -c SHA256SUMS)
```

| Package in `dist/` | SHA-256 |
| --- | --- |
| `underground-tech-pack-0.1.2.mcaddon` | `59aa5a521dd63d495461c266e2fa733f05f8aebed01f08e6f7b88b5358184804` |
| `underground-tech-pack-0.1.2-dev.mcaddon` | `e62cce723ae7f0aca5babb5ce04d0d90095a9e480b33da970ef8a1604f63aa5b` |

Local validation checks references, manifest versions, registered placement traits, rectangular bounds and Creative labels. Tests check stable M0/M1 behavior, centered model faces and deterministic packaging with the lab included only in the development build. CI for the final milestone and Minecraft testing are pending.

## Device checklist

No Android device was attached, so the Minecraft version, device model, screenshots and in-game outcomes are pending. Use a fresh dedicated world and report exact Minecraft and Android versions, device, graphics mode, package checksum and content-log warnings. Use a backed-up copy for existing-world upgrade tests. Preserve the original world and its matching packs.

| Check | Expected | Status |
| --- | --- | --- |
| Import | All three packs appear and activate with experiments off | NOT TESTED |
| Discovery and rotation | Both names and icons appear in Construction. Place, break and replace the straight on all axes and the elbow on side, top and underside faces | NOT TESTED |
| Joins | Run the [prototype lab](../../../worlds/underground-tech-pack-lab/README.md#milestone-2-prototype-station). Check seams and clipping on both runs. Build the runs manually and capture screenshots | NOT TESTED |
| Selection and collision | Outlines and collision follow the rotated bounds. Check the elbow's inside corner for usability | NOT TESTED |
| Lighting and persistence | Inspect in bright and dim light, then save and reopen. Confirm both orientations and M1 content persist | NOT TESTED |
| Launcher | Check success once, cancel and retry. Time the copy/load. If copying exceeds three seconds, rotate and force-stop/reopen during copying in separate attempts | NOT TESTED |

The [M1 device checklist](m1-validation.md) remains pending. If geometry or orientation fails in Bedrock, isolate the failing state before implementing the tee, cap, valve, conduit, utility box and drain.
