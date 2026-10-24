#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
META="$ROOT/meta.xml"
: "${DEVKITPRO:?ERROR: DEVKITPRO is not set}"
: "${DEVKITPPC:?ERROR: DEVKITPPC is not set}"

# The upstream Makefile uses PORTLIBS to locate FreeType and other portlibs.
# libogc2 containers do not always export this legacy variable automatically.
export PORTLIBS="${PORTLIBS:-$DEVKITPRO/portlibs/ppc}"
export PATH="$DEVKITPPC/bin:$DEVKITPRO/tools/bin:$PORTLIBS/bin:$DEVKITPRO/portlibs/wii/bin:$PATH"

# Build against the maintained WiiMC-SS fork, pinned to the release used for
# playback-quality improvements. Do not silently fall back to the older dborth tree.
UPSTREAM_URL="https://github.com/SuperrSonic/WiiMC-SSLC.git"
UPSTREAM_TAG="v3.0.0-2024"
UPSTREAM="$ROOT/upstream-wiimc"
DIST="$ROOT/dist/apps/WiiModernMediaPlayer"

PROJECT_VERSION="$(sed -n 's:.*<version>\([^<]*\)</version>.*:\1:p' "$META" | head -n 1)"
test -n "$PROJECT_VERSION" || { echo "ERROR: project version missing from meta.xml" >&2; exit 1; }

rm -rf "$UPSTREAM" "$ROOT/dist"
git clone --depth 1 --branch "$UPSTREAM_TAG" "$UPSTREAM_URL" "$UPSTREAM"
python3 "$ROOT/tools/apply_wiimc_patch.py"

cd "$UPSTREAM"
make PORTLIBS="$PORTLIBS" -j2

# WiiMC-SS's Makefile emits wiimc.dol at the repository root.
DOL="$UPSTREAM/wiimc.dol"
test -s "$DOL" || { echo "ERROR: expected DOL not found: $DOL" >&2; find "$UPSTREAM" -maxdepth 3 -name '*.dol' -print >&2; exit 1; }

mkdir -p "$DIST"
cp "$DOL" "$DIST/boot.dol"
cp "$META" "$DIST/meta.xml"
cp "$ROOT/icon.png" "$DIST/icon.png"
test -s "$DIST/boot.dol" && test -s "$DIST/meta.xml" && test -s "$DIST/icon.png"
printf '%s\n' "Built $DIST/boot.dol (version $PROJECT_VERSION, upstream $UPSTREAM_TAG)"
