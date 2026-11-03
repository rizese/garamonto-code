Garamonto Code
==============

Garamonto Code is a monospace serif based off Garamond meant for coding.

Weights: Regular, Medium and Bold, each with an italic.

- 150 coding ligatures through `calt`, each exactly as wide as the characters it
  replaces. Apps that turn ligatures off show the plain characters.
- Arrows built from Garamond's own.
- A dotted zero. `ss01` switches to a plain zero, an alternate `l` and an
  alternate hyphen.
- Old-style figures through `onum`.

[Download the fonts](https://github.com/rizese/garamonto-code/releases/latest/download/GaramontoCode.zip)
or see them at [rizese.github.io/garamonto-code](https://rizese.github.io/garamonto-code/).

- `fonts/ttf/` is for your editor and terminal.
- `fonts/webfonts/` is for the web.
- `source/` holds the FontForge sources and the scripts that build the fonts.

Building
--------

On macOS, with [Homebrew](https://brew.sh):

```sh
brew install fontforge ttfautohint
make
```

`make` rebuilds the fonts in `fonts/` from the `.sfd` files, adding the
ligatures, the hinting and the Medium weights. The first time, it also sets up
the Python environment the build uses, in `.venv`. `make site` rebuilds the
character list on the showcase page.

Any change to `fonts/` pushed to `main` makes a new release, with
`fonts/ttf/` and `fonts/webfonts/` zipped up for download.

This font is licensed under the [SIL Open Font License](OFL.txt).

<details>
<summary><sub>The 485 characters still copied from JetBrains Mono</sub></summary>

<sub>Box drawing, block elements, Powerline and many math and technical symbols
come from [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono). The
boxes of `⍇ ⍈ ⍐ ⍗` are JetBrains Mono's too, around our own arrows.</sub>

- Mathematical operators: `∁∅∈∉∊∋∌∎∓∘∣∤∥∧∨∩∪∴∵∶∷∸∹∼∾≃≅≇≉≋≍≔≗≟≡≢≣≪≫≬≭≮≯≰≱≲≳≺≻≼⊂⊃⊄⊅⊆⊇⊈⊉⊎⊏⊐⊑⊒⊓⊔⊕⊖⊗⊘⊙⊛⊜⊝⊞⊟⊠⊡⊢⊣⊤⊥⊴⊸⊻⊼⊽⋂⋃⋄⋆⋈⋉⋊⋎⋐⋢⋮⋯⋰⋱`
- Technical: `⌂⌃⌄⌅⌈⌉⌊⌋⌘⌜⌝⌞⌟⌤⌥⌦⌨⌫⌶⌷⌸⌹⌺⌻⌼⌽⌾⌿⍀⍁⍂⍃⍄⍅⍆⍉⍊⍋⍌⍍⍎⍏⍑⍒⍓⍔⍕⍖⍘⍙⍚⍛⍜⍝⍞⍟⍠⍡⍢⍣⍤⍥⍦⍧⍨⍩⍪⍫⍬⍭⍮⍯⍰⍱⍲⍳⍴⍵⍶⍷⍸⍹⍺⎉⎊⎋⎕⎛⎜⎝⎞⎟⎠⎡⎢⎣⎤⎥⎦⎧⎨⎩⎪⎫⎬⎭⏎⏻⏼⏽⏾`
- Control pictures: `␀␁␂␃␄␅␆␇␈␉␊␋␌␍␎␏␐␑␒␓␔␕␖␗␘␙␚␛␜␝␞␟␠␡␣␤`
- Box drawing: all of U+2500–257F
- Block elements: all of U+2580–259F
- Geometric shapes: `■□▪▫▲△▴▵▶▷▸▹►▻▼▽▾▿◀◁◂◃◄◅◆◇◈◉◊○◌◎●◔◕◦◧◨◩◪◫◯◶`
- Symbols and dingbats: `♭♯⚇⚠⚡✓✕✗✶❮❯❰❱⭘`
- Math brackets and operators: `⟅⟆⟜⟦⟧⟨⟩⟪⟫⦇⦈⨀⨅⨆`
- Powerline: U+E0A0–E0A2 and U+E0B0–E0B3

</details>
