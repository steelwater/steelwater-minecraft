#!/usr/bin/env python3
"""Build a locally debug-signed test APK with an existing Android SDK and JDK."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import zipfile

project = Path(__file__).resolve().parent
root = project.parents[1]
sdk = Path(os.environ.get('ANDROID_HOME', Path.home() / 'Library/Android/sdk'))
jdk = Path(os.environ.get('JAVA_HOME', '/Applications/Android Studio.app/Contents/jbr/Contents/Home'))
tools = sdk / 'build-tools/35.0.0'
android = sdk / 'platforms/android-35/android.jar'
testing = '--test' in sys.argv
source = project / 'tests' if testing else project
distribution = Path(os.environ.get('LAUNCHER_OUTPUT_DIR', root / 'dist'))
output = distribution / ('android-addon-launcher-tests' if testing else 'android-addon-launcher')
output.mkdir(parents=True, exist_ok=True)
classes = output / 'classes'
classes.mkdir(exist_ok=True)
dex = output / 'dex'
dex.mkdir(exist_ok=True)
env = dict(os.environ, JAVA_HOME=str(jdk), PATH=str(jdk / 'bin') + os.pathsep + os.environ['PATH'])
def run(*args):
    subprocess.run([str(a) for a in args], check=True, env=env)
run(tools / 'aapt2', 'compile', '--dir', project / 'res', '-o', output / 'resources.zip')
run(tools / 'aapt2', 'link', '-o', output / 'unsigned.apk', '--manifest', source / 'AndroidManifest.xml',
    '-I', android, output / 'resources.zip')
run(jdk / 'bin/javac', '--release', '8', '-Xlint:deprecation', '-classpath', android,
    '-d', classes, *sorted((source / 'src').rglob('*.java')))
run(tools / 'd8', '--lib', android, '--min-api', '26', '--output', dex, *sorted(classes.rglob('*.class')))
with zipfile.ZipFile(output / 'unsigned.apk', 'a', zipfile.ZIP_DEFLATED) as apk:
    apk.write(dex / 'classes.dex', 'classes.dex')
run(tools / 'zipalign', '-f', '4', output / 'unsigned.apk', output / 'aligned.apk')
keystore = Path(os.environ.get('ANDROID_DEBUG_KEYSTORE', Path.home() / '.android/debug.keystore'))
if not keystore.is_file():
    raise SystemExit('An existing Android debug keystore is required. No release signing key is created.')
result = distribution / ('steelwater-addon-launcher-tests.apk' if testing else 'steelwater-addon-launcher-0.1-debug.apk')
run(tools / 'apksigner', 'sign', '--ks', keystore, '--ks-key-alias', 'androiddebugkey',
    '--ks-pass', 'pass:android', '--key-pass', 'pass:android', '--out', result, output / 'aligned.apk')
run(tools / 'apksigner', 'verify', '--verbose', result)
checksum = hashlib.sha256(result.read_bytes()).hexdigest()
result.with_suffix('.apk.sha256').write_text(f'{checksum}  {result.name}\n')
print(result)
print(checksum)
