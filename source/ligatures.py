"""Coding ligatures for Garamonto Code, added at build time by build_font.py.

Each ligature keeps one cell per character, so cursors and alignment are
unchanged. The `calt` feature replaces every character but the last with an
empty spacer (LIG) and the last with the ligature glyph, which has the
normal advance width but draws leftwards over the earlier cells.

Ligatures are built only from Garamonto Code's own glyphs. See ligatures.fea
for the contexts in which they apply.
"""

import math
import os
import tempfile

import fontforge
import psMat

FEA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ligatures.fea")
MARGIN = 25  # space left at each end of a ligature, as on the hyphen
SWELL = 180  # height of a wavy arrow's wave, the same in every weight
STRIDE = 1.35  # how much longer each of its waves is than ~
TUCK = 16    # how far a wave runs inside the arrowhead it meets
TAIL = 80    # how far from a plain shaft end its points are moved
WIDEN = 1.6  # how far ≥ and ≤ widen; any further and the chevron goes flat
SQUEEZE = 0.9  # how far the italic & of && narrows so the pair stops colliding
PITCH = 0.72  # three bars sit this much closer than the two of `=`
LONG = 200   # a straight run at least this long is an arrow's shaft
TRIANGLE = 1.35  # how much the bars and chevrons of `|>` and the like grow
HEAD = 215   # how far a second arrowhead sits behind the first
GAP = 90     # gap left between characters that move together
GAPS = {     # pairs that want something else; negative where their shapes nest
	"||": 140, "..": 110, "//": -90, ">>": -164, "<<": -164, "\\/": -130, "/\\": -130,
	"<>": 10, "<|": -20, "|>": -20, "</": 10, "/>": 10, "<*": 40, "*>": 40, "<+": 30, "+>": 30,
	"<$": 40, "$>": 40, ":=": 50, "=:": 50, "<:": 50, ":>": 50, "<~": 30, "~>": 30, "~~": 40,
	"-<": 10, ">-": 10, "|-": 10, "-|": 10, "|=": 30,
	"~-": 20, "-~": 20, "_|": 0, "|_": 0,
}
CENTRED = "*:~"   # move to the hyphen's axis beside something that sits on it
ON_AXIS = "<>=-+|"
ARROWY = "<>=-|~"  # sequences of only these stay out of any longer run of them

AMPERSANDS = ("&&", "&&&")

# Characters that just close up, built from the characters themselves
SPACED = """
|| ||| :: ::: // /// .. ... >> >>> << <<< ## ### #### ;; ;;; ?? ??? !! ~~ ** *** {{ }}
:= ::= =: =:= ?: :? :?> ?. .? .= ..< ?= /= /== //= ^= &= |= ||= #= #: #! #? #( #[ #{ #_ #_( ]#
</ /> </> /* /** */ *> <* <*> +> <+ <+> $> <$ <$> <> \\/ /\\ _|_ @_ ~@ [| |] {| |} [< >]
{!! !!} =!= =/= |> <| <|> ||> <|| |||> <||| |- -| ||-
~- -~ <<~ <: :> <:< >: :< -< >- -<< >>-
""".split()

# Double chevrons whose `=` bars run into them and out to the far end
BOUND = (">>=", "=<<", "<<=", "=>>")

# Wavy arrows: which ends carry a head
WAVES = {"~>": "right", "<~": "left", "<~>": "both", "~~>": "right", "<~~": "left"}

# Comment markers: their `--` is one line, and `<` is the head of an arrow
COMMENTS = ("<!--", "<#--", "{!--", "{{--", "--}}")

# Longer arrows: (source arrow, heads, what else goes on the shaft)
ARROWS = {
	"-->": (0x2192, "right", None),
	"<--": (0x2190, "left", None),
	"<-->": (0x2194, "both", None),
	"==>": (0x21D2, "right", None),
	"<==": (0x21D0, "left", None),
	"<==>": (0x21D4, "both", None),
	"->>": (0x2192, "right", "head"),
	"<<-": (0x2190, "left", "head"),
	">->": (0x2192, "right", (">", "left")),
	"<-<": (0x2190, "left", ("<", "right")),
	">=>": (0x21D2, "right", (">", "left")),
	"<=<": (0x21D0, "left", ("<", "right")),
	"|->": (0x2192, "right", ("|", "left")),
	"<-|": (0x2190, "left", ("|", "right")),
	"|=>": (0x21D2, "right", ("|", "left")),
	"<=|": (0x21D0, "left", ("|", "right")),
}


