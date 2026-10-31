#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
META="$ROOT/meta.xml"
UPSTREAM="$ROOT/upstream-wiimc"
DIST="$ROOT/dist/apps/WiiModernMediaPlayer"
EXPECTED_VERSION="1.7.0"

version="$(sed -n 's:.*<version>\([^<]*\)</version>.*:\1:p' "$META" | head -n1)"
test "$version" = "$EXPECTED_VERSION" || {
    echo "ERROR: expected version $EXPECTED_VERSION, got $version" >&2
    exit 1
}
: "${DEVKITPRO:?ERROR: DEVKITPRO is not set}"
: "${DEVKITPPC:?ERROR: DEVKITPPC is not set}"
test -f "$DEVKITPRO/libogc2/wii_rules" || {
    echo "ERROR: libogc2 Wii rules not found" >&2
    exit 1
}

rm -rf "$UPSTREAM" "$ROOT/dist"
git clone --depth 1 https://github.com/dborth/wiimc.git "$UPSTREAM"
python3 "$ROOT/tools/apply_wiimc_patch.py"

cd "$UPSTREAM"
make -j2
DOL="$UPSTREAM/executables/wiimc.dol"
test -s "$DOL" || {
    echo "ERROR: WiiMC DOL was not produced" >&2
    exit 1
}

# Reject a truncated/empty executable before it reaches the Wii SD card.
python3 - "$DOL" <<'PY'
import os, struct, sys
p = sys.argv[1]
b = open(p, 'rb').read()
if len(b) < 0x100:
    raise SystemExit(f"ERROR: DOL too small: {len(b)} bytes")
pairs = []
for i in range(18):
    off = struct.unpack('>I', b[i*4:i*4+4])[0]
    size = struct.unpack('>I', b[0x90+i*4:0x90+i*4+4])[0]
    if off and size:
        if off + size > len(b):
            raise SystemExit(f"ERROR: invalid DOL section {i}")
        pairs.append((off, size))
if not pairs:
    raise SystemExit("ERROR: DOL has no loadable sections")
print(f"DOL OK: {len(b)} bytes, {len(pairs)} sections")
PY

mkdir -p "$DIST"
cp "$DOL" "$DIST/boot.dol"
cp "$ROOT/meta.xml" "$DIST/meta.xml"
cp "$ROOT/icon.png" "$DIST/icon.png"

test -s "$DIST/boot.dol" && test -s "$DIST/meta.xml" && test -s "$DIST/icon.png"
printf '%s\n' "Built $DIST/boot.dol"
