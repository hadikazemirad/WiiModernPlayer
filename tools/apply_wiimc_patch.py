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

old_volume='''\t\telse if(userInput[0].wpad->btns_h & WPAD_BUTTON_PLUS || held & PAD_BUTTON_Y ||\n\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_Y)'''
new_volume='''\t\telse if(userInput[0].wpad->btns_h & WPAD_BUTTON_PLUS ||\n\t\t\t((held & PAD_BUTTON_Y || userInput[0].cpad.data.down & CTR_BUTTON_Y) && !wiiPlayingDVD()))'''
if old_volume not in text: raise SystemExit('ERROR: volume/Y anchor not found')
text=text.replace(old_volume,new_volume,1)

old='''\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_2)// || down & PAD_TRIGGER_L)\n\t\t{\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_MENU);\n\t\t}'''
new='''\t\telse if(wiiPlayingDVD() &&\n\t\t\t(userInput[0].wpad->btns_d & WPAD_BUTTON_2 ||\n\t\t\t userInput[0].cpad.data.down & CTR_BUTTON_Y || down & PAD_BUTTON_Y))\n\t\t{\n\t\t\t/* 2/Y opens the DVD root menu while a DVD is playing. */\n\t\t\twiiDVDNav(MP_CMD_DVDNAV_MENU);\n\t\t}'''
if old not in text: raise SystemExit('ERROR: playback DVD menu key anchor not found')
text=text.replace(old,new,1)

start_pat=re.compile(r'\n\telse\n\t\{\n\t\tif\(userInput\[0\]\.wpad->ir\.valid\)\n\t\t\twiiUpdatePointer\(\(int\)userInput\[0\]\.wpad->ir\.x, \(int\)userInput\[0\]\.wpad->ir\.y\);\n')
m=start_pat.search(text)
if not m: raise SystemExit('ERROR: DVD menu input block start not found')
end=text.find('\n\t}\n\n\tif(volumeUpdated)',m.start())
if end<0: raise SystemExit('ERROR: DVD menu input block end not found')
block='''
\telse
\t{
\t\t/* DVD menu controls: a short 2/Y press opens root menu; held 2/Y is modifier mode. */
\t\tconst bool dvdRootMenuPressed =
\t\t\t(userInput[0].wpad->btns_d & WPAD_BUTTON_2) != 0 ||
\t\t\t(userInput[0].cpad.data.down & CTR_BUTTON_Y) != 0 ||
\t\t\t(down & PAD_BUTTON_Y) != 0;
\t\tconst bool dvdModifier =
\t\t\t(userInput[0].wpad->btns_h & WPAD_BUTTON_2) != 0 ||
\t\t\t(userInput[0].cpad.data.held & CTR_BUTTON_Y) != 0 ||
\t\t\t(held & PAD_BUTTON_Y) != 0;

\t\tif(userInput[0].wpad->ir.valid)
\t\t\twiiUpdatePointer((int)userInput[0].wpad->ir.x, (int)userInput[0].wpad->ir.y);

\t\tif(dvdRootMenuPressed)
\t\t\twiiDVDNav(MP_CMD_DVDNAV_MENU);
\t\telse if(dvdModifier)
\t\t{
\t\t\tif(userInput[0].wpad->btns_d & (WPAD_BUTTON_A | WPAD_BUTTON_1) ||
\t\t\t\tdown & (PAD_BUTTON_A | PAD_BUTTON_X) ||
\t\t\t\tuserInput[0].cpad.data.down & (CTR_BUTTON_A | CTR_BUTTON_X))
\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_SELECT);
\t\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_B || down & PAD_BUTTON_B ||
\t\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_B)
\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_MENU);
\t\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_UP || down & PAD_BUTTON_UP ||
\t\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_UP)
\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_UP);
\t\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_DOWN || down & PAD_BUTTON_DOWN ||
\t\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_DOWN)
\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_DOWN);
\t\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_RIGHT || down & PAD_BUTTON_RIGHT ||
\t\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_RIGHT)
\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_RIGHT);
\t\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_LEFT || down & PAD_BUTTON_LEFT ||
\t\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_LEFT)
\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_LEFT);
\t\t}
\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_A || down & PAD_BUTTON_A ||
\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_A)
\t\t{
\t\t\tif(userInput[0].wpad->ir.valid)
\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_MOUSECLICK);
\t\t\telse
\t\t\t\twiiDVDNav(MP_CMD_DVDNAV_SELECT);
\t\t}
\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_B || down & PAD_BUTTON_B ||
\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_B)
\t\t{
\t\t\t/* B = previous DVD menu. */
\t\t\twiiDVDNav(MP_CMD_DVDNAV_PREVMENU);
\t\t}
\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_UP || down & PAD_BUTTON_UP ||
\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_UP)
\t\t\twiiDVDNav(MP_CMD_DVDNAV_UP);
\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_DOWN || down & PAD_BUTTON_DOWN ||
\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_DOWN)
\t\t\twiiDVDNav(MP_CMD_DVDNAV_DOWN);
\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_RIGHT || down & PAD_BUTTON_RIGHT ||
\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_RIGHT)
\t\t\twiiDVDNav(MP_CMD_DVDNAV_RIGHT);
\t\telse if(userInput[0].wpad->btns_d & WPAD_BUTTON_LEFT || down & PAD_BUTTON_LEFT ||
\t\t\tuserInput[0].cpad.data.down & CTR_BUTTON_LEFT)
\t\t\twiiDVDNav(MP_CMD_DVDNAV_LEFT);
\t}'''
text=text[:m.start()]+block+text[end+3:]
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

