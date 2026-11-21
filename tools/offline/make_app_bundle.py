#!/usr/bin/env python3
"""Build self-contained FreeClipping .app bundles (arm64 / x86_64) for macOS.

The bundle carries everything a user needs: the app source and the whole
Python-3.12 wheelhouse, so the app runs with NO internet — on first launch it
bootstraps a local venv inside itself. No installer step, no shell script:
double-click FreeClipping.app.

Emitted (into dist/):
  FreeClipping-macOS-arm64.app.zip    - contains FreeClipping.app (Apple Silicon)
  FreeClipping-macOS-x64.app.zip      - contains FreeClipping.app (Intel)

Usage:
  python3 tools/offline/make_app_bundle.py --mac-arch arm64
  python3 tools/offline/make_app_bundle.py --mac-arch x64
"""
import argparse
import base64
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import tarfile
import io

ROOT = Path(__file__).resolve().parent.parent.parent
DIST = ROOT / 'dist'
PYTHON_VERSION = '3.12'
PYTHON_ABI = 'cp312'

# Same app payload as the offline installer (the app + icons + model)
APP_FILES = [
    'app.py', 'app.js', 'extras.js', 'transcripts.js', 'vision.js', 'report.js',
    'style.css', 'index.html', 'mobile.html', 'requirements.txt', 'run.ps1', 'run.sh',
    'install.ps1', 'install.sh', 'FREECLIPPING-AGENT-SETUP-PROMPT.txt', 'FreeClipping-Setup.bat',
    'action.py', 'aiparts.py', 'brands.py', 'bundles.py', 'captions.py', 'captions_yt.py',
    'creators.py', 'curation.py', 'encoders.py', 'excite.py', 'facecam_detect.py',
    'highlights.py', 'hooks.py', 'jobs.py', 'languages.py', 'layouts.py', 'learn.py',
    'live_session.py', 'phone.py', 'previews.py', 'reedit.py', 'report.py', 'smart.py',
    'standalone.py', 'styling.py', 'subtitles.py', 'transcripts.py', 'translit.py',
    'vision.py', 'ytdl.py', 'LICENSE', 'README.md',
    'models/face_detection_yunet_2023mar.onnx',
    'icons/app-icon.ico', 'icons/app-icon.icns', 'icons/app-icon-1024.png',
    'icons/app-icon-512.png', 'icons/app-icon-192.png', 'icons/app-icon-180.png',
    'icons/app-icon-32.png', 'icons/app-icon-maskable-512.png',
]

LAUNCHER = '''#!/bin/bash
# FreeClipping launcher - self-contained .app (no installer needed).
set -e
SELF="$(cd "$(dirname "$0")/../.." && pwd)"
RES="$SELF/Contents/Resources"
APP="$RES/app"

for c in python3.12; do command -v "$c" >/dev/null 2>&1 && PY="$c" && break; done
if [ -z "$PY" ]; then
  echo "FreeClipping needs Python 3.12 (https://www.python.org/downloads/ or brew install python@3.12)"
  exit 1
fi

if [ ! -d "$APP/.venv" ]; then
  echo "FreeClipping: first launch - setting up the app environment..."
  mkdir -p "$APP"
  "$PY" -c "import zipfile; zipfile.ZipFile('$RES/app.zip').extractall('$APP')"
  "$PY" -c "import zipfile; zipfile.ZipFile('$RES/wheelhouse.zip').extractall('$RES/wheelhouse')"
  mkdir -p "$RES/wheelhouse"
  "$PY" -m venv "$APP/.venv"
  "$APP/.venv/bin/pip" install --upgrade pip --quiet || true
  "$APP/.venv/bin/pip" install --no-index --find-links "$RES/wheelhouse" -r "$APP/requirements.txt" --quiet
  echo "FreeClipping: setup complete"
fi

PORT="${NEONCLIPPING_PORT:-8770}"
(sleep 4; command -v open >/dev/null 2>&1 && open "http://127.0.0.1:$PORT" || true) &
exec "$APP/.venv/bin/python" "$APP/app.py"
'''

PLIST = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>FreeClipping</string>
  <key>CFBundleDisplayName</key><string>FreeClipping</string>
  <key>CFBundleIdentifier</key><string>io.github.analoggeek.freeclipping</string>
  <key>CFBundleVersion</key><string>1.0.0</string>
  <key>CFBundleShortVersionString</key><string>1.0.0</string>
  <key>CFBundleExecutable</key><string>FreeClipping</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleIconFile</key><string>AppIcon.icns</string>
  <key>CFBundleURLTypes</key>
  <array>
    <dict><key>CFBundleURLName</key><string>io.github.analoggeek.freeclipping</string><key>CFBundleURLSchemes</key><array><string>freeclipping</string></array></dict>
  </array>
  <key>NSHighResolutionCapable</key><true/>
  <key>LSBackgroundOnly</key><false/>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
