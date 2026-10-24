#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
META="$ROOT/meta.xml"
: "${DEVKITPRO:?ERROR: DEVKITPRO is not set}"
: "${DEVKITPPC:?ERROR: DEVKITPPC is not set}"

export PORTLIBS="${PORTLIBS:-$DEVKITPRO/portlibs/ppc}"
export PATH="$DEVKITPPC/bin:$DEVKITPRO/tools/bin:$PORTLIBS/bin:$DEVKITPRO/portlibs/wii/bin:$PATH"

UPSTREAM_URL="https://github.com/SuperrSonic/WiiMC-SSLC.git"
UPSTREAM_TAG="v3.0.0-2024"
UPSTREAM="$ROOT/upstream-wiimc"
DIST="$ROOT/dist/apps/WiiModernMediaPlayer"

PROJECT_VERSION="$(sed -n 's:.*<version>\([^<]*\)</version>.*:\1:p' "$META" | head -n 1)"
test -n "$PROJECT_VERSION" || { echo "ERROR: project version missing from meta.xml" >&2; exit 1; }

rm -rf "$UPSTREAM" "$ROOT/dist"
git clone --depth 1 --branch "$UPSTREAM_TAG" "$UPSTREAM_URL" "$UPSTREAM"
python3 "$ROOT/tools/apply_wiimc_patch.py"
find "$UPSTREAM/source/mplayer" -type f -name '*.d' -delete
cd "$UPSTREAM"

python3 - <<'PY'
from pathlib import Path

root = Path('.')
makefile = root / 'Makefile'
s = makefile.read_text(encoding='utf-8')
s2 = s.replace('ENABLE_NTFS                   = 1', 'ENABLE_NTFS                   = 0')
s2 = s2.replace('ENABLE_EXT2                   = 1', 'ENABLE_EXT2                   = 0')
if s2 == s:
    raise SystemExit('ERROR: optional filesystem anchors not found in upstream Makefile')
makefile.write_text(s2, encoding='utf-8')

for p in (root / 'source' / 'mplayer' / 'config.mak', root / 'source' / 'mplayer' / 'Makefile'):
    if p.exists():
        t = p.read_text(encoding='utf-8')
        t2 = t.replace('-mpaired', '').replace('-mstring', '')
        if t2 != t:
            p.write_text(t2, encoding='utf-8')

mplayer = root / 'source' / 'mplayer' / 'mplayer.c'
t = mplayer.read_text(encoding='utf-8')
t2 = t.replace('char fileplaying[MAXPATHLEN];', '#ifndef MAXPATHLEN\n#define MAXPATHLEN 1024\n#endif\n\nchar fileplaying[MAXPATHLEN];')
t2 = t2.replace('stream_error(mpctx->stream)', 'mpctx->stream->error')
loop_anchor = '''void wiiSetLoopOn()\n{\n\tif(mpctx->sh_video)'''
loop_replacement = '''void wiiSetLoopOn()\n{\n\tif(filename && strncmp(filename, "dvd", 3) == 0)\n\t{\n\t\tm_config_set_option(mconfig, "loop", "-1");\n\t\treturn;\n\t}\n\tif(mpctx->sh_video)'''
t2 = t2.replace(loop_anchor, loop_replacement, 1)
if t2 == t:
    raise SystemExit('ERROR: mplayer.c compatibility anchors not found')
mplayer.write_text(t2, encoding='utf-8')

fileop = root / 'source' / 'fileop.cpp'
t = fileop.read_text(encoding='utf-8')
t2 = t.replace('strstr(path, "../") > 0', 'strstr(path, "../") != NULL')
t2 = t2.replace('stricmp(', 'strcasecmp(')
if t2 == t:
    raise SystemExit('ERROR: fileop.cpp compatibility anchors not found')
fileop.write_text(t2, encoding='utf-8')

for p in (root / 'source' / 'fileop.cpp', root / 'source' / 'filebrowser.cpp'):
    t = p.read_text(encoding='utf-8')
    if '#include <strings.h>' not in t:
        t = t.replace('#include <string.h>', '#include <string.h>\n#include <strings.h>', 1)
        p.write_text(t, encoding='utf-8')

