#!/usr/bin/env python3

import fontforge
import os
import tempfile
from sys import argv
import fontforge_refsel
from fontTools.ttLib import TTFont

from hinting import FLAVORS, autohint
from ligatures import add_ligatures

font = fontforge.open(argv[2])
fontforge_refsel.decomposeNestedRefs(font, True)
add_ligatures(font)
font.buildOrReplaceAALTFeatures()

if argv[1].endswith(".sfd"):
	font.save(argv[1])
elif os.path.splitext(argv[1])[1] in FLAVORS:
	# TrueType outputs are hinted by ttfautohint; see hinting.py
	with tempfile.TemporaryDirectory() as tmp:
		ttf = os.path.join(tmp, "unhinted.ttf")
		font.generate(ttf, flags=('no-mac-names','opentype','no-FFTM-table'))
		autohint(TTFont(ttf), argv[1])
else:
	font.generate(argv[1], flags=('no-mac-names','opentype','no-FFTM-table'))

font.close()
