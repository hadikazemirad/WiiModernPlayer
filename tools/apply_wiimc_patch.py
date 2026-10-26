#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "upstream-wiimc"
INPUT = SRC / "source" / "input.cpp"
INPUT_HDR = SRC / "source" / "mplayer" / "input" / "input.h"
VIDEO = SRC / "source" / "video.cpp"
WIIMC = SRC / "source" / "wiimc.cpp"

for p in (INPUT, INPUT_HDR, VIDEO, WIIMC):
    if not p.exists():
        raise SystemExit(f"ERROR: upstream WiiMC source is missing: {p}")

text = INPUT.read_text(encoding="utf-8")
header_text = INPUT_HDR.read_text(encoding="utf-8")
required_native = (
    "MP_CMD_DVDNAV_MOUSECLICK", "MP_CMD_DVDNAV_SELECT", "MP_CMD_DVDNAV_MENU",
    "MP_CMD_DVDNAV_PREVMENU", "MP_CMD_DVDNAV_UP", "MP_CMD_DVDNAV_DOWN",
    "MP_CMD_DVDNAV_LEFT", "MP_CMD_DVDNAV_RIGHT",
)
for required in required_native:
    if required not in header_text:
        raise SystemExit("ERROR: expected native DVDNav command missing from input.h: " + required)

start_marker = (
    "\telse\n"
    "\t{\n"
    "\t\tif(userInput[0].wpad->ir.valid)\n"
    "\t\t\twiiUpdatePointer((int)userInput[0].wpad->ir.x, (int)userInput[0].wpad->ir.y);\n"
)
start = text.find(start_marker)
if start < 0:
    raise SystemExit("ERROR: WiiMC DVD menu input anchor not found")
end_marker = "\n\t}\n\n\tif(volumeUpdated)"
end = text.find(end_marker, start)
if end < 0:
    raise SystemExit("ERROR: WiiMC DVD menu input end anchor not found")

