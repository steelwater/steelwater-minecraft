# Steelwater Add-on Launcher — Android test utility v0.1

Requested by Dan on 8 October 2026 after Android's file browser offered no Minecraft handler for `.mcaddon`. This separate utility picks one file and explicitly opens the installed Google Play Minecraft activity with a readable content URI. It cannot guarantee Minecraft accepts the import; check Minecraft's own notification.

## Install and use

Install `dist/steelwater-addon-launcher-0.1-debug.apk` on Android 8.0 or later. Android may ask you to allow installation from the browser/file manager delivering this APK. This is a locally debug-signed test build, not a Play Store release.

Open **Steelwater Add-on Launcher**, tap **Choose .mcaddon**, and choose your download. Minecraft must be installed and enabled in the same Android profile. Screen rotation preserves an in-progress copy. The resumed screen handles its result once. If Android kills the process, choose the file again when prompted; copying is not a persistent background job.

The app checks the extension and ZIP readability, copies up to 256 MB, then opens Minecraft directly. Minecraft remains responsible for validating and importing the pack. Choosing a file explicitly authorizes that handoff.

## Scope and privacy

No internet, account, analytics, ads, broad storage permission, root access, or access to Minecraft's private files. The picker grants access to the selected file only. A copy stays in this app's private cache so Minecraft can read it asynchronously; copies older than 24 hours are removed on the next selection. Android may also evict cache files. Originals and Minecraft worlds are never modified by this app. Clear this app's cache or uninstall it to remove its temporary copies.

The provider is not exported. Minecraft receives a temporary read URI grant; writes and paths other than app-created UUID-named `.mcaddon` files are rejected. The URI ends in `.mcaddon`, has queryable name/size metadata, and uses `application/octet-stream`. The explicit component is discovered from the installed Minecraft launch intent, avoiding reliance on Android's extension-based chooser or an invented activity name.

## Build

From the repository root:

```sh
python3 tools/android-addon-launcher/build.py
python3 tools/android-addon-launcher/build.py --test
```

Requires an existing Android SDK platform 35, build-tools 35.0.0, JDK, and Android debug keystore. Defaults use this Mac's Android Studio JBR and SDK. Override `ANDROID_HOME`, `JAVA_HOME`, and `ANDROID_DEBUG_KEYSTORE` where needed. The debug keystore uses Android's conventional debug alias/password. Keys and build outputs are not committed. Set `LAUNCHER_OUTPUT_DIR` to a separate directory when rebuilding for verification, so the exact Captain-tested APK is preserved.

This small platform-Java utility is built with javac, aapt2, d8, zipalign and apksigner. No Gradle, AndroidX or third-party dependencies were added. Retained deprecated inset accessors support Android 8+; compiler deprecation warnings are known. This is not a general Android project framework or store-release setup.

## Verification

Run the focused Android provider tests on a chosen emulator:

```sh
adb -s DEVICE install -r dist/steelwater-addon-launcher-0.1-debug.apk
adb -s DEVICE install -r dist/steelwater-addon-launcher-tests.apk
adb -s DEVICE shell am instrument -w com.steelwater.addonlauncher.tests/.ProviderTests
adb -s DEVICE shell am instrument -w com.steelwater.addonlauncher.tests/.ImportTests
```

Tests verify shared byte integrity, display-name/size metadata, write rejection and unknown-path rejection. Android enforces external URI permissions; these in-process tests do not prove the cross-app grant or Minecraft import.

Manual checks: picker opens, cancellation recovers, valid add-on copies and reaches the missing-Minecraft message, invalid extension/archive rejected, portrait/landscape readable. Neither emulator had Minecraft installed during Crew testing. On 9 October 2026 Dan reported that the launcher works well on his tablet and requested Uplink. This is Captain-reported end-to-end acceptance.

Google's `testing/testing-setup` skill was reviewed as required. Native testing and device verification apply, but the handbook's no-unapproved-dependencies constraint takes precedence over installing Hilt, Espresso, Robolectric, screenshot/coverage frameworks for this tiny helper. Platform Instrumentation and manual UI checks are used. No R8/Play/navigation migration applies.

References: https://developer.android.com/training/data-storage/shared/documents-files and https://developer.android.com/training/secure-file-sharing/share-file

