#!/usr/bin/env python3
"""Build FreeClipping's OFFLINE installers (macOS + Windows, wheels pinned to Python 3.12).

Emits (into dist/):
  FreeClipping-Offline-Setup-macOS-arm64.sh      - self-extracting macOS Apple Silicon installer
  FreeClipping-Offline-Setup-macOS-x64.sh        - self-extracting macOS Intel (x86_64) installer
  FreeClipping-Offline-Setup-Windows-x64.ps1     - Windows 64-bit engine (base64-embedded payload)
  FreeClipping-Offline-Setup-Windows-x64.bat     - Windows one-click wrapper (double-click this)

Plus the same payloads as zip files (with +x preserved for the .sh):
  FreeClipping-Offline-macOS-arm64.zip           - contains the .sh
  FreeClipping-Offline-macOS-x64.zip             - contains the .sh
  FreeClipping-Offline-Windows-x64.zip           - contains the .bat + .ps1

Payloads embed the app source, icons and every dependency as binary wheels - NO network needed.

Usage:
  python3 tools/offline/make_offline_installer.py
  python3 tools/offline/make_offline_installer.py --skip-mac
  python3 tools/offline/make_offline_installer.py --skip-windows

The target machines still need Python 3.12 installed (the installer installs NOTHING system-wide).
"""
import argparse
import base64
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent.parent
DIST = ROOT / 'dist'
PYTHON_VERSION = '3.12'
PYTHON_ABI = 'cp312'