new = r'''	else
	{
		/* Wii Modern Media Player: V14-style DVD input, without adding a second video bar. */
		const bool dvdModifier =
			(userInput[0].wpad->btns_h & WPAD_BUTTON_2) != 0 ||
			(userInput[0].wpad->btns_h & WPAD_CLASSIC_BUTTON_Y) != 0 ||
			(held & PAD_BUTTON_Y) != 0;

		if(userInput[0].wpad->ir.valid)
			wiiUpdatePointer((int)userInput[0].wpad->ir.x, (int)userInput[0].wpad->ir.y);

		/* Hold 2/Y for the explicit V14-style DVD controller layer. */
		if(dvdModifier)
		{
			if(userInput[0].wpad->btns_d & (WPAD_BUTTON_A | WPAD_BUTTON_1) ||
				down & (PAD_BUTTON_A | PAD_BUTTON_X) ||
				userInput[0].wpad->btns_d & (WPAD_CLASSIC_BUTTON_A | WPAD_CLASSIC_BUTTON_X))
				wiiDVDNav(MP_CMD_DVDNAV_SELECT);
			else if(userInput[0].wpad->btns_d & WPAD_BUTTON_B || down & PAD_BUTTON_B ||
				userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_B)
				wiiDVDNav(MP_CMD_DVDNAV_MENU);
			else if(userInput[0].wpad->btns_d & WPAD_BUTTON_UP || down & PAD_BUTTON_UP ||
				userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_UP)
				wiiDVDNav(MP_CMD_DVDNAV_UP);
			else if(userInput[0].wpad->btns_d & WPAD_BUTTON_DOWN || down & PAD_BUTTON_DOWN ||
				userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_DOWN)
				wiiDVDNav(MP_CMD_DVDNAV_DOWN);
			else if(userInput[0].wpad->btns_d & WPAD_BUTTON_RIGHT || down & PAD_BUTTON_RIGHT ||
				userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_RIGHT)
				wiiDVDNav(MP_CMD_DVDNAV_RIGHT);
			else if(userInput[0].wpad->btns_d & WPAD_BUTTON_LEFT || down & PAD_BUTTON_LEFT ||
				userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_LEFT)
				wiiDVDNav(MP_CMD_DVDNAV_LEFT);
		}
		else if(userInput[0].wpad->btns_d & WPAD_BUTTON_A || down & PAD_BUTTON_A ||
			userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_A)
		{
			/* Pointer A is a real DVD menu click; without IR it is DVD SELECT. */
			if(userInput[0].wpad->ir.valid)
				wiiDVDNav(MP_CMD_DVDNAV_MOUSECLICK);
			else
				wiiDVDNav(MP_CMD_DVDNAV_SELECT);
		}
		else if((userInput[0].wpad->btns_d & WPAD_BUTTON_B || down & PAD_BUTTON_B ||
			userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_B) &&
			!(userInput[0].wpad->btns_h & (WPAD_BUTTON_RIGHT | WPAD_BUTTON_LEFT | WPAD_BUTTON_UP | WPAD_BUTTON_DOWN)) &&
			!(held & (PAD_BUTTON_RIGHT | PAD_BUTTON_LEFT | PAD_BUTTON_UP | PAD_BUTTON_DOWN)))
		{
			/* B is DVD previous-menu/back; 2+B is reserved for the DVD root menu above. */
			wiiDVDNav(MP_CMD_DVDNAV_PREVMENU);
		}
		else if(userInput[0].wpad->btns_h & WPAD_BUTTON_B || held & PAD_TRIGGER_Z)
		{
			/* Keep WiiMC's native B+direction resize behaviour. */
			unsigned int delay = (resizeinitial == 1) ? RESIZE_INITIAL_DELAY : RESIZE_DELAY;
			int resizenow = gettime();
			if(userInput[0].wpad->btns_h & WPAD_BUTTON_RIGHT || held & PAD_BUTTON_RIGHT)
			{
				if(diff_usec(resizeprev, resizenow) > delay)
				{ resizeinitial++; resizeprev = resizenow; MPlayerResize(+0.003F, 0.00F); }
			}
			else if(userInput[0].wpad->btns_h & WPAD_BUTTON_LEFT || held & PAD_BUTTON_LEFT)
			{
				if(diff_usec(resizeprev, resizenow) > delay)
				{ resizeinitial++; resizeprev = resizenow; MPlayerResize(-0.003F, 0.00F); }
			}
			else if(userInput[0].wpad->btns_h & WPAD_BUTTON_UP || held & PAD_BUTTON_UP)
			{
				if(diff_usec(resizeprev, resizenow) > delay)
				{ resizeinitial++; resizeprev = resizenow; MPlayerResize(0.00F, +0.003F); }
			}
			else if(userInput[0].wpad->btns_h & WPAD_BUTTON_DOWN || held & PAD_BUTTON_DOWN)
			{
				if(diff_usec(resizeprev, resizenow) > delay)
				{ resizeinitial++; resizeprev = resizenow; MPlayerResize(0.00F, -0.003F); }
			}
			if(userInput[0].wpad->btns_d & (WPAD_BUTTON_RIGHT | WPAD_BUTTON_LEFT | WPAD_BUTTON_UP | WPAD_BUTTON_DOWN))
				resizeinitial = 0;
		}
		else if(userInput[0].wpad->btns_d & WPAD_BUTTON_UP || down & PAD_BUTTON_UP ||
			userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_UP)
			wiiDVDNav(MP_CMD_DVDNAV_UP);
		else if(userInput[0].wpad->btns_d & WPAD_BUTTON_DOWN || down & PAD_BUTTON_DOWN ||
			userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_DOWN)
			wiiDVDNav(MP_CMD_DVDNAV_DOWN);
		else if(userInput[0].wpad->btns_d & WPAD_BUTTON_RIGHT || down & PAD_BUTTON_RIGHT ||
			userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_RIGHT)
			wiiDVDNav(MP_CMD_DVDNAV_RIGHT);
		else if(userInput[0].wpad->btns_d & WPAD_BUTTON_LEFT || down & PAD_BUTTON_LEFT ||
			userInput[0].wpad->btns_d & WPAD_CLASSIC_BUTTON_LEFT)
			wiiDVDNav(MP_CMD_DVDNAV_LEFT);
	}
'''
text = text[:start] + new + text[end + 4:]

a_pattern = re.compile(
    r"(?ms)^[ \t]*if\s*\(!drawGui\s*\|\|\s*\(y\s*<\s*360\s*&&.*?^[ \t]*\}\s*(?=\n)")
a_replacement = "\t\t\tif(!drawGui || !userInput[0].wpad->ir.valid)\n\t\t\t\twiiPause();"
text, a_count = a_pattern.subn(a_replacement, text, count=1)
if a_count != 1:
    raise SystemExit("ERROR: native A/Pause logic not found (expected one WiiMC GUI-gated pause block)")
