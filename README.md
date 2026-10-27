# Wii Modern Media Player — V14/DVDLib integration

This version patches the upstream WiiMC-SS source at build time.

## This revision
- WiiMC-SS v3.0.0-2024 is used as the playback base.
- DVD navigation uses the upstream native DVDNav command path.
- Wiimote IR pointer + A performs DVD menu mouse-click selection.
- D-pad and Classic Controller directions are routed to DVDNav navigation.
- 2 on the Wiimote, Y on Classic Controller, and Y on GameCube Controller open the DVD root menu while an actual DVD title is playing.
- In DVD menus, holding 2/Y provides modifier-style DVD controls: A/1/X selects, B opens the DVD menu, and the D-pad navigates.
- B without the 2/Y modifier returns to the previous DVD menu.
- Normal non-DVD playback keeps the standard Y volume-up behavior.
- DVD looping is left to DVDNav instead of the generic media loop.
- The WiiMC native video control bar is retained; the obsolete experimental custom V14 overlay is not used.

## Build

With devkitPro/devkitPPC and network access:

`make`

Output: `dist/apps/WiiModernMediaPlayer/`.

## Important

A successful GitHub Actions build verifies compilation and package generation. Actual optical-DVD menu behavior, pointer selection, and controller behavior still require testing on a physical Wii with a DVD.
