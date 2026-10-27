#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'upstream-wiimc'
INPUT=SRC/'source/input.cpp'; HDR=SRC/'source/mplayer/input/input.h'; VIDEO=SRC/'source/video.cpp'; WIIMC=SRC/'source/wiimc.cpp'
for p in (INPUT,HDR,VIDEO,WIIMC):
    if not p.exists(): raise SystemExit(f'ERROR: missing upstream source: {p}')
text=INPUT.read_text(); header=HDR.read_text()
for name in ('MP_CMD_DVDNAV_MOUSECLICK','MP_CMD_DVDNAV_SELECT','MP_CMD_DVDNAV_MENU','MP_CMD_DVDNAV_PREVMENU','MP_CMD_DVDNAV_UP','MP_CMD_DVDNAV_DOWN','MP_CMD_DVDNAV_LEFT','MP_CMD_DVDNAV_RIGHT'):
    if name not in header: raise SystemExit('ERROR: missing native DVDNav command: '+name)

# Playback: Wiimote 2 + Classic Controller Y + GameCube Y open DVD root menu.
old='''\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_2)// || down & PAD_TRIGGER_L)\n\t\t{\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_MENU);\n\t\t}'''
new='''\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_2 ||\n\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_Y || down & PAD_BUTTON_Y)\n\t\t{\n\t\t\t/* 2/Y opens the DVD root menu while a DVD is playing. */\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_MENU);\n\t\t}'''
if old not in text: raise SystemExit('ERROR: playback DVD menu key anchor not found')
text=text.replace(old,new,1)

# Replace only the DVD-menu input block, anchored by its native pointer update and the volume block.
start_pat=re.compile(r'\n\telse\n\t\{\n\t\tif\(userInput\[0\]\.wpad->ir\.valid\)\n\t\t\twiiUpdatePointer\(\(int\)userInput\[0\]\.wpad->ir\.x, \(int\)userInput\[0\]\.wpad->ir\.y\);\n')
m=start_pat.search(text)
if not m: raise SystemExit('ERROR: DVD menu input block start not found')
end=text.find('\n\t}\n\n\tif(volumeUpdated)',m.start())
if end<0: raise SystemExit('ERROR: DVD menu input block end not found')
block='''\n\telse\n\t{\n\t\t/* DVD menu controls: IR pointer first, with 2/Y modifier mode. */\n\t\tconst bool dvdModifier =\n\t\t\t(userInput[0].wpad->btns_h & WPAD_BUTTON_2) != 0 ||\n\t\t\t(userInput[0].cpad.data.down & CTR_BUTTON_Y) != 0 ||\n\t\t\t(held & PAD_BUTTON_Y) != 0;\n\n\t\tif(userInput[0].wpad->ir.valid)\n\t\t\twiiUpdatePointer((int)userInput[0].wpad->ir.x, (int)userInput[0].wpad->ir.y);\n\n\t\tif(dvdModifier)\n\t\t{\n\t\t\tif(userInput[0].wpad->btns_d & (WPAD_BUTTON_A | WPAD_BUTTON_1) ||\n\t\t\t\tdown & (PAD_BUTTON_A | PAD_BUTTON_X) ||\n\t\t\t\tuserInput[0].cpad.data.down & (CTR_BUTTON_A | CTR_BUTTON_X))\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_SELECT);\n\t\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_B || down & PAD_BUTTON_B ||\n\t\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_B)\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_MENU);\n\t\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_UP || down & PAD_BUTTON_UP ||\n\t\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_UP)\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_UP);\n\t\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_DOWN || down & PAD_BUTTON_DOWN ||\n\t\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_DOWN)\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_DOWN);\n\t\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_RIGHT || down & PAD_BUTTON_RIGHT ||\n\t\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_RIGHT)\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_RIGHT);\n\t\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_LEFT || down & PAD_BUTTON_LEFT ||\n\t\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_LEFT)\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_LEFT);\n\t\t}\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_A || down & PAD_BUTTON_A ||\n\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_A)\n\t\t{\n\t\t\tif(userInput[0].wpad->ir.valid)\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_MOUSECLICK);\n\t\t\telse\n\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_SELECT);\n\t\t}\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_B || down & PAD_BUTTON_B ||\n\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_B)\n\t\t{\n\t\t\t/* B = previous DVD menu. */\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_PREVMENU);\n\t\t}\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_UP || down & PAD_BUTTON_UP ||\n\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_UP)\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_UP);\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_DOWN || down & PAD_BUTTON_DOWN ||\n\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_DOWN)\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_DOWN);\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_RIGHT || down & PAD_BUTTON_RIGHT ||\n\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_RIGHT)\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_RIGHT);\n\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_LEFT || down & PAD_BUTTON_LEFT ||\n\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_LEFT)\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_LEFT);\n\t}'''
text=text[:m.start()]+block+text[end+3:]
# Avoid accidental pause while IR pointer is used for DVD selection.
pause_pattern=re.compile(r'\t\t\tif\(!drawGui \|\| \(y < 360 &&.*?\n\t\t\t\{\n\t\t\t\twiiPause\(\);\n\t\t\t\}',re.S)
pause_replacement='\t\t\tif(!drawGui || !userInput[0].wpad->ir.valid)\n\t\t\t{\n\t\t\t\twiiPause();\n\t\t\t}'
text,pause_count=pause_pattern.subn(pause_replacement,text,count=1)
if pause_count != 1: raise SystemExit('ERROR: A/Pause block anchor not found')
INPUT.write_text(text)

