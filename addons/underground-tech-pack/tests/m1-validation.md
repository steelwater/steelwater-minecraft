# Milestone 1 verification and device handoff

17 November 2026. Scope: [issue #3](https://github.com/steelwater/steelwater-minecraft/issues/3), [M1 brief](https://docs.google.com/document/d/1oQAWaeWqeAK0ZclwmW7eTkEYGM6KrrjGK0w_q7U8DEA/edit), eight decorative core metal blocks. Status: **Implemented; Android acceptance pending**. No in-game screenshots or M1 device passes are claimed.

## Observed automated and source checks

- `python3 tools/utp.py render` and `validate`: passed. All eight definitions resolve to their own compiled 16×16 texture, metal sound and unique English inventory name; full-cube collision and decorative-only component contracts pass.
- `python3 -m unittest discover -s tests -v`: nine tests passed. Coverage includes complete/reproducible nested packages, player/lab separation, broken dependency rejection, corrupt texture rejection, unexpected interactive components, missing piece/name rejection, incorrect texture references, eight distinct textures, original prototype definition/texture hashes and all six stable pack UUIDs.
- `python3 tools/utp.py build`: passed. Player and development bundles have identical player packs; the development bundle adds manual lab functions. SHA-256 values below identify the local test packages.
- `python3 -m compileall -q tools tests` and `git diff --check`: passed. No separate Python linter or type checker is configured.
- Enlarged source-art contact sheet inspected: original riveted panel retained; seven new surfaces are distinct and use the original palette. Amber occupies only the warning band. This is source-art inspection, not proof of Minecraft lighting/tiling/rendering.
- M0 block JSON, `.pixels`, compiled PNG, original setup function, namespace, engine/format baseline and all UUIDs are preserved. Manifest/dependency versions advance together to the **0.1.1 M1 development test build**, not roadmap v0.2 final.

## Launcher carry-forward checks

A fresh launcher and instrumentation APK were built from the merged lifecycle-fix source into **`dist/m1-launcher/`**, preserving the older APK elsewhere. Both builds passed javac type checking and APK v2/v3 signature verification. Existing Java 8/deprecated-inset warnings remain. No launcher code, permissions, dependencies or test behavior changed in M1.

Launcher test APKs were installed on disposable `emulator-5554`, Android 16. Existing `ProviderTests` passed byte integrity, display name/size, write rejection and unknown-path rejection. Existing `ImportTests` passed held-open slow-copy rotation, one source read, accurate missing-Minecraft retry, no repeated import after a second rotation, corrupt-ZIP recovery after rotation, and background completion waiting for resume. Minecraft package inventory was empty, so these tests do **not** prove a Minecraft handoff/import or process-kill recovery.

Fresh launcher APK: `dist/m1-launcher/steelwater-addon-launcher-0.1-debug.apk`.
SHA-256: `e1ca4ea4b02ed8ea857e07b09c58227e8ab5ce348c3fa0ec28043651b2f9d25a`.
Only this application APK is for owner testing; do not install/distribute the instrumentation APK on a personal device. Local signing identity and these bytes may differ from ephemeral-key CI builds.

Google's current [testing/testing-setup](https://github.com/android/skills/blob/main/testing/testing-setup/SKILL.md) was reviewed. Existing platform instrumentation and build checks apply. Installing DI/UI/coverage frameworks would exceed this mission's no-new-dependencies boundary and is unnecessary for unchanged launcher source. R8, Play, AGP migrations, navigation and Compose skills do not apply. Minecraft-hosted JSON/PNG assets require Bedrock playtesting rather than native UI tests.

## Owner acceptance — all pending

Use a new dedicated world with the current development bundle. Record tester/date, device model, Android OS, exact Minecraft build, graphics mode, filenames and SHA-256, experiment settings, and any content-log warnings. The previous target was **1.26.52.3**, not an observed M1 test version.

| Test | Required evidence | Status |
| --- | --- | --- |
| A — Clean install | All three development packs import/activate without warnings; experiments off | Pending |
| B — Discovery | Eight distinct UTP items in Construction and successful give commands | Pending |
| C — Placement | Place/break/replace all eight; six faces; held/inventory view; collision/selection; four approach directions | Pending |
| D — Visual quality | 5×5 walls, floors and ceilings, bright and dim light; seams, scale, readability and repetition | Pending |
| E — Small room | `utp/m1` room and an owner-built compact room use all eight pieces coherently; trim/vent full-cube choice is useful | Pending |
| F — Regression/persistence | Original navy panel still works; save/exit/reopen retains packs and samples | Pending |
| Launcher import | Fresh fixed APK opens actual Minecraft and Minecraft reports successful current-pack import | Pending |
| Launcher rotation | Rotate during an active/slow copy; observe exactly one Minecraft handoff | Pending |
| Launcher cancel/retry | Cancel picker; retry succeeds; failed selection offers usable recovery | Pending |
| Launcher interruption | Kill process during copying; reopen and confirm accurate retry, then successful import | Pending |

Capture actual Minecraft screenshots: all eight samples, compact-room interior, bright/dim close-ups and any warnings. The [source-art sheet](../art/blocks.svg) is explicitly not a screenshot. Use the [lab instructions](../../../../worlds/underground-tech-pack-lab/README.md#milestone-1-station); source-only/manual lab commands have not been executed in Minecraft here.

## Boundaries and rollback

No scripts, interactions, recipes, custom sounds, pipes or later-milestone assets. No new durable dependencies, release/tag, deployment, merge or production-world changes. M0 source remains in Git and the original setup function remains available. Preserve existing worlds and matching packs before importing stable-UUID updates; do not downgrade a world containing M1 IDs. Uninstalling the launcher does not change source files or Minecraft worlds.

Next: review the M1 PR and CI, then owner device testing and screenshot evidence. Keep the PR open until explicit owner approval; do not mark M1 Verified or Released merely because automated checks pass.