def by_unicode(font, cp):
	return next(g for g in font.glyphs() if g.unicode == cp)


def axis(font):
	"""Vertical centre of the hyphen, where arrows in code sit."""
	_, ymin, _, ymax = by_unicode(font, 0x2D).boundingBox()
	return (ymin + ymax) / 2


def arrow(font, name, cp, cells, tips):
	"""A ligature from one of Garamond's arrows, its shaft stretched over `cells`.

	`tips` says which ends carry a head ("left", "right" or "both"). The arrow is
	moved onto the hyphen's axis and its heads keep their drawn size; only the
	shaft gets longer: only the shaft's plain end (within TAIL of it) moves, since
	in Bold the barbs of the head reach far back along the shaft.
	"""
	width = by_unicode(font, 0x41).width
	src = by_unicode(font, cp)
	layer = src.foreground.dup()
	xmin, ymin, xmax, ymax = layer.boundingBox()
	layer.transform(psMat.translate(0, axis(font) - (ymin + ymax) / 2))
	left, right = -(cells - 1) * width + MARGIN, width - MARGIN
	if tips == "right":
		# tip on the right edge; the shaft's tail moves out to the left
		layer.transform(psMat.translate(right - xmax, 0))
		cut, move, side = xmin + TAIL + right - xmax, left - (xmin + right - xmax), -1
	elif tips == "left":
		layer.transform(psMat.translate(left - xmin, 0))
		cut, move, side = xmax - TAIL + left - xmin, right - (xmax + left - xmin), 1
	else:
		# both heads: left tip on the left edge, then the right half moves out
		layer.transform(psMat.translate(left - xmin, 0))
		cut, move, side = (xmin + xmax) / 2 + left - xmin, right - (xmax + left - xmin), 1
	for c in layer:
		for p in c:
			if (p.x - cut) * side > 0:
				p.x += move
	glyph = font.createChar(-1, name)
	glyph.foreground = layer
	glyph.width = width
	glyph.round()


def equals(font, name, cp, cells, bars=2):
	"""`==`, `!=` and the like: the bars of = or ≠ span `cells`; a stroke stays as drawn.

	With `bars=3`, for `===` and `!==`, a third bar joins them and all three close up.
	"""
	width = by_unicode(font, 0x41).width
	left, right = -(cells - 1) * width + MARGIN, width - MARGIN
	layer = by_unicode(font, cp).foreground.dup()
	new = fontforge.layer()
	new.is_quadratic = layer.is_quadratic
	lines = []
	for c in layer:
		xmin, ymin, xmax, ymax = c.boundingBox()
		if ymax - ymin > 300:  # the stroke; moves to the middle of the cells
			c.transform(psMat.translate((left + right - xmin - xmax) / 2, 0))
			new += c
		else:
			mid = (xmin + xmax) / 2
			for p in c:
				p.x += left - xmin if p.x < mid else right - xmax
			lines.append(c)
	if bars == 3:
		middles = [(c.boundingBox()[1] + c.boundingBox()[3]) / 2 for c in lines]
		centre, pitch = sum(middles) / 2, abs(middles[0] - middles[1]) * PITCH
		bar = lines[0]
		lines = []
		for step in (-1, 0, 1):
			piece = bar.dup()
			piece.transform(psMat.translate(0, centre + step * pitch - middles[0]))
			lines.append(piece)
	for c in lines:
		new += c
	glyph = font.createChar(-1, name)
	glyph.foreground = new
	glyph.width = width
	glyph.round()


def comparison(font, name, cp):
	"""`<=` or `>=` from Garamond's ≤ or ≥, widened and centred across two cells."""
	layer = by_unicode(font, cp).foreground.dup()
	layer.transform(psMat.scale(WIDEN, 1))
	xmin, _, xmax, _ = layer.boundingBox()
	layer.transform(psMat.translate(-(xmin + xmax) / 2, 0))
	glyph = font.createChar(-1, name)
	glyph.foreground = layer
	glyph.width = by_unicode(font, 0x41).width
	glyph.round()


