#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream-wiimc"

for rel in ("source/mplayer/config.mak", "source/mplayer/Makefile"):
    p = UPSTREAM / rel
    if p.exists():
        s = p.read_text(encoding="utf-8")
        s2 = s.replace("-mpaired", "").replace("-mstring", "")
        if s2 != s:
            p.write_text(s2, encoding="utf-8")

p = UPSTREAM / "source/fileop.cpp"
s = p.read_text(encoding="utf-8")
if "#include <ntfs.h>" in s and "#ifdef WANT_NTFS" not in s:
    s = s.replace("#include <ntfs.h>", "#ifdef WANT_NTFS\n#include <ntfs.h>\n#endif", 1)
if "#include <ext2.h>" in s and "#ifdef WANT_EXT2" not in s:
    s = s.replace("#include <ext2.h>", "#ifdef WANT_EXT2\n#include <ext2.h>\n#endif", 1)
p.write_text(s, encoding="utf-8")

p = UPSTREAM / "Makefile"
s = p.read_text(encoding="utf-8")
s2 = s.replace("\t\t\t\t\t$(CURDIR)/source/utils/ehcmodule.elf.o\n", "")
# libogc2's current linker script normally provides this absolute exception
# buffer symbol; define it explicitly as a compatibility fallback for the
# WiiMC-SS link command.
if "__ppc_excpt_buf=0x800000d0" not in s2:
    s2 += "\n# libogc2 exception-buffer compatibility\nLDFLAGS += -Wl,--defsym,__ppc_excpt_buf=0x800000d0\n"
if s2 != s:
    p.write_text(s2, encoding="utf-8")

p = UPSTREAM / "source/mplayer/mplayer.c"
s = p.read_text(encoding="utf-8")
old = '''void wiiSetLoopOn()\n{\n\tif(filename && strncmp(filename, "dvd", 3) == 0)\n\t{\n\t\tm_config_set_option(mconfig, "loop", "-1");\n\t\treturn;\n\t}\n\tif(mpctx->sh_video)'''
new = '''void wiiSetLoopOn()\n{\n\tif(filename && strncmp(filename, "dvd", 3) == 0)\n\t\treturn;\n\tif(mpctx->sh_video)'''
if old in s:
    s = s.replace(old, new, 1)
else:
    old2 = '''void wiiSetLoopOn()\n{\n\tif(mpctx->sh_video)'''
    new2 = '''void wiiSetLoopOn()\n{\n\tif(filename && strncmp(filename, "dvd", 3) == 0)\n\t\treturn;\n\tif(mpctx->sh_video)'''
    if old2 not in s:
        raise SystemExit("ERROR: wiiSetLoopOn anchor not found")
    s = s.replace(old2, new2, 1)
p.write_text(s, encoding="utf-8")

p = UPSTREAM / "source/mplayer/libdvdnav/dvdnav_internal.h"
s = p.read_text(encoding="utf-8")
old_macros = '''#define pthread_mutex_init(a, b) LWP_MutexInit(a,false)\n#define pthread_mutex_lock(a)    LWP_MutexLock(*a)\n#define pthread_mutex_unlock(a)  LWP_MutexUnlock(*a)\n#define pthread_mutex_destroy(a) LWP_MutexDestroy(*a)'''
new_macros = '''#define pthread_mutex_init(a, b) LWP_MutexInit((mutex_t *)(a),false)\n#define pthread_mutex_lock(a)    LWP_MutexLock(*(mutex_t *)(a))\n#define pthread_mutex_unlock(a)  LWP_MutexUnlock(*(mutex_t *)(a))\n#define pthread_mutex_destroy(a) LWP_MutexDestroy(*(mutex_t *)(a))'''
if old_macros not in s:
    raise SystemExit("ERROR: dvdnav mutex macro block not found")
s = s.replace(old_macros, new_macros, 1)
p.write_text(s, encoding="utf-8")

# swscale now takes const plane arrays.
p = UPSTREAM / "source/mplayer/libmpcodecs/vf_screenshot.c"
s = p.read_text(encoding="utf-8")
s2 = s.replace("sws_scale(priv->ctx, mpi->planes,", "sws_scale(priv->ctx, (const uint8_t *const *)mpi->planes,")
s2 = s2.replace("sws_scale(vf->priv->ctx, src,", "sws_scale(vf->priv->ctx, (const uint8_t *const *)src,")
if s2 != s:
    p.write_text(s2, encoding="utf-8")

print("UPSTREAM_COMPAT_OK")