</dict></plist>
'''


def run(cmd):
    print('  $ ' + ' '.join(str(c) for c in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        raise SystemExit(f'failed: {cmd[0]} (rc={r.returncode})')
    return r


def build_app_zip(tmp):
    print('Building app payload...')
    app_dir = tmp / 'app-flat'
    app_dir.mkdir()
    for rel in APP_FILES:
        src = ROOT / rel
        if not src.exists():
            raise SystemExit(f'missing required file: {src}')
        dst = app_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
    # mirrored icon for the launcher (same name as the wheelhouse images)
    shutil.copy(ROOT / 'icons' / 'app-icon-512.png', app_dir / 'icons' / 'app-icon.png')
    zip_path = tmp / 'app.zip'
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zf:
        for p in sorted(app_dir.rglob('*')):
            if p.is_file():
                zf.write(p, p.relative_to(app_dir))
    print(f'  app payload: {zip_path.stat().st_size / 1e6:.2f} MB')
    return zip_path


def build_wheelhouse_zip(tmp, platform, name):
    print(f'Downloading wheelhouse ({name})...')
    wdir = tmp / f'wheelhouse-{name}'
    wdir.mkdir()
    run([sys.executable, '-m', 'pip', 'download', '--only-binary=:all:',
         '--platform', platform, '--python-version', PYTHON_VERSION,
         '--abi', PYTHON_ABI, '--implementation', 'cp', '--no-cache-dir', '--quiet',
         '-r', str(ROOT / 'requirements.txt'), '-d', str(wdir)])
    wheels = list(wdir.glob('*.whl'))
    if not wheels:
        raise SystemExit('wheelhouse is empty')
    total = sum(w.stat().st_size for w in wheels)
    print(f'  wheelhouse: {len(wheels)} wheels, {total / 1e6:.1f} MB')
    zip_path = tmp / f'wheelhouse.zip'
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zf:
        for w in sorted(wdir.glob('*.whl')):
            zf.write(w, w.name)
    print(f'  wheelhouse zip: {zip_path.stat().st_size / 1e6:.1f} MB')
    return zip_path


def build_bundle(tmp, arch, label):
    print(f'Building .app bundle ({label})...')
    platform = 'macosx_11_0_arm64' if arch == 'arm64' else 'macosx_11_0_x86_64'
    bundle = tmp / 'FreeClipping.app'
    shutil.rmtree(bundle, ignore_errors=True)
    app = bundle / 'Contents'
    contents = app
    (app / 'MacOS').mkdir(parents=True)
    (app / 'Resources').mkdir()

    # icons
    shutil.copy(ROOT / 'icons' / 'app-icon.icns', app / 'Resources' / 'AppIcon.icns')

    # app payload + wheelhouse (embedded)
    shutil.copy(tmp / 'app.zip', app / 'Resources' / 'app.zip')
    shutil.copy(tmp / 'wheelhouse.zip', app / 'Resources' / 'wheelhouse.zip')

    # launcher
    launcher = app / 'MacOS' / 'FreeClipping'
    launcher.write_text(LAUNCHER)
    launcher.chmod(0o755)

    # info.plist
    (app / 'Info.plist').write_text(PLIST)
    return bundle


def pack_bundle_zip(bundle, zip_path):
    print(f'Packing {zip_path.name}...')
    from zipfile import ZipInfo
    import time
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zf:
        for p in sorted(bundle.rglob('*')):
            if p.is_file():
                arc = str(p.relative_to(bundle.parent))
                info = ZipInfo(arc, (time.localtime(p.stat().st_mtime)[:6]))
                mode = 0o644
                try:
                    if p.stat().st_mode & 0o111:
                        mode = 0o755
                except OSError:
                    pass
                info.external_attr = (mode << 16)
                info.create_system = 3
                zf.writestr(info, p.read_bytes())
    print(f'  {zip_path.name}: {zip_path.stat().st_size / 1e6:.1f} MB')


def main():
    ap = argparse.ArgumentParser(description='Build self-contained FreeClipping .app bundles')
    ap.add_argument('--mac-arch', choices=['arm64', 'x64', 'both'], default='arm64',
                    help='arm64 (Apple Silicon), x64 (Intel), or both (default: arm64)')
    args = ap.parse_args()

    DIST.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='freeclipping-bundle-') as td:
        tmp = Path(td)
        build_app_zip(tmp)                       # shared app payload
        archs = ['arm64', 'x64'] if args.mac_arch == 'both' else [args.mac_arch]
        for arch in archs:
            label = 'macOS Apple Silicon (arm64)' if arch == 'arm64' else 'macOS Intel (x86_64)'
            build_wheelhouse_zip(tmp,
                                 'macosx_11_0_arm64' if arch == 'arm64' else 'macosx_11_0_x86_64',
                                 f'macos-{arch}')
            bundle = build_bundle(tmp, arch, label)
            pack_bundle_zip(bundle, DIST / f'FreeClipping-macOS-{arch}.app.zip')


if __name__ == '__main__':
    main()
