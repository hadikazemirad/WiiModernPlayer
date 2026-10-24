#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream-wiimc"

# The current libogc2 PowerPC compiler no longer accepts these legacy
# Wii-era code-generation switches used by the old MPlayer config.
for rel in ("source/mplayer/config.mak", "source/mplayer/Makefile"):
    p = UPSTREAM / rel
    if p.exists():
        s = p.read_text(encoding="utf-8")
        s2 = s.replace("-mpaired", "").replace("-mstring", "")
        if s2 != s:
            p.write_text(s2, encoding="utf-8")

# NTFS/EXT2 support is optional in WiiMC-SS.  libogc2 does not provide the
# old NTFS/EXT2 development headers by default, so make the source explicitly
# safe when those features are disabled.
p = UPSTREAM / "source/fileop.cpp"
s = p.read_text(encoding="utf-8")
if "#include <ntfs.h>" in s and "#ifdef WANT_NTFS" not in s:
    s = s.replace("#include <ntfs.h>", "#ifdef WANT_NTFS\n#include <ntfs.h>\n#endif", 1)
if "#include <ext2.h>" in s and "#ifdef WANT_EXT2" not in s:
    s = s.replace("#include <ext2.h>", "#ifdef WANT_EXT2\n#include <ext2.h>\n#endif", 1)
p.write_text(s, encoding="utf-8")

# Disable optional filesystems unless their libraries/headers are actually
# available.  This keeps the WiiMC core (SD/USB/DVD/FAT/ISO9660) intact.
p = UPSTREAM / "Makefile"
s = p.read_text(encoding="utf-8")
s2 = s.replace("ENABLE_NTFS                   = 1", "ENABLE_NTFS                   = 0")
s2 = s2.replace("ENABLE_EXT2                   = 1", "ENABLE_EXT2                   = 0")
if s2 != s:
    p.write_text(s2, encoding="utf-8")

# DVD playback must not inherit the global 'repeat/loop' media setting.
# WiiMC calls wiiSetLoopOn() when the user selects AUTOPLAY_LOOP; DVDs should
# remain under DVDNav/title control instead of restarting a selected title.
p = UPSTREAM / "source/mplayer/mplayer.c"
s = p.read_text(encoding="utf-8")
old = '''void wiiSetLoopOn()\n{\n\tif(filename && strncmp(filename, "dvd", 3) == 0)\n\t{\n\t\tm_config_set_option(mconfig, "loop", "-1");\n\t\treturn;\n\t}\n\tif(mpctx->sh_video)'''
new = '''void wiiSetLoopOn()\n{\n\tif(filename && strncmp(filename, "dvd", 3) == 0)\n\t\treturn;\n\tif(mpctx->sh_video)'''
if old in s:
    s = s.replace(old, new, 1)
else:
    # If the loop guard was not present yet, add it to the upstream function.
    old2 = '''void wiiSetLoopOn()\n{\n\tif(mpctx->sh_video)'''
    new2 = '''void wiiSetLoopOn()\n{\n\tif(filename && strncmp(filename, "dvd", 3) == 0)\n\t\treturn;\n\tif(mpctx->sh_video)'''
    if old2 not in s:
        raise SystemExit("ERROR: wiiSetLoopOn anchor not found")
    s = s.replace(old2, new2, 1)
p.write_text(s, encoding="utf-8")

print("UPSTREAM_COMPAT_OK")
