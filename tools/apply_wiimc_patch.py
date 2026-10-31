#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "upstream-wiimc"
INPUT = SRC / "source" / "input.cpp"
VIDEO = SRC / "source" / "video.cpp"

if not INPUT.exists() or not VIDEO.exists():
    raise SystemExit("ERROR: upstream WiiMC sources are missing")

text = INPUT.read_text(encoding="utf-8")
required = (
    "MP_CMD_DVDNAV_MOUSECLICK",
    "MP_CMD_DVDNAV_SELECT",
    "MP_CMD_DVDNAV_MENU",
    "MP_CMD_DVDNAV_PREVMENU",
    "MP_CMD_DVDNAV_UP",
    "MP_CMD_DVDNAV_DOWN",
    "MP_CMD_DVDNAV_LEFT",
    "MP_CMD_DVDNAV_RIGHT",
)
for name in required:
    if name not in text:
        raise SystemExit(f"ERROR: native DVDNav command missing: {name}")

# The upstream WiiMC already has the correct DVDNav engine and pointer click path.
# Only extend the DVD-menu branch with explicit D-pad navigation and a safe 2/Y menu action.
old = '''\telse\n\t{\n\t\tif(userInput[0].wpad->ir.valid)\n\t\t\twiiUpdatePointer((int)userInput[0].wpad->ir.x, (int)userInput[0].wpad->ir.y);\n\n\t\tif(userInput[0].wpad->btns_d & WPAD_BUTTON_A || down & PAD_BUTTON_A)\n\t\t{\n\t\t\tif(userInput[0].wpad->ir.valid)\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_MOUSECLICK);\n\t\t\telse\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_SELECT);\n\t\t}\n\t\telse if (userInput[0].wpad->btns_h & WPAD_BUTTON_B || held & PAD_TRIGGER_Z)'''
new = '''\telse\n\t{\n\t\tif(userInput[0].wpad->ir.valid)\n\t\t\twiiUpdatePointer((int)userInput[0].wpad->ir.x, (int)userInput[0].wpad->ir.y);\n\n\t\tif(userInput[0].wpad->btns_d & WPAD_BUTTON_A || down & PAD_BUTTON_A)\n\t\t{\n\t\t\tif(userInput[0].wpad->ir.valid)\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_MOUSECLICK);\n\t\t\telse\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_SELECT);\n\t\t}\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_UP || down & PAD_BUTTON_UP)\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_UP);\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_DOWN || down & PAD_BUTTON_DOWN)\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_DOWN);\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_LEFT || down & PAD_BUTTON_LEFT)\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_LEFT);\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_RIGHT || down & PAD_BUTTON_RIGHT)\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_RIGHT);\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_2)\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_MENU);\n\t\telse if (userInput[0].wpad->btns_h & WPAD_BUTTON_B || held & PAD_TRIGGER_Z)'''
if old not in text:
    raise SystemExit("ERROR: expected upstream DVD menu block not found")
text = text.replace(old, new, 1)
# Button 2 returns to the previous DVD menu level (Part -> Title -> Root).
text = text.replace(
    "wiiDVDNav(MP_CMD_DVDNAV_MENU);",
    "wiiDVDNav(MP_CMD_DVDNAV_PREVMENU);",
)
INPUT.write_text(text, encoding="utf-8")

# Do not add a second/custom video bar. The native WiiMC video GUI remains the sole bar.
video = VIDEO.read_text(encoding="utf-8")
if "WMPV14_DrawBar" in video or "wmp_v14_bar.h" in video:
    raise SystemExit("ERROR: experimental custom video bar is still present")

print("PATCH_OK: native WiiMC DVDNav + pointer + D-pad + 2/previous-menu")
