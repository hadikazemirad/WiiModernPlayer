# Wii Modern Media Player
# The real WiiMC build stays in upstream; this file only drives it.

.PHONY: all build package clean

all: build

build:
	@./tools/build_upstream.sh

package: build
	@echo "Homebrew package: dist/apps/WiiModernMediaPlayer/"

clean:
	@rm -rf upstream-wiimc dist