settings = root / 'source' / 'settings.h'
t = settings.read_text(encoding='utf-8')
if '#ifndef MAXPATHLEN' not in t:
    t = '#ifndef MAXPATHLEN\n#define MAXPATHLEN 1024\n#endif\n\n' + t
    settings.write_text(t, encoding='utf-8')

input_cpp = root / 'source' / 'input.cpp'
t = input_cpp.read_text(encoding='utf-8')
t2 = t.replace('static u64 prev[4];', 'static u64 rumblePrev[4];')
t2 = t2.replace('prev[i]', 'rumblePrev[i]')
if t2 == t:
    raise SystemExit('ERROR: input.cpp rumble array anchor not found')
input_cpp.write_text(t2, encoding='utf-8')

ave = root / 'source' / 'mplayer' / 'osdep' / 'ave-rvl.c'
t = ave.read_text(encoding='utf-8')
if '#include <string.h>' not in t:
    t = t.replace('#include <gccore.h>', '#include <gccore.h>\n#include <string.h>', 1)
if '#include <ogc/lwp_watchdog.h>' not in t:
    t = t.replace('#include <gccore.h>', '#include <gccore.h>\n#include <ogc/lwp_watchdog.h>', 1)
ave.write_text(t, encoding='utf-8')

gx = root / 'source' / 'mplayer' / 'osdep' / 'gx_supp.c'
t = gx.read_text(encoding='utf-8')
t2 = t.replace('extern timerFadeBlack;', 'static int timerFadeBlack = 0;')
if 'extern void wiiPause();' not in t2:
    t2 = t2.replace('int DrawMPlayerGui();', 'int DrawMPlayerGui();\nextern void wiiPause();', 1)
if t2 == t:
    raise SystemExit('ERROR: gx_supp.c compatibility anchor not found')
gx.write_text(t2, encoding='utf-8')

music = root / 'source' / 'musicplaylist.cpp'
t = music.read_text(encoding='utf-8')
t2 = t.replace('stricmp(', 'strcasecmp(')
if '#include <strings.h>' not in t2:
    t2 = t2.replace('#include <string.h>', '#include <string.h>\n#include <strings.h>', 1)
if t2 == t:
    raise SystemExit('ERROR: musicplaylist.cpp stricmp anchor not found')
music.write_text(t2, encoding='utf-8')

mpmsg = root / 'source' / 'mplayer' / 'mp_msg.c'
t = mpmsg.read_text(encoding='utf-8')
t2 = t.replace('iconv(inv_msgiconv, &filename, &filename_len,', 'iconv(inv_msgiconv, (char **)&filename, &filename_len,')
if t2 == t:
    raise SystemExit('ERROR: mp_msg.c iconv anchor not found')
mpmsg.write_text(t2, encoding='utf-8')

settings_cpp = root / 'source' / 'settings.cpp'
t = settings_cpp.read_text(encoding='latin-1')
t2 = t.replace('node->value.element.name', 'mxmlGetElement(node)')
if t2 == t:
    raise SystemExit('ERROR: settings.cpp mxml anchor not found')
settings_cpp.write_text(t2, encoding='latin-1')
PY

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
DOL="$UPSTREAM/wiimc.dol"
test -s "$DOL" || { echo "ERROR: expected DOL not found: $DOL" >&2; find "$UPSTREAM" -maxdepth 3 -name '*.dol' -print >&2; exit 1; }
mkdir -p "$DIST"
cp "$DOL" "$DIST/boot.dol"
cp "$META" "$DIST/meta.xml"
cp "$ROOT/icon.png" "$DIST/icon.png"
test -s "$DIST/boot.dol" && test -s "$DIST/meta.xml" && test -s "$DIST/icon.png"
printf '%s\n' "Built $DIST/boot.dol (version $PROJECT_VERSION, upstream $UPSTREAM_TAG)"
