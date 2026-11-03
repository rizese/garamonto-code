# Makefile for Garamonto Code
#
#   make          build the fonts in fonts/ from the sources in source/
#   make site     rebuild the showcase page's character list
#   make info     list the pages and links

# FontForge's Python module (Homebrew), and a Python environment made with the
# Python it was built for, holding the other libraries the build uses
FFPYTHON:=$(firstword $(wildcard /opt/homebrew/opt/fontforge/lib/python3*/site-packages))
FFVERSION:=$(notdir $(patsubst %/site-packages,%,${FFPYTHON}))
export PYTHONPATH:=${FFPYTHON}
PYTHON=.venv/bin/python
LIBRARIES="fonttools[woff]" skia-pathops booleanOperations freetype-py numpy fontforge-ref-sel-util

TTF=fonts/ttf
WEB=fonts/webfonts
STYLES=GaramontoCode GaramontoCode-Italic GaramontoCode-Medium \
       GaramontoCode-MediumItalic GaramontoCode-Bold GaramontoCode-BoldItalic
FONTS=$(STYLES:%=${TTF}/%.ttf) $(STYLES:%=${WEB}/%.woff2)
BUILD=source/build_font.py source/hinting.py source/ligatures.py source/ligatures.fea

.PHONY: all
all: ${FONTS}

.venv:
	/opt/homebrew/bin/${FFVERSION} -m venv .venv
	.venv/bin/pip install -q ${LIBRARIES}

${TTF}/%.ttf: source/%.sfd ${BUILD} | .venv
	${PYTHON} source/build_font.py $@ $<
${WEB}/%.woff2: source/%.sfd ${BUILD} | .venv
	${PYTHON} source/build_font.py $@ $<

# Medium has no source of its own: it is made from the built Regular or Italic
${TTF}/GaramontoCode-Medium.ttf: ${TTF}/GaramontoCode.ttf source/build_medium.py source/hinting.py | .venv
	${PYTHON} source/build_medium.py $@ $<
${TTF}/GaramontoCode-MediumItalic.ttf: ${TTF}/GaramontoCode-Italic.ttf source/build_medium.py source/hinting.py | .venv
	${PYTHON} source/build_medium.py $@ $<
${WEB}/GaramontoCode-Medium.woff2: ${WEB}/GaramontoCode.woff2 source/build_medium.py source/hinting.py | .venv
	${PYTHON} source/build_medium.py $@ $<
${WEB}/GaramontoCode-MediumItalic.woff2: ${WEB}/GaramontoCode-Italic.woff2 source/build_medium.py source/hinting.py | .venv
	${PYTHON} source/build_medium.py $@ $<

.PHONY: site
site: source/charmap.json
source/charmap.json: ${TTF}/GaramontoCode.ttf ${TTF}/GaramontoCode-Italic.ttf source/build_charmap.py | .venv
	${PYTHON} source/build_charmap.py ${TTF} $@

PORT ?= 8793
LOCAL := http://127.0.0.1:${PORT}

.PHONY: info
info:
	@echo "Showcase page          ${LOCAL}/index.html"
	@echo "  every character      ${LOCAL}/index.html#characters"
	@echo "Repository             https://github.com/rizese/garamonto-code"
	@echo "GitHub Pages           https://rizese.github.io/garamonto-code/"
	@echo "Download               https://github.com/rizese/garamonto-code/releases/latest/download/GaramontoCode.zip"
	@curl -s -o /dev/null ${LOCAL}/ && echo "The local server is running on port ${PORT}." \
	|| echo "The local server is not running: python3 -m http.server ${PORT} --bind 127.0.0.1"
