"""Hint a TrueType font with ttfautohint, writing TTF, WOFF or WOFF2.

Hinting tells renderers how to fit stems to the pixel grid at small sizes.
macOS ignores it; Windows and many Linux setups use it. ttfautohint generates
it automatically, as it does for JetBrains Mono.
"""

import os
import subprocess
import tempfile

from fontTools.ttLib import TTFont

FLAVORS = {".ttf": None, ".woff": "woff", ".woff2": "woff2"}
OPTIONS = [
	"--no-info",                # keep the version string clean
	"--windows-compatibility",  # don't clip glyphs that reach the line box
]

def autohint(font, out):
	"""Hint `font` (a TTFont) and save it to `out` in the format its extension names."""
	for table in ("fpgm", "prep", "cvt ", "gasp"):
		if table in font:
			del font[table]  # ttfautohint refuses fonts that are already hinted
	with tempfile.TemporaryDirectory() as tmp:
		src, dst = os.path.join(tmp, "in.ttf"), os.path.join(tmp, "out.ttf")
		font.flavor = None
		font.save(src)
		subprocess.run(["ttfautohint", *OPTIONS, src, dst], check=True)
		hinted = TTFont(dst)
		hinted.flavor = FLAVORS[os.path.splitext(out)[1]]
		hinted.save(out)