INPUT.write_text(text, encoding="utf-8")

vt = VIDEO.read_text(encoding="utf-8")
vt = re.sub(r'^\s*#include\s+"wmp_v14_bar\.h"\s*\n', '', vt, flags=re.MULTILINE)
vt = re.sub(r'^\s*WMPV14_DrawBar\s*\(\s*\)\s*;\s*\n', '', vt, flags=re.MULTILINE)
if 'WMPV14_DrawBar();' in vt or 'wmp_v14_bar.h' in vt:
    raise SystemExit("ERROR: experimental custom video bar remains in upstream video.cpp")
VIDEO.write_text(vt, encoding="utf-8")

wt = WIIMC.read_text(encoding="utf-8")
if "#include <sys/stat.h>" not in wt:
    first_include = wt.find("#include")
    if first_include < 0:
        raise SystemExit("ERROR: no include section found in wiimc.cpp")
    wt = wt[:first_include] + "#include <sys/stat.h>\n" + wt[first_include:]
anchor = 'void LoadMPlayerFile()\n{\n'
if anchor not in wt:
    raise SystemExit("ERROR: LoadMPlayerFile anchor changed")
helper = r'''
static bool NormalizeDVDComponent(char *path, size_t pathSize)
{
	if(!path || path[0] == 0 || pathSize < 2 || strncmp(path, "dvd", 3) == 0)
		return false;

	char ext[7] = {0};
	GetExt(path, ext);
	if(strcasecmp(ext, "vob") != 0 && strcasecmp(ext, "ifo") != 0)
		return false;

	char candidate[1024];
	strncpy(candidate, path, sizeof(candidate)-1);
	candidate[sizeof(candidate)-1] = 0;
	char *slash = strrchr(candidate, '/');
	if(!slash)
		return false;
	char basename[256];
	snprintf(basename, sizeof(basename), "%s", slash + 1);
	*slash = 0;

	char root[1024] = {0};
	if(strcasecmp(candidate, "") == 0)
		return false;
	if(strcasecmp(basename, "VIDEO_TS.IFO") == 0)
		return false;

	char *last = strrchr(candidate, '/');
	const char *leaf = last ? last + 1 : candidate;
	if(strcasecmp(leaf, "VIDEO_TS") == 0)
	{
		snprintf(root, sizeof(root), "%s", candidate);
	}
	else
	{
		char ts[1024];
		snprintf(ts, sizeof(ts), "%s/VIDEO_TS", candidate);
		struct stat st;
		if(stat(ts, &st) == 0 && S_ISDIR(st.st_mode))
			snprintf(root, sizeof(root), "%s", ts);
		else
			snprintf(root, sizeof(root), "%s", candidate);
	}

	char ifo[1024];
	snprintf(ifo, sizeof(ifo), "%s/VIDEO_TS.IFO", root);
	struct stat st;
	if(stat(ifo, &st) != 0)
		return false;

	strncpy(path, ifo, pathSize - 1);
	path[pathSize - 1] = 0;
	return true;
}
'''
wt = wt.replace(anchor, helper + anchor, 1)
old = '\tchar ext[7];\n\tGetExt(loadedFile, ext);\n\n\twiiSetDVDDevice(NULL);\n'
new = '\tchar ext[7];\n\tGetExt(loadedFile, ext);\n\n\t/* Prefer the DVD root IFO over a short navigation VOB. */\n\tif(NormalizeDVDComponent(loadedFile, sizeof(loadedFile)))\n\t\tGetExt(loadedFile, ext);\n\n\twiiSetDVDDevice(NULL);\n'
if old not in wt:
    raise SystemExit("ERROR: DVD LoadMPlayerFile anchor changed")
wt = wt.replace(old, new, 1)

loop_line = '\tif(WiiSettings.autoPlayNextVideo == AUTOPLAY_LOOP) // Loop video setting from mplayer\n\t\twiiSetLoopOn();\n'
loop_guard = '\tif(WiiSettings.autoPlayNextVideo == AUTOPLAY_LOOP && strncmp(loadedFile, "dvd", 3) != 0) // Loop normal videos only; DVDNav owns DVD transitions\n\t\twiiSetLoopOn();\n'
if loop_line not in wt:
    raise SystemExit("ERROR: generic media loop block not found")
wt = wt.replace(loop_line, loop_guard, 1)
WIIMC.write_text(wt, encoding="utf-8")

print("PATCH_OK")