DVDNAV=SRC/'source/mplayer/stream/stream_dvdnav.c'
if not DVDNAV.exists(): raise SystemExit('ERROR: missing upstream DVDNav source')
dt=DVDNAV.read_text()
disabled=re.compile(r'#ifdef GEKKO\s*\n\s*// always hide button highlight\s*\n\s*hlev->sx = hlev->ex = 0;\s*\n\s*hlev->sy = hlev->ey = 0;\s*\n\s*hlev->palette = hlev->buttonN = 0;\s*\n#else\s*\n(.*?)\n#endif',re.S)
dt2,n=disabled.subn(lambda m:m.group(1),dt,count=1)
if n != 1:
    if 'always hide button highlight' in dt: raise SystemExit('ERROR: DVDNav highlight-disable block changed; refusing unsafe patch')
    if 'hlev->sx = FFMIN (btni->x_start, btni->x_end);' not in dt: raise SystemExit('ERROR: DVDNav highlight calculation not found')
    dt2=dt
reset='''  hlev->display = display_mode; /* show */
  hlev->sx = hlev->ex = 0;
  hlev->sy = hlev->ey = 0;
  hlev->palette = 0;
'''
if reset not in dt2:
    marker='  hlev->display = display_mode; /* show */\n'
    if dt2.count(marker) != 1: raise SystemExit('ERROR: DVDNav highlight reset anchor missing/ambiguous')
    dt2=dt2.replace(marker,reset,1)
DVDNAV.write_text(dt2)

wt=WIIMC.read_text()
if '#include <sys/stat.h>' not in wt:
    pos=wt.find('#include')
    if pos<0: raise SystemExit('ERROR: wiimc include anchor missing')
    wt=wt[:pos]+'#include <sys/stat.h>\n'+wt[pos:]
anchor='void LoadMPlayerFile()\n{\n'
if anchor not in wt: raise SystemExit('ERROR: LoadMPlayerFile anchor missing')
helper='''static bool NormalizeDVDComponent(char *path, size_t pathSize)
{
\tif(!path || !path[0] || pathSize < 2 || strncmp(path, "dvd", 3) == 0) return false;
\tchar ext[7] = {0}; GetExt(path, ext);
\tif(strcasecmp(ext, "vob") != 0 && strcasecmp(ext, "ifo") != 0) return false;
\tchar *slash = strrchr(path, '/');
\tif(!slash) return false;
\tchar root[1024]; size_t n=(size_t)(slash-path);
\tif(n >= sizeof(root)-10) return false;
\tmemcpy(root,path,n); root[n]=0;
\tconst char *leaf=slash+1;
\tif(strcasecmp(leaf,"VIDEO_TS.IFO")==0) return false;
\tchar *lastroot = strrchr(root,'/'); const char *rootleaf = lastroot ? lastroot + 1 : root; if(strcasecmp(rootleaf,"VIDEO_TS") != 0) {
\t\tchar ts[1024]; snprintf(ts,sizeof(ts),"%s/VIDEO_TS",root); struct stat st;
\t\tif(stat(ts,&st)==0 && S_ISDIR(st.st_mode)) strncpy(root,ts,sizeof(root)-1);
\t}
\tchar ifo[1024]; snprintf(ifo,sizeof(ifo),"%s/VIDEO_TS.IFO",root); struct stat st;
\tif(stat(ifo,&st)!=0) return false;
\tstrncpy(path,ifo,pathSize-1); path[pathSize-1]=0; return true;
}

'''
wt=wt.replace(anchor,helper+anchor,1)
old='\tchar ext[7];\n\tGetExt(loadedFile, ext);\n\n\twiiSetDVDDevice(NULL);\n'
new='\tchar ext[7];\n\tGetExt(loadedFile, ext);\n\tNormalizeDVDComponent(loadedFile, sizeof(loadedFile));\n\tGetExt(loadedFile, ext);\n\n\twiiSetDVDDevice(NULL);\n'
if old not in wt: raise SystemExit('ERROR: DVD load anchor missing')
wt=wt.replace(old,new,1)
loop='\tif(WiiSettings.autoPlayNextVideo == AUTOPLAY_LOOP) // Loop video setting from mplayer\n\t\twiiSetLoopOn();\n'
guard='\tif(WiiSettings.autoPlayNextVideo == AUTOPLAY_LOOP && strncmp(loadedFile, "dvd", 3) != 0 && !IsDVDComponentPath(loadedFile)) // Loop normal media only; DVDNav owns DVD transitions\n\t\twiiSetLoopOn();\n'
# Guard both the dvd pseudo-source and VIDEO_TS components from generic looping.
if loop not in wt: raise SystemExit('ERROR: generic loop anchor missing')
# helper for the loop guard
loophelper='''static bool IsDVDComponentPath(const char *path)
{
\tif(!path || !path[0]) return false;
\tchar ext[7] = {0}; GetExt((char *)path, ext);
\tif(strcasecmp(ext, "vob") != 0 && strcasecmp(ext, "ifo") != 0) return false;
\treturn strcasestr(path, "VIDEO_TS") != NULL;
}

'''
wt=wt.replace('void LoadMPlayerFile()\n{\n',loophelper+'void LoadMPlayerFile()\n{\n',1)
wt=wt.replace(loop,guard,1)
WIIMC.write_text(wt)
print('PATCH_OK')