def ampersands(font, name, cells):
	"""`&&` and `&&&`: `&` as drawn, except that the wide swash & of italics is narrowed.

	The slant is taken out first so it survives, and the outer edges stay put, so
	gaps open between the ampersands without running further into their neighbours.
	"""
	width = by_unicode(font, 0x41).width
	src = by_unicode(font, 0x26).foreground
	layer = fontforge.layer()
	lean = math.radians(font.italicangle)
	squeeze = psMat.compose(psMat.compose(psMat.skew(lean), psMat.scale(SQUEEZE, 1)), psMat.skew(-lean))
	for i in range(cells):
		piece = src.dup()
		if font.italicangle:
			xmin, _, xmax, _ = piece.boundingBox()
			piece.transform(squeeze)
			left, _, right, _ = piece.boundingBox()
			spare = xmax - xmin - (right - left)
			piece.transform(psMat.translate(xmin - left + spare * i / (cells - 1), 0))
		piece.transform(psMat.translate((i - cells + 1) * width, 0))
		layer += piece
	glyph = font.createChar(-1, name)
	glyph.foreground = layer
	glyph.width = width
	glyph.round()


def outline(font, ch):
	"""A character's contours, with any references resolved."""
	glyph = by_unicode(font, ord(ch))
	layer = glyph.foreground.dup()
	for ref, matrix, *_ in glyph.references:
		piece = font[ref].foreground.dup()
		piece.transform(matrix)
		layer += piece
	return layer


def upright_box(piece, lean):
	"""A piece's bounding box with the slant taken out of whatever slants."""
	_, ymin, _, ymax = piece.boundingBox()
	upright = piece.dup()
	upright.transform(psMat.translate(0, -(ymin + ymax) / 2))
	upright.transform(psMat.skew(lean))
	return min(piece.boundingBox(), upright.boundingBox(), key=lambda box: box[2] - box[0])


def spaced(font, name, seq):
	"""A sequence whose characters only move together, as drawn.

	Gaps close to GAPS, measured with the slant taken out of whatever slants
	(italic `|` and `<` are upright), and the group stays
	centred on its cells. Characters in CENTRED join the hyphen's axis when the
	sequence also has something that sits on it, as `:` does in `:=`.
	"""
	width = by_unicode(font, 0x41).width
	lean = math.radians(font.italicangle)
	pieces, boxes = [], []
	for i, ch in enumerate(seq):
		piece = outline(font, ch)
		piece.transform(psMat.translate((i - len(seq) + 1) * width, 0))
		if ch in CENTRED and any(c in ON_AXIS for c in seq):
			_, ymin, _, ymax = piece.boundingBox()
			piece.transform(psMat.translate(0, axis(font) - (ymin + ymax) / 2))
		if ch == "|" and set(seq) <= set("<|>") and set(seq) != {"|"}:
			# the bar closes the chevron into a triangle, so it takes the chevron's height
			_, low, _, high = outline(font, next(c for c in seq if c != "|")).boundingBox()
			_, ymin, _, ymax = piece.boundingBox()
			piece.transform(psMat.translate(0, -ymin))
			piece.transform(psMat.scale(1, (high - low) / (ymax - ymin)))
			piece.transform(psMat.translate(0, low))
		if set(seq) <= set("<|>") and set(seq) != {"|"}:
			xmin, ymin, xmax, ymax = piece.boundingBox()
			piece.transform(psMat.translate(-(xmin + xmax) / 2, -(ymin + ymax) / 2))
			piece.transform(psMat.scale(TRIANGLE))
			piece.transform(psMat.translate((xmin + xmax) / 2, axis(font)))
		xmin, _, xmax, _ = upright_box(piece, lean)
		pieces.append(piece)
		boxes.append((xmin, xmax))
	centre = (boxes[0][0] + boxes[-1][1]) / 2
	moves, reach = [0], boxes[0][1]
	for i in range(1, len(seq)):
		gap = GAPS.get(seq[i - 1:i + 1], GAP)
		moves.append(min(moves[-1], reach + gap - boxes[i][0]))
		reach = boxes[i][1] + moves[-1]
	shift = centre - (boxes[0][0] + moves[0] + reach) / 2
	layer = fontforge.layer()
	for piece, move in zip(pieces, moves):
		piece.transform(psMat.translate(move + shift, 0))
		layer += piece
	glyph = font.createChar(-1, name)
	glyph.foreground = layer
	glyph.width = width
	glyph.round()