vt=VIDEO.read_text()
vt=re.sub(r'^#include\s+"wmp_v14_bar\.h"\s*\n','',vt,flags=re.M)
vt=re.sub(r'^\s*WMPV14_DrawBar\(\);\s*\n','',vt,flags=re.M)
if 'WMPV14_DrawBar();' in vt or 'wmp_v14_bar.h' in vt: raise SystemExit('ERROR: experimental bar remains')
VIDEO.write_text(vt)

wt=WIIMC.read_text()
if '#include <sys/stat.h>' not in wt:
    pos=wt.find('#include')
    if pos<0: raise SystemExit('ERROR: wiimc include anchor missing')
    wt=wt[:pos]+'#include <sys/stat.h>\n'+wt[pos:]
anchor='void LoadMPlayerFile()\n{\n'
if anchor not in wt: raise SystemExit('ERROR: LoadMPlayerFile anchor missing')
helper='''static bool NormalizeDVDComponent(char *path, size_t pathSize)\n{\n\tif(!path || !path[0] || pathSize < 2 || strncmp(path, "dvd", 3) == 0) return false;\n\tchar ext[7] = {0}; GetExt(path, ext);\n\tif(strcasecmp(ext, "vob") != 0 && strcasecmp(ext, "ifo") != 0) return false;\n\tchar *slash = strrchr(path, '/');\n\tif(!slash) return false;\n\tchar root[1024]; size_t n=(size_t)(slash-path);\n\tif(n >= sizeof(root)-10) return false;\n\tmemcpy(root,path,n); root[n]=0;\n\tconst char *leaf=slash+1;\n\tif(strcasecmp(leaf,"VIDEO_TS.IFO")==0) return false;\n\tchar *lastroot = strrchr(root,'/'); const char *rootleaf = lastroot ? lastroot + 1 : root; if(strcasecmp(rootleaf,"VIDEO_TS") != 0) {\n\t\tchar ts[1024]; snprintf(ts,sizeof(ts),"%s/VIDEO_TS",root); struct stat st;\n\t\tif(stat(ts,&st)==0 && S_ISDIR(st.st_mode)) strncpy(root,ts,sizeof(root)-1);\n\t}\n\tchar ifo[1024]; snprintf(ifo,sizeof(ifo),"%s/VIDEO_TS.IFO",root); struct stat st;\n\tif(stat(ifo,&st)!=0) return false;\n\tstrncpy(path,ifo,pathSize-1); path[pathSize-1]=0; return true;\n}\n\n'''
wt=wt.replace(anchor,helper+anchor,1)
old='\tchar ext[7];\n\tGetExt(loadedFile, ext);\n\n\twiiSetDVDDevice(NULL);\n'
new='\tchar ext[7];\n\tGetExt(loadedFile, ext);\n\tNormalizeDVDComponent(loadedFile, sizeof(loadedFile));\n\tGetExt(loadedFile, ext);\n\n\twiiSetDVDDevice(NULL);\n'
if old not in wt: raise SystemExit('ERROR: DVD load anchor missing')
wt=wt.replace(old,new,1)
loop='\tif(WiiSettings.autoPlayNextVideo == AUTOPLAY_LOOP) // Loop video setting from mplayer\n\t\twiiSetLoopOn();\n'
guard='\tif(WiiSettings.autoPlayNextVideo == AUTOPLAY_LOOP && strncmp(loadedFile, "dvd", 3) != 0) // Loop normal media only; DVDNav owns DVD transitions\n\t\twiiSetLoopOn();\n'
if loop not in wt: raise SystemExit('ERROR: generic loop anchor missing')
wt=wt.replace(loop,guard,1)
WIIMC.write_text(wt)
print('PATCH_OK')
