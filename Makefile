#---------------------------------------------------------------------------------
# Wii Modern Media Player
# Build wrapper for upstream WiiMC + the WMP integration patch.
#---------------------------------------------------------------------------------
.SUFFIXES:
.PHONY: all build package clean
all: build
build:
	./tools/build_upstream.sh
package: build
	@echo "Homebrew package: dist/apps/WiiModernMediaPlayer/"
clean:
	rm -rf upstream-wiimc dist