def comment(font, name, seq):
	"""`<!--`, `{{--`, `--}}` and the like: the `--` becomes one line running to the far end.

	Outer characters sit from the margin inwards, and `<` is Garamond's ← so that
	`<!--` opens with the same arrow `-->` closes with.
	"""
	width = by_unicode(font, 0x41).width
	lean = math.radians(font.italicangle)
	left, right = -(len(seq) - 1) * width + MARGIN, width - MARGIN
	closing = seq.startswith("--")
	layer = fontforge.layer()
	reach = right if closing else left
	for ch in reversed(seq[2:]) if closing else seq[:-2]:
		piece = by_unicode(font, 0x2190).foreground.dup() if ch == "<" else outline(font, ch)
		if ch == "<":
			_, ymin, _, ymax = piece.boundingBox()
			piece.transform(psMat.translate(0, axis(font) - (ymin + ymax) / 2))
		xmin, _, xmax, _ = upright_box(piece, lean)
		piece.transform(psMat.translate(reach - xmax if closing else reach - xmin, 0))
		reach = reach - (xmax - xmin) - GAP if closing else reach + (xmax - xmin) + GAP
		layer += piece
	line = outline(font, "-")
	xmin, _, xmax, _ = line.boundingBox()
	mid = (xmin + xmax) / 2
	start, end = (left, reach) if closing else (reach, right)
	for c in line:
		for p in c:
			p.x += start - xmin if p.x < mid else end - xmax
	layer += line
	glyph = font.createChar(-1, name)
	glyph.foreground = layer
	glyph.width = width
	glyph.round()


def head(font, cp):
	"""Garamond's arrowhead from → or ←, on the hyphen's axis, cut from its shaft.

	Returns the head and the x where the shaft joined it.
	"""
	contour = by_unicode(font, cp).foreground[0]
	points = list(contour)
	count = len(points)
	cuts = [i for i in range(count)
		if points[i].on_curve and points[(i + 1) % count].on_curve
		and abs(points[i].x - points[(i + 1) % count].x) > LONG]
	ends = [p.x for i in cuts for p in (points[i], points[(i + 1) % count])]
	pieces = []
	for a, b in zip(cuts, cuts[1:] + cuts[:1]):
		start = (a + 1) % count
		pieces.append([points[(start + i) % count] for i in range((b - start) % count + 1)])
	piece = max(pieces, key=lambda part: max(p.y for p in part) - min(p.y for p in part))
	cut = fontforge.contour()
	cut.is_quadratic = contour.is_quadratic
	for p in piece:
		cut += p
	cut.closed = True
	_, ymin, _, ymax = by_unicode(font, cp).foreground.boundingBox()
	cut.transform(psMat.translate(0, axis(font) - (ymin + ymax) / 2))
	return cut, max(ends) if cp == 0x2192 else min(ends)


def wavy(font, start, end, swell=None):
	"""A line of joined `~` from `start` to `end`, on the hyphen's axis, `swell` tall.

	Copies of ~ overlap where one's rising tail runs along the next one's start,
	so the wave never breaks, and they stretch slightly to fit between the ends.
	"""
	tilde = outline(font, "~")
	xmin, ymin, xmax, ymax = tilde.boundingBox()
	# the trough is in the right half; in italics the left tail can sit lower still
	lowest = min((p for c in tilde for p in c if p.on_curve and p.x > (xmin + xmax) / 2), key=lambda p: p.y)
	pitch = lowest.x - xmin
	tilde.transform(psMat.translate(-xmin, axis(font) - (ymin + ymax) / 2))
	line = fontforge.layer()
	line.is_quadratic = tilde.is_quadratic
	copies = max(1, round((end - start - (xmax - xmin) * STRIDE) / (pitch * STRIDE)) + 1)
	stretch = (end - start) / (xmax - xmin + (copies - 1) * pitch)
	for i in range(copies):
		piece = tilde.dup()
		piece.transform(psMat.translate(i * pitch, 0))
		piece.transform(psMat.translate(0, -axis(font)))
		piece.transform(psMat.scale(stretch, (swell or SWELL) / (ymax - ymin)))
		piece.transform(psMat.translate(start, axis(font)))
		line += piece
	return line


