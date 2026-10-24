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
root=Path('.')
makefile=root/'Makefile'; s=makefile.read_text(encoding='utf-8'); s2=s.replace('ENABLE_NTFS                   = 1','ENABLE_NTFS                   = 0').replace('ENABLE_EXT2                   = 1','ENABLE_EXT2                   = 0')
if s2==s: raise SystemExit('ERROR: optional filesystem anchors not found')
makefile.write_text(s2,encoding='utf-8')
for p in (root/'source/mplayer/config.mak',root/'source/mplayer/Makefile'):
    if p.exists():
        t=p.read_text(encoding='utf-8'); t2=t.replace('-mpaired','').replace('-mstring','')
        if t2!=t: p.write_text(t2,encoding='utf-8')
mplayer=root/'source/mplayer/mplayer.c'; t=mplayer.read_text(encoding='utf-8'); t2=t.replace('char fileplaying[MAXPATHLEN];','#ifndef MAXPATHLEN\n#define MAXPATHLEN 1024\n#endif\n\nchar fileplaying[MAXPATHLEN];').replace('stream_error(mpctx->stream)','mpctx->stream->error')
t2=t2.replace('''void wiiSetLoopOn()\n{\n\tif(mpctx->sh_video)''','''void wiiSetLoopOn()\n{\n\tif(filename && strncmp(filename, "dvd", 3) == 0)\n\t{\n\t\tm_config_set_option(mconfig, "loop", "-1");\n\t\treturn;\n\t}\n\tif(mpctx->sh_video)''',1)
if t2==t: raise SystemExit('ERROR: mplayer.c anchors not found')
mplayer.write_text(t2,encoding='utf-8')
fileop=root/'source/fileop.cpp'; t=fileop.read_text(encoding='utf-8'); t2=t.replace('strstr(path, "../") > 0','strstr(path, "../") != NULL').replace('stricmp(','strcasecmp(')
if t2==t: raise SystemExit('ERROR: fileop.cpp anchors not found')
fileop.write_text(t2,encoding='utf-8')
for p in (root/'source/fileop.cpp',root/'source/filebrowser.cpp'):
    t=p.read_text(encoding='utf-8')
    if '#include <strings.h>' not in t: p.write_text(t.replace('#include <string.h>','#include <string.h>\n#include <strings.h>',1),encoding='utf-8')