Development is isolated on `feature/android-addon-launcher`. PR #1 merged on 8 November 2026; PR #2 now targets `main`. Uplink was authorized on 9 October 2026. No PR merge is authorized. The APK is a test handoff, not a canonical release artifact. Dan explicitly authorized the APK upload on 8 October 2026. Uploaded and verified in the project Drive dist folder: https://drive.google.com/file/d/1tpcBV1PPZqpQkZ8JRO8_3M2uC1tHp8HF/view . Rollback: uninstall the helper; add-on source remains unchanged.

## Observed results — 8 October 2026

Android 16 emulator: all four provider assertions passed. An unrelated ADB caller was denied provider access. Manual valid-file selection, missing-Minecraft message, picker cancellation, wrong-extension rejection and corrupt-ZIP rejection passed. Portrait and landscape screenshots were inspected; content and controls were readable. APK signature verification passed (v2/v3). Build script syntax and all new-file whitespace checks passed. No actual Minecraft import, cross-app read by Minecraft, real-tablet check, or remote CI run was performed.

APK SHA-256: `5de5cc1605db8b69e7f0a35d2f40500c4ee0182cfca7fdccda3c99ee4cadfc6d`. This checksum identifies the original Captain-tested APK, preserved for distribution.

## Uplink verification — 9 October 2026

Runtime Java, manifest and resources remain the tested implementation. Only the build output directory option, CI, and documentation were added for Uplink. Local provider/manual evidence from 8 October is retained; no device is connected for a new instrumentation run. CI builds the app and provider-test APKs and checks signatures with an ephemeral debug key; it does not reproduce the local signing identity or replace the Captain-tested attachment. CI does not execute emulator instrumentation. No standalone lint/type checker is configured; javac performs Java type checking. Known Java 8/deprecated inset compiler warnings remain.

## Activity recreation fix — 17 November 2026

Scope: [PR #2 review follow-up](https://github.com/steelwater/steelwater-minecraft/pull/2#issuecomment-6933191772), separate from Underground Tech Pack Milestone 1.

The copy uses application context and a retained platform non-configuration object. Only the resumed Activity observes completion; pausing detaches it. Completion is consumed on the main thread before handoff, so another rotation cannot send the same result twice. A saved pending operation without retained memory shows an interrupted-import retry message. No AndroidX, Gradle, service, persistent storage, or permission was added.

Current local evidence: Android 16 / API 36 emulator (`alphabet_phone_api_36`), 17 November 2026. All four existing provider checks passed again. New lifecycle instrumentation holds a pipe open until after a real portrait/landscape Activity recreation. Both a valid ZIP and a corrupt archive complete on the replacement Activity, selection remains disabled during copying, retry becomes enabled afterward, and a second rotation retains the result without a second source read. A further test lets the copy finish while the Activity is backgrounded and confirms the result is handled only after resume. The valid case verifies the accurate missing-Minecraft retry path because Minecraft is absent from the emulator. It does not prove a real Minecraft launch or import.

The test APK alone exports a gated fixture provider. Do not distribute or install the test APK on a personal device; it is intended for a disposable emulator. The production provider and manifest permissions are unchanged.

Portrait and landscape emulator screenshots were inspected; text and controls remained readable. App/test builds, javac type checking, and v2/v3 signature verification passed. Google's current `testing/testing-setup` skill was reviewed on 17 November 2026; existing platform instrumentation is retained under the no-new-dependencies boundary. Other domains (R8, Play, navigation, AGP migration) do not apply. CI builds/signs both APKs; it does not execute instrumentation. No standalone lint command exists.

Still required: post-fix real-device Minecraft handoff and successful import, including rotation during a slow import. Process-kill recovery still needs explicit evidence. October tablet acceptance applies to the old artifact, not this fix. The published v0.1.0 APK, tag and release are unchanged; new local builds use a separate output directory. Rollback: revert the fix or uninstall the helper; originals and worlds remain untouched.

## M1 device handoff — 17 November 2026

PR #2 is now merged. A fresh build of its lifecycle fix and repeat emulator checks accompany the [M1 pack acceptance](../../addons/underground-tech-pack/tests/m1-validation.md). Build into `dist/m1-launcher/` using `LAUNCHER_OUTPUT_DIR` to preserve the historical APK. Real Minecraft import, slow-copy rotation handoff and process-kill recovery remain pending owner testing; the old v0.1.0 prerelease does not verify this fix.
