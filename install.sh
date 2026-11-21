#!/usr/bin/env bash
# DigiRG Cloud installer for macOS and Linux.
# Needs: python3 (3.10+), ffmpeg, curl, unzip.
# Everything goes into ~/DigiRGCloud. Delete that folder to uninstall.
set -e
DIR="${DIGIRGCLOUD_DIR:-$HOME/DigiRGCloud}"
ZIP="${DIGIRGCLOUD_ZIP:-https://github.com/DIGIRGCLOUD/DIGIRGCLIPPINGFREE/archive/refs/heads/main.zip}"
say() { printf '\n==> %s\n' "$1"; }
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing: $1. $2"; MISSING=1; }; }

say "Step 1/4 - Checking your computer"
MISSING=0
need python3 "Install Python 3.10+ (macOS: brew install python; Ubuntu: sudo apt install python3 python3-venv python3-pip)"
need ffmpeg "Install FFmpeg (macOS: brew install ffmpeg; Ubuntu: sudo apt install ffmpeg)"
need curl "Install curl"
need unzip "Install unzip (Ubuntu: sudo apt install unzip)"
[ "$MISSING" = "1" ] && { echo; echo "Install the missing tools above, then run this again."; exit 1; }

PY=""
for c in python3.12 python3.11 python3.13 python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if (3, 10) <= sys.version_info[:2] <= (3, 13) else 1)' 2>/dev/null; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "Your Python is $(python3 --version 2>&1). DigiRG Cloud needs Python 3.10 to 3.13."
  echo "Install one:  macOS: brew install python@3.12     Ubuntu: sudo apt install python3.12 python3.12-venv"
  echo "Then run this installer again."
  exit 1
fi
"$PY" -c "import venv" 2>/dev/null || { echo "Missing the venv module (Ubuntu: sudo apt install python3-venv)."; exit 1; }
echo "OK: $($PY --version), $(ffmpeg -version | head -1 | cut -c1-30)"

say "Step 2/4 - Downloading DigiRG Cloud"
TMP="$(mktemp -d)"
curl -fsSL "$ZIP" -o "$TMP/nc.zip"
unzip -q "$TMP/nc.zip" -d "$TMP"
mkdir -p "$DIR/app"
cp -R "$TMP"/*/. "$DIR/app/"
rm -rf "$TMP"

say "Step 3/4 - Installing packages"
cd "$DIR/app"
[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install -r requirements.txt --quiet
.venv/bin/python -c "import fastapi, uvicorn, yt_dlp, numpy, cv2, faster_whisper, PIL; print('imports ok')"

say "Step 4/4 - Start script"
cat > "$DIR/start.sh" <<EOF
#!/usr/bin/env bash
cd "$DIR/app"
PORT="\${PORT:-8770}"
(sleep 4; (command -v open >/dev/null && open "http://127.0.0.1:\$PORT") || (command -v xdg-open >/dev/null && xdg-open "http://127.0.0.1:\$PORT") || true) &
exec .venv/bin/python app.py
EOF
chmod +x "$DIR/start.sh"

echo
echo "SETUP COMPLETE."
echo "Start DigiRG Cloud:  $DIR/start.sh    (then open http://127.0.0.1:8770)"
echo "Use: 1) paste a video link  2) press 'Make clips'  3) preview and 'Download MP4'."
[ "${NO_START:-0}" = "1" ] && exit 0
echo "Starting now..."
exec "$DIR/start.sh"