def wave(font, name, seq, tips):
	"""`~>` and the like: Garamond's arrowhead on a line of joined `~`."""
	width = by_unicode(font, 0x41).width
	left, right = -(len(seq) - 1) * width + MARGIN, width - MARGIN
	new = fontforge.layer()
	new.is_quadratic = by_unicode(font, 0x2192).foreground.is_quadratic
	start, end = left, right
	if tips in ("right", "both"):
		arrowhead, joint = head(font, 0x2192)
		xhigh = arrowhead.boundingBox()[2]
		arrowhead.transform(psMat.translate(right - xhigh, 0))
		new += arrowhead
		end = joint + right - xhigh + TUCK
	if tips in ("left", "both"):
		arrowhead, joint = head(font, 0x2190)
		xlow = arrowhead.boundingBox()[0]
		arrowhead.transform(psMat.translate(left - xlow, 0))
		new += arrowhead
		start = joint + left - xlow - TUCK
	new += wavy(font, start, end)
	glyph = font.createChar(-1, name)
	glyph.foreground = new
	glyph.width = width
	glyph.removeOverlap()
	glyph.correctDirection()
	glyph.round()


def bound(font, name, seq):
	"""`>>=`, `=<<` and the like: nested chevrons, with the bars of = running into them.

	The chevrons sit at one end and the bars run to the other, ending inside the
	nearer chevron's stroke.
	"""
	width = by_unicode(font, 0x41).width
	left, right = -(len(seq) - 1) * width + MARGIN, width - MARGIN
	bars_right = seq.endswith("=")
	ch = seq[0] if bars_right else seq[-1]
	new = fontforge.layer()
	piece = outline(font, ch)
	xmin, ymin, xmax, ymax = piece.boundingBox()
	wide, tall = xmax - xmin, ymax - ymin
	middle = [p.x for c in piece for p in c if abs(p.y - (ymin + ymax) / 2) < tall * 0.15]
	stroke = max(middle) - min(middle)  # the chevron's thickness, measured across
	piece.transform(psMat.translate(-xmin, axis(font) - (ymin + ymax) / 2))
	step = wide + GAPS[ch + ch]
	near = left + step if bars_right else right - wide - step
	for x in (left, near) if bars_right else (near, right - wide):
		chevron = piece.dup()
		chevron.transform(psMat.translate(x, 0))
		new += chevron
	bars = outline(font, "=")
	_, low, _, high = bars.boundingBox()
	offset = (high - low) / 2 - (bars[0].boundingBox()[3] - bars[0].boundingBox()[1]) / 2
	# the bars end in the middle of the chevron's stroke, so nothing shows beyond it
	back = wide * offset / (tall / 2) + stroke / 2
	join = near + wide - back if ch == ">" else near + back
	start, end = (join, right) if bars_right else (left, join)
	xmin, _, xmax, _ = bars.boundingBox()
	mid = (xmin + xmax) / 2
	for c in bars:
		for p in c:
			p.x += start - xmin if p.x < mid else end - xmax
	bars.transform(psMat.translate(0, axis(font) - (low + high) / 2))
	new += bars
	glyph = font.createChar(-1, name)
	glyph.foreground = new
	glyph.width = width
	glyph.round()


