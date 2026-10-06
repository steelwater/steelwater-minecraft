# UTP Development Lab

Reusable test-world **setup kit** for v0.1. A saved Minecraft world has **not yet been created or verified**. Complete creation and save/reopen testing before marking this deliverable complete.

## Create once, reuse

1. Build and import `dist/underground-tech-pack-0.1.0-dev.mcaddon` using the [add-on instructions](../../addons/underground-tech-pack/README.md).
2. Create a new empty Creative/Flat/Peaceful world named **UTP Development Lab**. Enable cheats and coordinates, leave experiments off, and activate the main behavior/resource packs and lab pack.
3. Use `/tp @s 15 90 10` to load the site. Run `/function utp/setup` only in this new dedicated world.

**Setup replaces x=0–31, y=79–87, z=0–23.** It changes time/weather/mob-spawning rules and teleports the invoking player. It is manual, never run on load. Re-running rebuilds the area; do not rerun after adding samples you want to preserve. The function is excluded from the player bundle.

| Station | Coordinates | Check |
| --- | --- | --- |
| Daylight wall | x=2–9, z=2 | 8×4 repetition, seams, near/far readability |
| Daylight floor | x=2–9, z=5–8 | Top faces, repetition, walking surface |
| Single block | x=12, z=2 | Full cube, six faces, outline, place/break |
| Collision wall/step | x=12–14, z=5–8 | Wall collision, jumping and standing |
| Vanilla controls | x=17–21, z=2 | Iron/stone versus prototype scale |
| Dark room | x=2–12, z=13–22 | Low-light readability, unwanted glow |
| Lit room | x=17–27, z=13–22 | Sea-lantern lighting and color |
| Reserved lane | x=24–30, z=2–10 | Future side-by-side comparison |

Floor level is y=79; samples begin at y=80. Rooms have western entrances. The dark-room baffle limits daylight; compare an actual cave if it reveals different readability. No Milestone 1 assets are included.

The prototype has no orientation state. Place it facing north, south, east, and west and confirm consistent appearance; directional rotation testing becomes applicable only when a later asset requires it.

Enable Content Log GUI/file options under Minecraft Creator settings when available. Record exact build, graphics mode, warnings and screenshots. Missing textures, install failures, broken references or relevant pack warnings block completion.

Save and exit, close Minecraft, reopen, and revisit all stations. Confirm packs and samples persist with the same texture/collision. Save the world under the same name and record results in [validation notes](../../addons/underground-tech-pack/tests/validation.md).

An approved `.mcworld` export can later be archived with the exact tested packs in GitHub Releases. Generated world databases/archives stay outside Git. This branch contains no saved world export.
