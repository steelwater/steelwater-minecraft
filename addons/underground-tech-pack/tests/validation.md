# Milestone 0 validation

6 October 2026 — **source/package foundation implemented; Android acceptance blocked**.

## Observed local checks

- Python 3.14.7 on macOS: `python3 tools/utp.py validate` passed.
- Four regression tests passed: reproducible archive structure and player/lab separation; corrupt texture rejection; broken resource dependency rejection; unexpected interactive component rejection.
- `python3 tools/utp.py build` passed. Player/development archives and SHA-256 checksums were produced; archive integrity and manifests at each inner `.mcpack` root were checked.
- `python3 -m compileall -q tools tests` passed. No separate formatter, linter or type checker is configured; none was installed.
- Original 16×16 PNG opened for visual inspection: navy panel, trim and fasteners are present. This does not prove Minecraft rendering.
- GitHub Actions runs validation, tests, build, syntax and whitespace checks under Python 3.12. See PR checks for remote results.
- Connected Android emulator had no `com.mojang.minecraftpe` package. No Minecraft UI or world was available for execution.

## Android acceptance — pending

| Evidence | Result |
| --- | --- |
| Tester, date, Android device/OS | Pending |
| Exact Minecraft build and graphics mode | Captain confirmed **1.26.52.3**; graphics mode pending |
| Package filename + SHA-256 tested | Pending |
| All three development-bundle packs import cleanly | Not run |
| Packs active, experiments off | Not run |
| Construction search finds UTP Navy Metal | Not run |
| Give command, placement, break and replacement | Not run |
| All six faces, held/inventory appearance and textures correct | Not run |
| Daylight, dark-room and lit-room readability | Not run |
| One-block scale, collision and selection align | Not run |
| Wall/floor repetition readable near and far | Not run |
| Placement from four directions consistent | Not run; no directional state |
| No relevant content-log warnings or broken references | Not run |
| Dedicated reusable lab world created and saved | Not run |
| Close app/reopen world preserves packs and samples | Not run |

Record failures verbatim with reproduction steps; resolve them before passing the milestone. The local validator checks narrow project contracts, not the full Bedrock schema. Runtime testing is authoritative.

## Android Skills applicability

Reviewed Google's [Android Skills catalog](https://github.com/android/skills) and [testing/testing-setup](https://github.com/android/skills/blob/main/testing/testing-setup/SKILL.md). Native build, dependency-injection, Compose/Espresso and APK test setup do not apply to a JSON/PNG add-on hosted by Minecraft. No Android framework was installed. R8, AGP migration, Play, navigation and native app security/performance skills are outside scope. Device playtesting remains mandatory.

## Boundaries and next step

No Milestone 1 assets, gameplay scripts, recipes, interactions, marketplace submission, license selection, release tag, deployment or production world changes. The setup kit is not a saved world. `main` retains the starter as rollback baseline.

Next: Dan runs the Android checklist on **1.26.52.3** with the exact development archive. Record evidence, resolve errors, then request final review. Milestone 0 remains incomplete until these checks pass.
