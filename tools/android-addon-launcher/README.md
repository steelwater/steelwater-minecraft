# Steelwater Add-on Launcher — Android test utility v0.1

Requested by Dan on 8 October 2026 after Android's file browser offered no Minecraft handler for `.mcaddon`. This separate utility picks one file and explicitly opens the installed Google Play Minecraft activity with a readable content URI. It cannot guarantee Minecraft accepts the import; check Minecraft's own notification.

## Install and use

Install `dist/steelwater-addon-launcher-0.1-debug.apk` on Android 8.0 or later. Android may ask you to allow installation from the browser/file manager delivering this APK. This is a locally debug-signed test build, not a Play Store release.

Open **Steelwater Add-on Launcher**, tap **Choose .mcaddon**, and choose your download. Minecraft must be installed and enabled in the same Android profile. The app checks the extension and ZIP readability, copies up to 256 MB, then opens Minecraft directly. Minecraft remains responsible for validating and importing the pack. Choosing a file explicitly authorizes that handoff.

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
```

Tests verify shared byte integrity, display-name/size metadata, write rejection and unknown-path rejection. Android enforces external URI permissions; these in-process tests do not prove the cross-app grant or Minecraft import.

Manual checks: picker opens, cancellation recovers, valid add-on copies and reaches the missing-Minecraft message, invalid extension/archive rejected, portrait/landscape readable. Neither emulator had Minecraft installed during Crew testing. On 9 October 2026 Dan reported that the launcher works well on his tablet and requested Uplink. This is Captain-reported end-to-end acceptance.

Google's `testing/testing-setup` skill was reviewed as required. Native testing and device verification apply, but the handbook's no-unapproved-dependencies constraint takes precedence over installing Hilt, Espresso, Robolectric, screenshot/coverage frameworks for this tiny helper. Platform Instrumentation and manual UI checks are used. No R8/Play/navigation migration applies.

References: https://developer.android.com/training/data-storage/shared/documents-files and https://developer.android.com/training/secure-file-sharing/share-file

Development is isolated on `feature/android-addon-launcher`, based on the unmerged Milestone 0 branch. Uplink was authorized on 9 October 2026. The launcher PR is stacked on the Milestone 0 branch until PR #1 merges; no merge is authorized. The APK is a test handoff, not a canonical release artifact. Dan explicitly authorized the APK upload on 8 October 2026. Uploaded and verified in the project Drive dist folder: https://drive.google.com/file/d/1tpcBV1PPZqpQkZ8JRO8_3M2uC1tHp8HF/view . Rollback: uninstall the helper; add-on source remains unchanged.

## Observed results — 8 October 2026

Android 16 emulator: all four provider assertions passed. An unrelated ADB caller was denied provider access. Manual valid-file selection, missing-Minecraft message, picker cancellation, wrong-extension rejection and corrupt-ZIP rejection passed. Portrait and landscape screenshots were inspected; content and controls were readable. APK signature verification passed (v2/v3). Build script syntax and all new-file whitespace checks passed. No actual Minecraft import, cross-app read by Minecraft, real-tablet check, or remote CI run was performed.

APK SHA-256: `5de5cc1605db8b69e7f0a35d2f40500c4ee0182cfca7fdccda3c99ee4cadfc6d`. This checksum identifies the original Captain-tested APK, preserved for distribution.

## Uplink verification — 9 October 2026

Runtime Java, manifest and resources remain the tested implementation. Only the build output directory option, CI, and documentation were added for Uplink. Local provider/manual evidence from 8 October is retained; no device is connected for a new instrumentation run. CI builds the app and provider-test APKs and checks signatures with an ephemeral debug key; it does not reproduce the local signing identity or replace the Captain-tested attachment. CI does not execute emulator instrumentation. No standalone lint/type checker is configured; javac performs Java type checking. Known Java 8/deprecated inset compiler warnings remain.
