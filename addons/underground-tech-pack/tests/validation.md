# Milestone 0 validation

9 October 2026 — **Android acceptance passed, reported by Dan.** [Captain acceptance](https://github.com/steelwater/steelwater-minecraft/pull/1#issuecomment-6074793838); screenshots and placement confirmation are in the [earlier test report](https://github.com/steelwater/steelwater-minecraft/pull/1#issuecomment-6051288307).

Dan explicitly confirmed that Android device testing was complete with no issues and requested that the Android checklist be recorded as passed. The results below rely on that attestation; they are not independent Crew observations. Device model, Android OS version, graphics mode, and a device-computed package checksum were not supplied.

## Observed local checks

- Python 3.14.7 on macOS: `python3 tools/utp.py validate` passed.
- Four regression tests passed: reproducible archive structure and player/lab separation; corrupt texture rejection; broken resource dependency rejection; unexpected interactive component rejection.
- `python3 tools/utp.py build` passed. Player/development archives and SHA-256 checksums were produced; archive integrity and manifests at each inner `.mcpack` root were checked.
- `python3 -m compileall -q tools tests` passed. No separate formatter, linter or type checker is configured; none was installed.
- Original 16×16 PNG opened for visual inspection: navy panel, trim and fasteners are present. This does not prove Minecraft rendering.
- GitHub Actions runs validation, tests, build, syntax and whitespace checks under Python 3.12. See PR checks for remote results.
- Connected Android emulator had no `com.mojang.minecraftpe` package. No Minecraft UI or world was available for execution.

## Android acceptance — passed (Captain-reported)

| Evidence | Result |
| --- | --- |
| Tester, date, Android device/OS | Dan; placement report 8 October, full acceptance 9 October 2026; tablet model/OS not recorded |
| Exact Minecraft build and graphics mode | Captain-confirmed target **1.26.52.3**; graphics mode not recorded |
| Package filename + SHA-256 tested | Supplied development bundle `underground-tech-pack-0.1.0-dev.mcaddon`; supplied SHA-256 `28f9883295c67be02d0d6c0d9af4fe529d1b689b90aa12878e3c08db5b714226`; device checksum not independently recorded |
| All three development-bundle packs import cleanly | Passed — Captain-reported |
| Packs active, experiments off | Passed — Captain-reported |
| Construction search finds UTP Navy Metal | Passed — Captain-reported |
| Give command, placement, break and replacement | Passed — Captain-reported |
| All six faces, held/inventory appearance and textures correct | Passed — Captain-reported |
| Daylight, dark-room and lit-room readability | Passed — Captain-reported |
| One-block scale, collision and selection align | Passed — Captain-reported |
| Wall/floor repetition readable near and far | Passed — Captain-reported |
| Placement from four directions consistent | Passed — Captain-reported; no directional state |
| No relevant content-log warnings or broken references | Passed — Captain-reported |
| Dedicated reusable lab world created and saved | Passed — Captain-reported |
| Close app/reopen world preserves packs and samples | Passed — Captain-reported |

Record failures verbatim with reproduction steps; resolve them before passing the milestone. The local validator checks narrow project contracts, not the full Bedrock schema. Runtime testing is authoritative.

## Android Skills applicability

Reviewed Google's [Android Skills catalog](https://github.com/android/skills) and [testing/testing-setup](https://github.com/android/skills/blob/main/testing/testing-setup/SKILL.md). Native build, dependency-injection, Compose/Espresso and APK test setup do not apply to a JSON/PNG add-on hosted by Minecraft. No Android framework was installed. R8, AGP migration, Play, navigation and native app security/performance skills are outside scope. Device playtesting was subsequently accepted by Dan.

## Boundaries and next step

No Milestone 1 assets, gameplay scripts, recipes, interactions, marketplace submission, license selection, release tag, deployment or production world changes. The repository contains the setup kit; the saved world remains on the test device per Captain acceptance, with no world export archived. `main` retains the starter as rollback baseline.

Next: complete First Officer review and obtain the merge instruction after CI passes on this documentation update. No Milestone 1 work is authorized.
