# Wii Modern Media Player — WiiMC / DVDNav integration

This project builds WiiMC from a pinned upstream source and applies a small, reproducible input patch at build time.

## Current revision
- Uses WiiMC's native DVDNav playback and menu engine.
- During normal DVD playback, Wiimote **2** keeps the native WiiMC action for opening the DVD menu.
- While a DVD menu is active, Wiimote **2** sends `MP_CMD_DVDNAV_PREVMENU` to return to the previous DVD menu level.
- Wiimote IR pointer movement is retained; **A** uses DVDNav mouse-click when the pointer is valid and DVDNav select otherwise.
- DVD-menu D-pad navigation sends native DVDNav UP/DOWN/LEFT/RIGHT commands.
- The native WiiMC video control bar is retained; no experimental second/custom V14 overlay is built.
- The build pins WiiMC to commit `fae733f1ee51db8f8c9e3560cdb8b65835174f00` so a future upstream change cannot silently alter the patch target.

## Build

With devkitPro/devkitPPC and network access:

`make`

Output: `dist/apps/WiiModernMediaPlayer/`.

## Wii installation

Copy the resulting `WiiModernMediaPlayer` directory to:

`SD:/apps/WiiModernMediaPlayer/`

The Homebrew Launcher entry uses `boot.dol`, `meta.xml`, and `icon.png`.

## Important

A successful build verifies compilation and DOL structure; it cannot replace a real Wii/DVD test. DVD menu entry, pointer selection, D-pad navigation, previous-menu behavior, and long/complex DVD menu transitions should be tested with a real DVD containing interactive menus.