settings=root/'source/settings.h'; t=settings.read_text(encoding='utf-8')
if '#ifndef MAXPATHLEN' not in t: settings.write_text('#ifndef MAXPATHLEN\n#define MAXPATHLEN 1024\n#endif\n\n'+t,encoding='utf-8')
input_cpp=root/'source/input.cpp'; t=input_cpp.read_text(encoding='utf-8'); t2=t.replace('static u64 prev[4];','static u64 rumblePrev[4];').replace('prev[i]','rumblePrev[i]')
if t2==t: raise SystemExit('ERROR: input.cpp anchor not found')
input_cpp.write_text(t2,encoding='utf-8')
ave=root/'source/mplayer/osdep/ave-rvl.c'; t=ave.read_text(encoding='utf-8')
if '#include <string.h>' not in t: t=t.replace('#include <gccore.h>','#include <gccore.h>\n#include <string.h>',1)
if '#include <ogc/lwp_watchdog.h>' not in t: t=t.replace('#include <gccore.h>','#include <gccore.h>\n#include <ogc/lwp_watchdog.h>',1)
ave.write_text(t,encoding='utf-8')
gx=root/'source/mplayer/osdep/gx_supp.c'; t=gx.read_text(encoding='utf-8'); t2=t.replace('extern timerFadeBlack;','static int timerFadeBlack = 0;')
if 'extern void wiiPause();' not in t2: t2=t2.replace('int DrawMPlayerGui();','int DrawMPlayerGui();\nextern void wiiPause();',1)
if t2==t: raise SystemExit('ERROR: gx_supp.c anchor not found')
gx.write_text(t2,encoding='utf-8')
music=root/'source/musicplaylist.cpp'; t=music.read_text(encoding='utf-8'); t2=t.replace('stricmp(','strcasecmp(')
if '#include <strings.h>' not in t2: t2=t2.replace('#include <string.h>','#include <string.h>\n#include <strings.h>',1)
if t2==t: raise SystemExit('ERROR: musicplaylist.cpp anchor not found')
music.write_text(t2,encoding='utf-8')
mpmsg=root/'source/mplayer/mp_msg.c'; t=mpmsg.read_text(encoding='utf-8'); t2=t.replace('iconv(inv_msgiconv, &filename, &filename_len,','iconv(inv_msgiconv, (char **)&filename, &filename_len,')
if t2==t: raise SystemExit('ERROR: mp_msg.c anchor not found')
mpmsg.write_text(t2,encoding='utf-8')
settings_cpp=root/'source/settings.cpp'; t=settings_cpp.read_text(encoding='latin-1'); t2=t.replace('node->value.element.name','mxmlGetElement(node)')
if t2==t: raise SystemExit('ERROR: settings.cpp anchor not found')
settings_cpp.write_text(t2,encoding='latin-1')
wiimc=root/'source/wiimc.cpp'; t=wiimc.read_text(encoding='latin-1'); t2=t.replace('static ssize_t __out_write(struct _reent *r, int fd, const char *ptr, size_t len)','static ssize_t __out_write(struct _reent *r, void *fd, const char *ptr, size_t len)').replace('static void ResetCB()','static void ResetCB(u32 reset_type, void *addr)')
if t2==t: raise SystemExit('ERROR: wiimc.cpp callback anchors not found')
wiimc.write_text(t2,encoding='latin-1')
vf=root/'source/mplayer/libmpcodecs/vf_scale.c'; t=vf.read_text(encoding='utf-8'); t2=t.replace('src2[1]= pal2;','src2[1]= (uint8_t *)pal2;').replace('sws_scale(sws1, src2,','sws_scale(sws1, (const uint8_t *const *)src2,').replace('sws_scale(sws2, src2,','sws_scale(sws2, (const uint8_t *const *)src2,')
if t2==t: raise SystemExit('ERROR: vf_scale anchors not found')
vf.write_text(t2,encoding='utf-8')
film=root/'source/mplayer/libmpdemux/demux_film.c'; t=film.read_text(encoding='utf-8'); t2=t.replace('unsigned short* tmp = dp->buffer;','unsigned short* tmp = (unsigned short*)dp->buffer;')
if t2==t: raise SystemExit('ERROR: demux_film anchor not found')
film.write_text(t2,encoding='utf-8')
gui=root/'source/libwiigui/gui_image.cpp'; t=gui.read_text(encoding='utf-8'); t2=t.replace('static u64 prev;','static u64 imagePrev;').replace('diff_usec(prev, now)','diff_usec(imagePrev, now)').replace('prev = now;','imagePrev = now;')
if t2==t: raise SystemExit('ERROR: gui_image anchor not found')
gui.write_text(t2,encoding='utf-8')
qtx=root/'source/mplayer/loader/qtx/qtxsdk/components.h'; t=qtx.read_text(encoding='utf-8'); t2=t.replace('unsigned int* p=cd->wantedDestinationPixelTypes;','unsigned int* p=(unsigned int*)cd->wantedDestinationPixelTypes;')
if t2==t: raise SystemExit('ERROR: qtx anchor not found')
qtx.write_text(t2,encoding='utf-8')
trigger=root/'source/libwiigui/gui_trigger.cpp'; t=trigger.read_text(encoding='utf-8'); t2=t.replace('static u64 prev[4];','static u64 triggerPrev[4];').replace('prev[chan]','triggerPrev[chan]')
if t2==t: raise SystemExit('ERROR: gui_trigger anchor not found')
trigger.write_text(t2,encoding='utf-8')
# libogc2/newlib devoptab uses opaque void* file handles.
ftp=root/'source/utils/ftp_devoptab.c'; t=ftp.read_text(encoding='utf-8'); t2=t
for old,new in [
('static off_t __ftp_seek(struct _reent *r, int fd,','static off_t __ftp_seek(struct _reent *r, void *fd,'),
('static ssize_t __ftp_read(struct _reent *r, int fd,','static ssize_t __ftp_read(struct _reent *r, void *fd,'),
('static ssize_t __ftp_write(struct _reent *r, int fd,','static ssize_t __ftp_write(struct _reent *r, void *fd,'),
('static int __ftp_close(struct _reent *r, int fd)','static int __ftp_close(struct _reent *r, void *fd)'),
('static int __ftp_fstat(struct _reent *r, int fd,','static int __ftp_fstat(struct _reent *r, void *fd,'),
('st->st_spare1 = 0;','st->st_spare4[0] = 0;'),
('st->st_spare2 = 0;','st->st_spare4[1] = 0;'),
('st->st_spare3 = 0;','st->st_spare4[2] = 0;'),
('if (if_config(myIP, NULL, NULL, true) < 0)','if (if_config(myIP, NULL, NULL, true, 5) < 0)')]:
    t2=t2.replace(old,new)
if t2==t: raise SystemExit('ERROR: ftp_devoptab anchors not found')
ftp.write_text(t2,encoding='utf-8')
# MPlayer's old swscale calls pass a single plane pointer by address.
spu=root/'source/mplayer/sub/spudec.c'; t=spu.read_text(encoding='utf-8'); t2=t.replace('sws_scale(ctx,&s1,','sws_scale(ctx,(const uint8_t *const *)&s1,').replace('sws_scale(ctx,&s2,','sws_scale(ctx,(const uint8_t *const *)&s2,')
if t2==t: raise SystemExit('ERROR: spudec swscale anchors not found')
spu.write_text(t2,encoding='utf-8')
PY
if ! grep -q '#define MAXPATHLEN 1024' source/filebrowser.h; then
python3 - <<'PY'
from pathlib import Path
p=Path('source/filebrowser.h'); s=p.read_text(encoding='utf-8'); marker='#define _FILEBROWSER_H_\n'
if marker not in s: raise SystemExit('ERROR: filebrowser.h anchor changed')
if '#ifndef MAXPATHLEN' not in s: s=s.replace(marker,marker+'\n#ifndef MAXPATHLEN\n#define MAXPATHLEN 1024\n#endif\n',1)
p.write_text(s,encoding='utf-8')
PY
fi
make PORTLIBS="$PORTLIBS" -j2
DOL="$UPSTREAM/wiimc.dol"; test -s "$DOL" || { echo "ERROR: expected DOL not found: $DOL" >&2; find "$UPSTREAM" -maxdepth 3 -name '*.dol' -print >&2; exit 1; }
mkdir -p "$DIST"; cp "$DOL" "$DIST/boot.dol"; cp "$META" "$DIST/meta.xml"; cp "$ROOT/icon.png" "$DIST/icon.png"
test -s "$DIST/boot.dol" && test -s "$DIST/meta.xml" && test -s "$DIST/icon.png"
printf '%s\n' "Built $DIST/boot.dol (version $PROJECT_VERSION, upstream $UPSTREAM_TAG)"
