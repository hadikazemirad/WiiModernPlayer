# Wii Modern Media Player — WiiMC / DVDNav integration

This project builds WiiMC from a pinned upstream source and applies a small, reproducible input patch at build time.

## Current implementation
- Uses WiiMC's native DVDNav playback and DVD menu engine.
- During normal DVD playback, Wiimote 2 opens the DVD menu.
- While a DVD menu is active, Wiimote 2, GameCube Y, or Classic Controller Y sends MP_CMD_DVDNAV_PREVMENU.
- Wiimote IR pointer movement is retained; A uses DVDNav mouse-click when the pointer is valid and DVDNav select otherwise.
- DVD-menu D-pad navigation is supported for Wiimote, GameCube controller, and Classic Controller.
- The native WiiMC video control bar is retained. The experimental custom WiiMC+ V14 overlay is not integrated.
- The home screen and overall interface are still the upstream WiiMC interface; a fully redesigned modern media-center UI is not yet implemented.
- The build pins WiiMC to commit fae733f1ee51db8f8c9e3560cdb8b65835174f00.

## Build

With devkitPro/devkitPPC and network access, run make.

Output: dist/apps/WiiModernMediaPlayer/.

## Wii installation

Copy the resulting WiiModernMediaPlayer directory to:

SD:/apps/WiiModernMediaPlayer/

The Homebrew Launcher entry uses boot.dol, meta.xml, and icon.png.

## Validation limits

GitHub Actions verifies compilation, the DOL structure, and package contents. It does not emulate a Wii or prove DVD menu behavior. Real-hardware tests are still required for DVD menu entry, pointer selection, all controller mappings, previous-menu behavior, and long/complex menu transitions. H.265 playback and the WiiMC+ V14 playback bar are not claimed as implemented.