APP_FILES = [
    'app.py', 'app.js', 'extras.js', 'transcripts.js', 'vision.js', 'report.js',
    'style.css', 'app/index.html', 'mobile.html', 'requirements.txt', 'run.ps1', 'run.sh',
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

MARKER = 'FREECLIPPINGPAYLOADMARKER'

def run(cmd):
    print('  $ ' + ' '.join(str(c) for c in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        raise SystemExit(f'failed: {cmd[0]} (rc={r.returncode})')
    return r

def build_app_zip(tmp):
    print('Building app payload...')
    app_dir = tmp / 'app'
    app_dir.mkdir()
    for rel in APP_FILES:
        src = ROOT / rel
        if not src.exists():
            raise SystemExit(f'missing required file: {src}')
        dst = app_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
    # mirrored icon for the shortcut/launcher (same as the wheelhouse images)
    dst = app_dir / 'icons' / 'app-icon.png'
    shutil.copy(ROOT / 'icons' / 'app-icon-512.png', dst)
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
    zip_path = tmp / f'wheelhouse-{name}.zip'
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zf:
        for w in sorted(wdir.glob('*.whl')):
            zf.write(w, w.name)
    return zip_path

def build_payload_tar(tmp, app_zip, wheelhouse_zip):
    import tarfile
    payload = tmp / 'payload.tar.gz'
    with tarfile.open(payload, 'w:gz') as tf:
        tf.add(app_zip, 'app.zip')
        tf.add(wheelhouse_zip, 'wheelhouse.zip')
    print(f'  payload: {payload.stat().st_size / 1e6:.1f} MB (~{payload.stat().st_size / 1e6 * 1.34:.0f} MB as base64)')
    return payload

# ---------------- macOS .sh ----------------
MAC_SH_TEMPLATE = r'''#!/usr/bin/env bash
# FreeClipping OFFLINE installer for __MAC_ARCH_LABEL__ - self-contained.
# Built by tools/offline/make_offline_installer.py - no internet needed.
set -euo pipefail

PAYLOAD="$(mktemp /tmp/freeclipping-offline.XXXXXX.tar.gz)"
PAYLOAD_B64="$(mktemp /tmp/freeclipping-payload.XXXXXX.b64)"
cat > "$PAYLOAD_B64" <<'FREEeCLIPPING-PAYLOAD-MARKER'
__PAYLOAD_B64__
FREEeCLIPPING-PAYLOAD-MARKER
base64 -d "$PAYLOAD_B64" > "$PAYLOAD"
rm -f "$PAYLOAD_B64"

WORK="$(mktemp -d /tmp/freeclipping-offline-XXXXXX)"
tar -xzf "$PAYLOAD" -C "$WORK"
APP_DIR="$HOME/FreeClipping/app"
WHEELHOUSE="$WORK/wheelhouse"
mkdir -p "$APP_DIR" "$WHEELHOUSE"

# Python 3.12 check
PY=""
for c in python3.12; do command -v "$c" >/dev/null 2>&1 && PY="$c" && break; done
if [ -z "$PY" ]; then
  echo "  Python 3.12 required (bundled wheels are for 3.12)."
  echo "  Install it (brew install python@3.12) and run this again."
  exit 1
fi
echo ""
echo "  FreeClipping (offline macOS) - installing to $APP_DIR"
echo "  $($PY --version)"

"$PY" -c "import zipfile; zipfile.ZipFile('$WORK/app.zip').extractall('$APP_DIR')"
"$PY" -c "import zipfile; zipfile.ZipFile('$WORK/wheelhouse.zip').extractall('$WHEELHOUSE')"

"$PY" -c "import venv" 2>/dev/null || { echo "  Missing the venv module."; exit 1; }
[ -d "$APP_DIR/.venv" ] || "$PY" -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip --quiet || true
"$APP_DIR/.venv/bin/pip" install --no-index --find-links "$WHEELHOUSE" -r "$APP_DIR/requirements.txt" --quiet
"$APP_DIR/.venv/bin/python" -c "import fastapi, uvicorn, yt_dlp, numpy, cv2, faster_whisper, PIL; print('  imports ok')"

# start script (based on run.sh)
cat > "$HOME/FreeClipping/start.sh" <<'EOF'
#!/usr/bin/env bash
cd "$HOME/FreeClipping/app"
PORT="\${NEONCLIPPING_PORT:-8770}"
(sleep 4; command -v open >/dev/null 2>&1 && open "http://127.0.0.1:\$PORT" || true) &
exec .venv/bin/python app.py
EOF
chmod +x "$HOME/FreeClipping/start.sh"

# .app bundle with 3D icon (Finder/Dock app style)
BUNDLE="$HOME/Applications/FreeClipping.app"
mkdir -p "$BUNDLE/Contents/MacOS" "$BUNDLE/Contents/Resources"
cp "$APP_DIR/icons/app-icon.icns" "$BUNDLE/Contents/Resources/AppIcon.icns"
cat > "$BUNDLE/Contents/MacOS/FreeClipping" <<'EOF2'
#!/usr/bin/env bash
cd "$HOME/FreeClipping/app"
PORT="\${NEONCLIPPING_PORT:-8770}"
(sleep 4; command -v open >/dev/null 2>&1 && open "http://127.0.0.1:\$PORT" || true) &
exec .venv/bin/python app.py
EOF2
chmod +x "$BUNDLE/Contents/MacOS/FreeClipping"
cat > "$BUNDLE/Contents/Info.plist" <<'EOF3'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>FreeClipping</string>
  <key>CFBundleDisplayName</key><string>FreeClipping</string>
  <key>CFBundleIdentifier</key><string>io.github.analoggeek.freeclipping</string>
  <key>CFBundleVersion</key><string>2.0.0</string>
  <key>CFBundleShortVersionString</key><string>2.0.0</string>
  <key>CFBundleExecutable</key><string>FreeClipping</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleIconFile</key><string>AppIcon.icns</string>
  <key>NSHighResolutionCapable</key><true/>
</dict></plist>
EOF3

rm -rf "$WORK" "$PAYLOAD"

echo ""
echo "  INSTALL COMPLETE."
echo "  Next time:  ~/Applications/FreeClipping.app  (or $HOME/FreeClipping/start.sh)"
echo "  The app opens at http://127.0.0.1:8770  - 3D icon installed"
echo "  Uninstall: delete ~/FreeClipping and ~/Applications/FreeClipping.app"
echo ""
'''

# ---------------- Windows .bat + .ps1 ----------------
WIN_BAT_TEMPLATE = '''@echo off
setlocal
title FreeClipping Offline Setup
echo.
echo   FreeClipping OFFLINE setup shuru ho raha hai...
echo   (ab offline: app aur packages embedded hain, internet nahi chaahiye)
echo.
set "PS=%~dp0FreeClipping-Offline-Setup-Windows-x64.ps1"
if not exist "%PS%" (
  echo   Error: engine file nahi mila: %PS%
  echo   Setup se dono files (.bat + .ps1) saath mein rakhein.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS%"
pause
'''

WIN_PS1_TEMPLATE = '''# FreeClipping offline installer for Windows 64-bit (Python 3.12 wheels embedded)
# Built by tools/offline/make_offline_installer.py - no internet needed.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

$InstallDir = $env:LOCALAPPDATA
$InstallDir = Join-Path $InstallDir 'FreeClipping'

Write-Host ""
Write-Host "  FreeClipping (offline) - Windows installer" -ForegroundColor Cyan
Write-Host "  Install folder: $InstallDir"

# ---- extract embedded payload ----
$raw = Get-Content -Raw -Path $PSCommandPath
# payload marker: the engine text contains the marker, the APPENDED tail holds the real one.
# Always use the LAST occurrence so the search string inside the engine is never matched.
$markerIndex = $raw.LastIndexOf('freclippingpayloadmarker')
if ($markerIndex -lt 0) { throw "Installer is damaged (missing payload)." }
$nl = $raw.IndexOf("`n", $markerIndex)
if ($nl -lt 0) { throw "Installer is damaged (bad payload marker)." }
$after = $raw.Substring($nl + 1)
$payload = $after -replace '[^A-Za-z0-9+/=]', ''
$bytes = [Convert]::FromBase64String($payload)
$tmp = Join-Path $env:TEMP ("freeclipping-offline-" + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$payloadTar = Join-Path $tmp "payload.tar.gz"
[System.IO.File]::WriteAllBytes($payloadTar, $bytes)
tar -xzf "$payloadTar" -C "$tmp"
$appSrc = Join-Path $tmp "app"
$wheelhouse = Join-Path $tmp "wheelhouse"
New-Item -ItemType Directory -Force -Path $appSrc, $wheelhouse | Out-Null
Expand-Archive -Path (Join-Path $tmp "app.zip") -DestinationPath $appSrc -Force
Expand-Archive -Path (Join-Path $tmp "wheelhouse.zip") -DestinationPath $wheelhouse -Force

# ---- Python 3.12 check ----
$py = $null
foreach ($c in @("python3.12", "py")) {
    if (Get-Command $c -ErrorAction SilentlyContinue) {
        try {
            $v = & $c -c "import sys;print('%d.%d' % sys.version_info[:2])" 2>$null
            if ($v -eq '3.12') { $py = $c; break }
        } catch {}
    }
}
if (-not $py) {
    Write-Host "  Python 3.12 is required (wheels bundled are for 3.12)."
    Write-Host "  Install it from python.org and run this file again."
    exit 1
}

$app = Join-Path $InstallDir "app"
New-Item -ItemType Directory -Force -Path $app | Out-Null
Copy-Item -Path (Join-Path $appSrc "*") -Destination $app -Recurse -Force
$venvPy = Join-Path $app ".venv\\Scripts\\python.exe"
if (-not (Test-Path $venvPy)) { & $py -m venv (Join-Path $app ".venv"); if ($LASTEXITCODE -ne 0) { throw "Virtual environment nahi bana." } }
& $venvPy -m pip install --upgrade pip --quiet 2>$null
Write-Host "  Installing packages from the embedded wheelhouse..."
& $venvPy -m pip install --no-index --find-links $wheelhouse -r (Join-Path $app "requirements.txt") --quiet
if ($LASTEXITCODE -ne 0) { throw "Offline packages install fail hue." }
& $venvPy -c "import fastapi, uvicorn, yt_dlp, numpy, cv2, faster_whisper, PIL; print('  imports ok')"

# ---- icons + start script + 3D-iconed shortcut ----
$iconIco = Join-Path $app "icons\\app-icon.ico"
$startBat = Join-Path $InstallDir "Start-FreeClipping.bat"
$bat = @(
    '@echo off',
    'title FreeClipping (band karne ke liye ye window band karo)',
    'if not defined NEONCLIPPING_PORT set NEONCLIPPING_PORT=8770',
    "cd /d `"$app`"",
    'start "" /min powershell -NoProfile -WindowStyle Hidden -Command "for($i=0;$i -lt 90;$i++){try{Invoke-WebRequest -UseBasicParsing http://127.0.0.1:$env:NEONCLIPPING_PORT/healthz -TimeoutSec 2 | Out-Null; Start-Process http://127.0.0.1:$env:NEONCLIPPING_PORT; break}catch{Start-Sleep 1}}"',
    "`"$venvPy`" app.py"
)
Set-Content -Path $startBat -Value $bat -Encoding ASCII

$desktop = [Environment]::GetFolderPath('Desktop')
$sh = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desktop "FreeClipping.lnk"))
$sh.TargetPath = $startBat
$sh.WorkingDirectory = $InstallDir
$sh.Description = "FreeClipping - captioned 9:16 clips"
if (Test-Path $iconIco) { $sh.IconLocation = "$iconIco,0" }
$sh.Save()

Write-Host ""
Write-Host "  INSTALL COMPLETE." -ForegroundColor Green
Write-Host "  Next time: Desktop pe 'FreeClipping' (3D icon - app-icon.ico ke saath)"
Write-Host "  The app opens at http://127.0.0.1:8770"
Write-Host "  Uninstall: delete $InstallDir, aur Desktop shortcuts hatayein."
Write-Host ""

Start-Process -FilePath $startBat -WindowStyle Minimized
Start-Sleep -Seconds 3
Write-Host "  Cleaning up..."
Remove-Item -Path $tmp -Recurse -Force
'''

def write_installer(tmp, out_name, is_mac, mac_arch=None):
    payload = build_payload_tar(tmp, tmp / 'app.zip', tmp / 'wheelhouse.zip')
    b64 = base64.b64encode(payload.read_bytes()).decode('ascii')
    if is_mac:
        template = (MAC_SH_TEMPLATE.replace('__PAYLOAD_B64__', b64, 1)
                    .replace('__MAC_ARCH_LABEL__', mac_arch or 'macOS', 1))
        out_path = out_name
        out_path.write_text(template)
        out_path.chmod(0o755)
        print(f'  {out_path.name}: {out_path.stat().st_size / 1e6:.1f} MB')
    else:
        # append one clean marker line + raw base64 as the tail of the .ps1
        tail = '\nfreclippingpayloadmarker\n' + b64 + '\n'
        # strip trailing blank/newlines from template so the tail is exactly one clean region
        body = WIN_PS1_TEMPLATE.rstrip() + tail
        out_path = out_name
        out_path.write_text(body)
        print(f'  {out_path.name}: {out_path.stat().st_size / 1e6:.1f} MB')

def zip_installer(files, zip_path, mac_mode=None):
    """Zip the installer payloads. mac .sh files keep their +x bit in the zip."""
    from zipfile import ZipFile, ZipInfo
    import time
    zi = ZipFile(zip_path, 'w')
    if mac_mode is not None:
        for f in files:
            fi = f.stat()
            info = ZipInfo(f.name, (time.localtime(fi.st_mtime)[:6]))
            info.external_attr = (0o755 << 16) if mac_mode else 0
            info.create_system = 3
            zi.writestr(info, f.read_bytes())
    else:
        for f in files:
            zi.write(f, f.name)
    zi.close()
    print(f'  {zip_path.name}: {zip_path.stat().st_size / 1e6:.1f} MB')

def main():
    ap = argparse.ArgumentParser(description='Build FreeClipping offline installers')
    ap.add_argument('--skip-mac', action='store_true')
    ap.add_argument('--skip-mac-x64', action='store_true')
    ap.add_argument('--skip-windows', action='store_true')
    args = ap.parse_args()
    DIST.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='freeclipping-offline-') as td:
        tmp = Path(td)
        build_app_zip(tmp)

        if not args.skip_mac:
            mac_sh = []
            # Apple Silicon (arm64)
            build_wheelhouse_zip(tmp, 'macosx_11_0_arm64', 'macos-arm64')
            shutil.copy(tmp / 'wheelhouse-macos-arm64.zip', tmp / 'wheelhouse.zip')
            arc = DIST / 'FreeClipping-Offline-Setup-macOS-arm64.sh'
            write_installer(tmp, arc, True, 'macOS Apple Silicon')
            mac_sh.append((arc, 'FreeClipping-Offline-macOS-arm64.zip'))
            # Intel (x86_64)
            if not args.skip_mac_x64:
                build_wheelhouse_zip(tmp, 'macosx_11_0_x86_64', 'macos-x64')
                shutil.copy(tmp / 'wheelhouse-macos-x64.zip', tmp / 'wheelhouse.zip')
                x64_arc = DIST / 'FreeClipping-Offline-Setup-macOS-x64.sh'
                write_installer(tmp, x64_arc, True, 'macOS Intel (x86_64)')
                mac_sh.append((x64_arc, 'FreeClipping-Offline-macOS-x64.zip'))
            for sh, zip_name in mac_sh:
                zip_installer([sh], DIST / zip_name, mac_mode=True)
        if not args.skip_windows:
            build_wheelhouse_zip(tmp, 'win_amd64', 'windows-x64')
            shutil.copy(tmp / 'wheelhouse-windows-x64.zip', tmp / 'wheelhouse.zip')
            write_installer(tmp, DIST / 'FreeClipping-Offline-Setup-Windows-x64.ps1', False)
            WIN_BAT_PATH = DIST / 'FreeClipping-Offline-Setup-Windows-x64.bat'
            WIN_BAT_PATH.write_text(WIN_BAT_TEMPLATE)
            print(f'  {WIN_BAT_PATH.name}: {WIN_BAT_PATH.stat().st_size / 1e6:.1f} MB')
            zip_installer([WIN_BAT_PATH, DIST / 'FreeClipping-Offline-Setup-Windows-x64.ps1'],
                          DIST / 'FreeClipping-Offline-Windows-x64.zip')

if __name__ == '__main__':
    main()
