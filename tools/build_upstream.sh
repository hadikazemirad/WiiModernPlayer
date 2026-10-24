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

# WiiMC-SS ships an old generated dependency file which GNU make on the current
# toolchain parses as a malformed rule. Dependency files are regenerated during
# compilation, so remove only those generated *.d files before building.
find "$UPSTREAM/source/mplayer" -type f -name '*.d' -delete

cd "$UPSTREAM"

# The libogc2 toolchain is newer than the legacy WiiMC-SS build environment.
# The old project enables optional NTFS/EXT2 libraries and PowerPC flags that
# are not present/accepted by the current container. Keep FAT/SD/USB/DVD support
# while disabling only those legacy optional pieces.
python3 - <<'PY'
from pathlib import Path

root = Path('.')
makefile = root / 'Makefile'
s = makefile.read_text(encoding='utf-8')
s2 = s.replace('ENABLE_NTFS                   = 1', 'ENABLE_NTFS                   = 0')
if s2 == s:
    raise SystemExit('ERROR: ENABLE_NTFS anchor not found in upstream Makefile')
makefile.write_text(s2, encoding='utf-8')

# GCC 15-era devkitPPC rejects the obsolete -mpaired option. -mstring is also
# obsolete and only generates a warning, so remove both from the generated
# MPlayer configuration/build files when present.
for p in (root / 'source' / 'mplayer' / 'config.mak', root / 'source' / 'mplayer' / 'Makefile'):
    if p.exists():
        t = p.read_text(encoding='utf-8')
        t2 = t.replace('-mpaired', '').replace('-mstring', '')
        if t2 != t:
            p.write_text(t2, encoding='utf-8')
PY

# libogc2 no longer exposes MAXPATHLEN through WiiMC's legacy include chain.
# Keep the upstream source untouched except for the build-compatible definition.
if ! grep -q '#define MAXPATHLEN 1024' source/filebrowser.h; then
    python3 - <<'PY'
from pathlib import Path
p = Path('source/filebrowser.h')
s = p.read_text(encoding='utf-8')
marker = '#define _FILEBROWSER_H_\n'
if marker not in s:
    raise SystemExit('ERROR: filebrowser.h include guard anchor changed')
if '#ifndef MAXPATHLEN' not in s:
    s = s.replace(marker, marker + '\n#ifndef MAXPATHLEN\n#define MAXPATHLEN 1024\n#endif\n', 1)
p.write_text(s, encoding='utf-8')
PY
fi

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
