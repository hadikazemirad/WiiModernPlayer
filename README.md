# Wii Modern Media Player — V14/DVDLib integration

This version patches the upstream WiiMC source at build time.

## This revision
- The bottom strip is now a real three-button playback strip: rewind, pause/resume and fast-forward.
- Wiimote IR pointer + A is used for the strip's buttons.
- A on a DVD menu uses WiiMC's DVDNav mouse-click/select path.
- Short B during normal playback returns to the WiiMC browser; B + direction keeps the native resize gesture.
- D-pad DVD navigation remains on native DVDNav commands.

## Build

With devkitPro/devkitPPC and network access:

`make`

Output: `dist/apps/WiiModernMediaPlayer/`.


**Video controls:** No custom overlay/bar is added; WiiMC’s native video control bar is retained. The obsolete experimental bar source files have been removed.
