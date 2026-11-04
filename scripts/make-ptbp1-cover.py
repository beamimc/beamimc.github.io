#!/usr/bin/env python3
"""Generate the animated cover for the PTBP1 project card.

  content/projects/ptbp1-splicelogic/cover.svg

A simplified version of the nucleotide-composition figure (fraction of A/C/G/U
around the 3'ss and 5'ss of skipped exons). The loop:
  1. the four SE (signal) lines draw left to right together
  2. the four non-SE (background) lines draw over them, thinner and fainter
  3. A and G dim; the SE vs non-SE gaps for C and U upstream of the 3'ss light up
  4. hold, fade out, repeat

The values are read by eye from the poster figure; they only need to look right.
All motion is CSS keyframes inside the SVG, so it plays when loaded with <img>.
Pure stdlib:  python3 scripts/make-ptbp1-cover.py
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                   'content', 'projects', 'ptbp1-splicelogic', 'cover.svg')

COLORS = {'A': '#4F7FE8', 'C': '#E0575B', 'G': '#4FA874', 'U': '#E8B83A'}
ORDER = ['A', 'C', 'G', 'U']

# 19 points per side: upstream -95..-5, downstream +5..+95 (step 5 nt)
SE = {
    'up': {
        'U': [.34, .335, .345, .345, .34, .35, .375, .375, .37, .39, .395, .38, .385, .39, .40, .43, .46, .47, .345],
        'C': [.215, .235, .225, .21, .21, .205, .205, .205, .205, .215, .24, .25, .245, .25, .26, .275, .28, .30, .255],
        'A': [.24, .235, .23, .23, .24, .24, .225, .235, .25, .225, .205, .215, .215, .215, .21, .18, .14, .12, .22],
        'G': [.205, .195, .205, .215, .21, .205, .20, .19, .175, .17, .16, .155, .155, .145, .125, .115, .115, .11, .175],
    },
    'down': {
        'U': [.305, .34, .35, .355, .345, .34, .335, .33, .33, .32, .30, .30, .31, .32, .32, .31, .32, .32, .31],
        'A': [.27, .25, .23, .22, .225, .235, .245, .25, .245, .245, .26, .26, .26, .26, .255, .265, .26, .25, .26],
        'C': [.13, .22, .225, .22, .215, .21, .20, .20, .21, .21, .22, .225, .21, .205, .205, .20, .205, .215, .225],
        'G': [.30, .195, .195, .215, .21, .205, .21, .215, .215, .22, .225, .215, .22, .215, .22, .225, .215, .21, .205],
    },
}
BG = {
    'up': {
        'U': [.315, .32, .325, .33, .32, .32, .32, .32, .32, .32, .325, .345, .34, .345, .365, .42, .485, .515, .39],
        'A': [.29, .27, .265, .275, .285, .29, .285, .28, .275, .275, .265, .25, .26, .27, .28, .245, .165, .12, .195],
        'C': [.19, .19, .18, .175, .185, .185, .17, .17, .175, .165, .18, .195, .20, .205, .19, .195, .23, .255, .245],
        'G': [.21, .22, .23, .225, .21, .205, .215, .225, .23, .235, .225, .21, .20, .185, .17, .145, .125, .11, .17],
    },
    'down': {
        'U': [.31, .355, .34, .33, .335, .34, .33, .325, .315, .325, .33, .33, .34, .345, .345, .335, .34, .34, .345],
        'A': [.265, .245, .25, .255, .24, .24, .245, .255, .26, .265, .27, .275, .275, .265, .26, .26, .26, .27, .27],
        'C': [.115, .20, .20, .20, .195, .185, .19, .195, .205, .20, .185, .175, .195, .20, .19, .185, .18, .19, .195],
        'G': [.31, .205, .21, .22, .235, .235, .235, .23, .22, .215, .215, .215, .195, .19, .20, .215, .22, .21, .195],
    },
}

# Geometry (viewBox 400 x 300)
W, H = 400, 300
UP_X = (22, 182)        # upstream intron panel
EX_X = (190, 210)       # exon bar
DN_X = (218, 378)       # downstream intron panel
Y_TOP, Y_BOT = 52, 258  # plot area
Y_MIN, Y_MAX = 0.08, 0.53

# Timeline (seconds)
T = 10.0
SIG_START, SIG_DUR = 0.3, 1.3   # signal lines, all four at once
BG_START, BG_DUR = 2.2, 1.3     # background lines, drawn on top
HI_START, HI_DUR = 4.2, 0.6     # dim A/G, highlight C and U
OUT_START, OUT_DUR = 8.9, 0.6   # fade everything out
HIGHLIGHT = ('C', 'U')


def pct(t):
    return f'{100 * t / T:.2f}%'


def xs(panel):
    x0, x1 = UP_X if panel == 'up' else DN_X
    return [x0 + (x1 - x0) * i / 18 for i in range(19)]


def y(v):
    return Y_BOT - (v - Y_MIN) / (Y_MAX - Y_MIN) * (Y_BOT - Y_TOP)


def pts(panel, vals):
    return ' '.join(f'{x:.1f},{y(v):.1f}' for x, v in zip(xs(panel), vals))


def line_path(data, nt):
    """Both panels in one path, so a pathLength=1 dash draws them left to right."""
    return f'M{pts("up", data["up"][nt])} M{pts("down", data["down"][nt])}'


def draw_keyframes(name, start, dur):
    return (f'@keyframes {name}{{0%,{pct(start)}{{stroke-dashoffset:1;opacity:1}}'
            f'{pct(start + dur)},{pct(OUT_START)}{{stroke-dashoffset:0;opacity:1}}'
            f'{pct(OUT_START + OUT_DUR)},100%{{stroke-dashoffset:0;opacity:0}}}}')


def fade_keyframes(name, start, dur, peak=1):
    return (f'@keyframes {name}{{0%,{pct(start)}{{opacity:0}}'
            f'{pct(start + dur)},{pct(OUT_START)}{{opacity:{peak}}}'
            f'{pct(OUT_START + OUT_DUR)},100%{{opacity:0}}}}')


css = [
    'text{font-family:Inter,"Helvetica Neue",Helvetica,Arial,sans-serif;fill:#5b6473}',
    '.ax{font-size:13px;text-anchor:middle}',
    '.lg{font-size:15px;font-weight:600;fill:#2b3340}',
    '.sig,.bg{fill:none;stroke-linejoin:round;stroke-linecap:round;stroke-dasharray:1 1;stroke-dashoffset:1}',
    '.sig{stroke-width:3}',
    '.bg{stroke-width:1.6;stroke-opacity:.5}',
    draw_keyframes('drawsig', SIG_START, SIG_DUR),
    draw_keyframes('drawbg', BG_START, BG_DUR),
    f'.sig{{animation:drawsig {T}s linear infinite}}',
    f'.bg{{animation:drawbg {T}s linear infinite}}',
    f'.dim{{animation:dim {T}s linear infinite}}',
    f'@keyframes dim{{0%,{pct(HI_START)}{{opacity:1}}{pct(HI_START + HI_DUR)},100%{{opacity:.18}}}}',
    fade_keyframes('legin', SIG_START, 0.4),
    f'.leg{{opacity:0;animation:legin {T}s linear infinite}}',
    fade_keyframes('key', BG_START, 0.5),
    f'.key{{opacity:0;animation:key {T}s linear infinite}}',
    fade_keyframes('call', HI_START + 0.2, HI_DUR),
    f'.call{{opacity:0;animation:call {T}s linear infinite}}',
    f'.band{{opacity:0;animation:band {T}s linear infinite}}',
    f'@keyframes band{{0%,{pct(HI_START)}{{opacity:0}}{pct(HI_START + HI_DUR)}{{opacity:.5}}'
    f'{pct(HI_START + 1.6)}{{opacity:.25}}{pct(HI_START + 2.6)}{{opacity:.5}}{pct(HI_START + 3.6)}{{opacity:.3}}'
    f'{pct(OUT_START)}{{opacity:.4}}{pct(OUT_START + OUT_DUR)},100%{{opacity:0}}}}',
]
body = []

# Grid + axes
for v in (0.2, 0.3, 0.4, 0.5):
    for x0, x1 in (UP_X, DN_X):
        body.append(f'<line x1="{x0}" x2="{x1}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#e3e6eb" stroke-width="1"/>')
body.append(f'<rect x="{EX_X[0]}" y="{Y_TOP - 6}" width="{EX_X[1] - EX_X[0]}" height="{Y_BOT - Y_TOP + 12}" rx="3" fill="#c4c8ce"/>')
lab_y = Y_BOT + 26
body.append(f'<text class="ax" x="{UP_X[0] + 20}" y="{lab_y}">−90</text>')
body.append(f'<text class="ax" x="{UP_X[1]}" y="{lab_y}" style="text-anchor:end">3\'ss</text>')
body.append(f'<text class="ax" x="{DN_X[0]}" y="{lab_y}" style="text-anchor:start">5\'ss</text>')
body.append(f'<text class="ax" x="{DN_X[1] - 20}" y="{lab_y}">+90</text>')

# Highlight bands: gap between SE and non-SE upstream of the 3'ss, for C and U
x_up = xs('up')
for nt in HIGHLIGHT:
    top = [f'{x:.1f},{y(v):.1f}' for x, v in zip(x_up, SE['up'][nt])]
    bot = [f'{x:.1f},{y(v):.1f}' for x, v in zip(x_up, BG['up'][nt])][::-1]
    body.append(f'<polygon class="band" points="{" ".join(top + bot)}" fill="{COLORS[nt]}"/>')


def lines(data, cls):
    """All four lines of one set; the ones not highlighted sit in a group that dims."""
    out = []
    for nt in ORDER:
        p = f'<path class="{cls}" stroke="{COLORS[nt]}" pathLength="1" d="{line_path(data, nt)}"/>'
        out.append(p if nt in HIGHLIGHT else f'<g class="dim">{p}</g>')
    return ''.join(out)


body.append(lines(SE, 'sig'))
body.append(lines(BG, 'bg'))  # after the signal, so the background draws on top

# Legend
lx = 98
body.append('<g class="leg">')
for nt in ORDER:
    body.append(f'<line x1="{lx}" x2="{lx + 20}" y1="22" y2="22" stroke="{COLORS[nt]}" '
                f'stroke-width="3.5" stroke-linecap="round"/><text class="lg" x="{lx + 27}" y="27">{nt}</text>')
    lx += 56
body.append('</g>')

# Key (appears with the background) + callout (appears with the highlight)
ky = Y_TOP + 4
body.append(f'<g class="key"><line x1="{DN_X[1] - 118}" x2="{DN_X[1] - 102}" y1="{ky}" y2="{ky}" stroke="#2b3340" stroke-width="3"/>'
            f'<text x="{DN_X[1] - 97}" y="{ky + 4}" style="font-size:12px">SE</text>'
            f'<line x1="{DN_X[1] - 70}" x2="{DN_X[1] - 54}" y1="{ky}" y2="{ky}" stroke="#2b3340" stroke-width="1.6" stroke-opacity=".5"/>'
            f'<text x="{DN_X[1] - 49}" y="{ky + 4}" style="font-size:12px">non-SE</text></g>')
cx, cy = x_up[8], y(max(SE['up']['U'])) + 2
body.append(f'<text class="call" x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" style="font-size:14px;font-weight:700">'
            f'<tspan fill="{COLORS["C"]}">C</tspan><tspan fill="{COLORS["U"]}">U</tspan>'
            f'<tspan fill="#2b3340">-rich ↑</tspan></text>')

# Without motion, show the final highlighted frame
css.append('@media (prefers-reduced-motion:reduce){*{animation:none!important}'
           '.sig,.bg{stroke-dashoffset:0}.leg,.key,.call{opacity:1}.band{opacity:.45}.dim{opacity:.18}}')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<style>{"".join(css)}</style>'
       f'<rect width="{W}" height="{H}" fill="#fff"/>'
       + ''.join(body) + '</svg>\n')

with open(OUT, 'w') as f:
    f.write(svg)
print(f'wrote {os.path.relpath(OUT)} ({len(svg) / 1024:.1f} KB)')
