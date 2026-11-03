#!/usr/bin/env python3
"""Build charmap.json for the showcase page: every character, alternate and
ligature in Garamonto Code.

Usage: build_charmap.py FONT_DIR OUTPUT.json
"""
import json, sys, unicodedata
from pathlib import Path
from fontTools.ttLib import TTFont

BLOCKS = [
    (0x0000, 0x007F, "Basic Latin"), (0x0080, 0x00FF, "Latin-1 Supplement"),
    (0x0100, 0x017F, "Latin Extended-A"), (0x0180, 0x024F, "Latin Extended-B"),
    (0x0250, 0x02AF, "IPA Extensions"), (0x02B0, 0x02FF, "Spacing Modifiers"),
    (0x0300, 0x036F, "Combining Diacritics"), (0x0370, 0x03FF, "Greek"),
    (0x0400, 0x04FF, "Cyrillic"), (0x0500, 0x052F, "Cyrillic Supplement"),
    (0x1E00, 0x1EFF, "Latin Extended Additional"), (0x1F00, 0x1FFF, "Greek Extended"),
    (0x2000, 0x206F, "General Punctuation"), (0x2070, 0x209F, "Super- & Subscripts"),
    (0x20A0, 0x20CF, "Currency"), (0x2100, 0x214F, "Letterlike Symbols"),
    (0x2150, 0x218F, "Number Forms"), (0x2190, 0x21FF, "Arrows"),
    (0x2200, 0x22FF, "Math Operators"), (0x2300, 0x23FF, "Misc Technical"),
    (0x2400, 0x243F, "Control Pictures"),
    (0x2500, 0x257F, "Box Drawing"), (0x2580, 0x259F, "Block Elements"),
    (0x25A0, 0x25FF, "Geometric Shapes"), (0x2600, 0x26FF, "Misc Symbols"),
    (0x2700, 0x27BF, "Dingbats"), (0x27C0, 0x27FF, "Math Brackets & Long Arrows"),
    (0x2800, 0x28FF, "Braille Patterns"), (0x2900, 0x2BFF, "More Arrows & Math"),
    (0xE0A0, 0xE0D4, "Powerline"), (0xFB00, 0xFB4F, "Ligatures"),
]

def block(cp):
    for a, b, n in BLOCKS:
        if a <= cp <= b:
            return n
    return "Other"

def single_subs(font, tag):
    """Glyph -> alternate for single substitutions under a GSUB feature."""
    out = {}
    gsub = font["GSUB"].table
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag != tag:
            continue
        for li in fr.Feature.LookupListIndex:
            lk = gsub.LookupList.Lookup[li]
            for st in lk.SubTable:
                st = getattr(st, "ExtSubTable", st)
                if hasattr(st, "mapping"):
                    out.update(st.mapping)
    return out

d = Path(sys.argv[1])
reg = TTFont(d / "GaramontoCode.ttf")
ital = TTFont(d / "GaramontoCode-Italic.ttf")
cmap, icmap = reg.getBestCmap(), ital.getBestCmap()

def name(cp, glyph):
    return unicodedata.name(chr(cp), glyph).lower()

# More words the search finds a character by, beyond its Unicode name
ALSO = {0xA5: "yuan renminbi"}

def also(cp):
    words = ["currency"] if unicodedata.category(chr(cp)) == "Sc" else []
    return " ".join(words + [ALSO.get(cp, "")]).strip()

groups = {}
for cp in sorted(cmap.keys() | icmap.keys()):
    if unicodedata.category(chr(cp)) == "Cc":
        continue
    item = {"c": cp, "n": name(cp, cmap.get(cp) or icmap[cp])}
    if also(cp):
        item["a"] = also(cp)
    if unicodedata.category(chr(cp)) == "Mn":
        item["m"] = 1
    if cp not in cmap:
        item["i"] = 1
    groups.setdefault(block(cp), []).append(item)

# Currency signs outside the Currency block ($ ¢ £ ¤ ¥) appear there too, first
signs = [it for k, v in groups.items() if k != "Currency" for it in v if unicodedata.category(chr(it["c"])) == "Sc"]
count = sum(len(v) for v in groups.values())
groups["Currency"] = signs + groups.get("Currency", [])

# Alternates: reachable through a feature, or through the text's language
rev = {}
for cp, g in sorted(cmap.items()):
    rev.setdefault(g, cp)
alts = []
for tag, keep in (("ss01", ""), ("onum", ""), ("locl", ".bgr")):
    for src, dst in single_subs(reg, tag).items():
        if src in rev and dst.endswith(keep):
            alts.append({"c": rev[src], "f": tag, "n": f"{name(rev[src], src)} ({'Bulgarian' if keep else tag})"})
alts.sort(key=lambda a: (a["f"] == "locl", a["c"], a["f"]))

# Ligature glyphs are named after the characters they join
parts = {g: chr(cp) for cp, g in cmap.items() if cp < 0x80}
parts["hyphen"] = "-"
ligs = sorted("".join(parts[p] for p in g[:-len(".liga")].split("_"))
              for g in reg.getGlyphOrder() if g.endswith(".liga"))

order = [n for *_, n in BLOCKS] + ["Other"]
data = {"groups": [[k, groups[k]] for k in order if k in groups], "alts": alts, "ligs": ligs,
        "chars": count}
Path(sys.argv[2]).write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
print("characters:", data["chars"], "alternates:", len(alts), "ligatures:", len(ligs))