def lined(font, name, cp, cells, tips, extra):
	"""An arrow from `arrow` with something more on its shaft: `|` or `>` at one end, or a second head."""
	arrow(font, name, cp, cells, tips)
	width = by_unicode(font, 0x41).width
	left, right = -(cells - 1) * width + MARGIN, width - MARGIN
	glyph = font[name]
	layer = glyph.foreground
	if extra == "head":
		piece = by_unicode(font, cp).foreground.dup()
		xmin, ymin, xmax, ymax = piece.boundingBox()
		piece.transform(psMat.translate(0, axis(font) - (ymin + ymax) / 2))
		piece.transform(psMat.translate(right - HEAD - xmax if tips == "right" else left + HEAD - xmin, 0))
	else:
		ch, side = extra
		piece = outline(font, ch)
		xmin, ymin, xmax, ymax = piece.boundingBox()
		piece.transform(psMat.translate(0, axis(font) - (ymin + ymax) / 2))
		piece.transform(psMat.translate(left - xmin if side == "left" else right - xmax, 0))
	layer += piece
	glyph.foreground = layer
	glyph.round()


def rules(font, seq):
	"""The feature text for one ligature: when to leave it alone, then the substitution."""
	names = [by_unicode(font, ord(ch)).glyphname for ch in seq]
	liga = "_".join(names) + ".liga"
	before, after = names[0], names[-1]
	if all(ch in ARROWY for ch in seq):
		before = after = "[" + " ".join(by_unicode(font, ord(ch)).glyphname for ch in ARROWY) + "]"
	marked = " ".join(n + "'" for n in names)
	body = " ".join(n + "' lookup to_spacer" for n in names[:-1])
	end = "end_" + liga.replace(".", "_")
	return end, f"sub {names[-1]} by {liga};", (
		f"\t\tignore sub {before} {marked};\n"
		f"\t\tignore sub {marked} {after};\n"
		f"\t\tsub {body} {names[-1]}' lookup {end};\n"
	)


def add_ligatures(font):
	width = by_unicode(font, 0x41).width
	spacer = font.createChar(-1, "LIG")
	spacer.width = width
	arrow(font, "hyphen_greater.liga", 0x2192, 2, "right")
	arrow(font, "less_hyphen.liga", 0x2190, 2, "left")
	arrow(font, "less_hyphen_greater.liga", 0x2194, 3, "both")
	arrow(font, "equal_greater.liga", 0x21D2, 2, "right")
	arrow(font, "less_equal_greater.liga", 0x21D4, 3, "both")
	equals(font, "exclam_equal.liga", 0x2260, 2)
	equals(font, "exclam_equal_equal.liga", 0x2260, 3, bars=3)
	equals(font, "equal_equal.liga", 0x3D, 2)
	equals(font, "equal_equal_equal.liga", 0x3D, 3, bars=3)
	comparison(font, "less_equal.liga", 0x2264)
	comparison(font, "greater_equal.liga", 0x2265)
	name = lambda seq: "_".join(by_unicode(font, ord(ch)).glyphname for ch in seq) + ".liga"
	for seq in AMPERSANDS:
		ampersands(font, name(seq), len(seq))
	for seq in SPACED:
		spaced(font, name(seq), seq)
	for seq in COMMENTS:
		comment(font, name(seq), seq)
	for seq, tips in WAVES.items():
		wave(font, name(seq), seq, tips)
	for seq in BOUND:
		bound(font, name(seq), seq)
	for seq, (cp, tips, extra) in ARROWS.items():
		if extra:
			lined(font, name(seq), cp, len(seq), tips, extra)
		else:
			arrow(font, name(seq), cp, len(seq), tips)
	ends, joined = [], []
	for seq in sorted((*AMPERSANDS, *SPACED, *COMMENTS, *WAVES, *BOUND, *ARROWS), key=len, reverse=True):
		end, sub, rule = rules(font, seq)
		ends.append(f"lookup {end} {{\n\t{sub}\n}} {end};\n")
		joined.append(rule)
	chars = "ampersand exclam less hyphenminus equal greater".split()
	chars += [by_unicode(font, ord(ch)).glyphname for seq in (*AMPERSANDS, *SPACED, *COMMENTS, *WAVES, *BOUND, *ARROWS) for ch in seq]
	with open(FEA) as src:
		text = src.read()
	text = text.replace("@SPACERS@", " ".join(dict.fromkeys(chars)))
	text = text.replace("@ENDS@", "".join(ends)).replace("@JOINED@", "".join(joined))
	with tempfile.NamedTemporaryFile("w", suffix=".fea") as fea:
		fea.write(text)
		fea.flush()
		font.mergeFeature(fea.name)
