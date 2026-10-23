#!/bin/sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
EXPECTED_VERSION="1.7.0"
META="$ROOT/meta.xml"
grep -Fq "<version>${EXPECTED_VERSION}</version>" "$META" || { echo "ERROR: expected version ${EXPECTED_VERSION}" >&2; exit 1; }
: "${DEVKITPRO:?ERROR: DEVKITPRO is not set}"
: "${DEVKITPPC:?ERROR: DEVKITPPC is not set}"
LIBOGC2_RULES="$DEVKITPRO/libogc2/wii_rules"
test -f "$LIBOGC2_RULES" || { echo "ERROR: libogc2 Wii rules not found: $LIBOGC2_RULES" >&2; exit 1; }
UPSTREAM="$ROOT/upstream-wiimc"
DIST="$ROOT/dist/apps/WiiModernMediaPlayer"
rm -rf "$UPSTREAM" "$ROOT/dist"
git clone --depth 1 https://github.com/dborth/wiimc.git "$UPSTREAM"
python3 "$ROOT/tools/apply_wiimc_patch.py"
cd "$UPSTREAM"
make
DOL="$UPSTREAM/executables/wiimc.dol"
test -s "$DOL" || { echo "ERROR: expected DOL not found: $DOL" >&2; exit 1; }
mkdir -p "$DIST"
cp "$DOL" "$DIST/boot.dol"
cp "$ROOT/meta.xml" "$DIST/meta.xml"
cp "$ROOT/icon.png" "$DIST/icon.png"
test -s "$DIST/boot.dol" && test -s "$DIST/meta.xml" && test -s "$DIST/icon.png"
printf '%s\n' "Built $DIST/boot.dol"
