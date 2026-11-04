#!/usr/bin/env python3
"""Generate the animated splicelogic SVGs used on the site.

  content/software/splicelogic/splicelogic_logo_anim.svg   hex logo (card + homepage)
  content/software/splicelogic/<page>/icon.svg             tile icons, one per animation page

They copy the style of the explainer animations in ../splicelogic-annimations:
blue up / red down transcripts, a glowing scan line that drops from the up
transcript onto the down one, and the event lighting up in its Okabe-Ito colour.
The segment data below mirrors MINI in splicelogic-mini-events.jsx and TX in
splicelogic-events-v3.jsx; update both if the animations change.

All motion is CSS keyframes inside the SVG, so it plays when loaded with <img>.
Text is converted to paths (IBM Plex), so no web fonts are needed.

Needs fontTools and two IBM Plex TTFs (https://github.com/IBM/plex):
  python3 -m venv venv && venv/bin/pip install fonttools
  venv/bin/python scripts/make-splicelogic-icons.py <dir with IBMPlexSans-SemiBoldItalic.ttf and IBMPlexMono-Medium.ttf>
"""
import os, random, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = sys.argv[1] if len(sys.argv) > 1 else 'fonts'
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'content', 'software', 'splicelogic')
SANS = TTFont(os.path.join(FONTS, 'IBMPlexSans-SemiBoldItalic.ttf'))
MONO = TTFont(os.path.join(FONTS, 'IBMPlexMono-Medium.ttf'))

UP, DOWN = '#4C8DF6', '#E5484D'


def text_width(font, text, size):
    cmap, hmtx = font.getBestCmap(), font['hmtx']
    return sum(hmtx[cmap[ord(c)]][0] for c in text) * size / font['head'].unitsPerEm


def text_d(font, text, size, x, y, anchor='start'):
    """SVG path data for `text` with its baseline at y."""
    cmap, hmtx, gs = font.getBestCmap(), font['hmtx'], font.getGlyphSet()
    k = size / font['head'].unitsPerEm
    if anchor == 'middle':
        x -= text_width(font, text, size) / 2
    out = []
    for c in text:
        g = cmap[ord(c)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
        out.append(pen.getCommands())
        x += hmtx[g][0] * k
    return ' '.join(out)


def f(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def rpath(x0, x1, y, h, rl, rr):
    """Rectangle centred on y with rounded left corners rl and right corners rr."""
    t, b = y - h / 2, y + h / 2
    return (f'M{f(x0 + rl)} {f(t)}H{f(x1 - rr)}' + (f'A{f(rr)} {f(rr)} 0 0 1 {f(x1)} {f(t + rr)}' if rr else '')
            + f'V{f(b - rr)}' + (f'A{f(rr)} {f(rr)} 0 0 1 {f(x1 - rr)} {f(b)}' if rr else '')
            + f'H{f(x0 + rl)}' + (f'A{f(rl)} {f(rl)} 0 0 1 {f(x0)} {f(b - rl)}' if rl else '')
            + f'V{f(t + rl)}' + (f'A{f(rl)} {f(rl)} 0 0 1 {f(x0 + rl)} {f(t)}' if rl else '') + 'Z')


def segments(segs, X, y, h, r):
    """[(path, seg)] for each segment; touching segments form one exon, so only
    the outer ends of an exon are rounded."""
    out = []
    for i, s in enumerate(segs):
        first = i == 0 or segs[i - 1][1] != s[0]
        last = i == len(segs) - 1 or segs[i + 1][0] != s[1]
        out.append((rpath(X(s[0]), X(s[1]), y, h, r if first else 0, r if last else 0), s))
    return out


def kf(name, stops):
    """@keyframes from {percent: 'css declarations'}."""
    return '@keyframes %s{%s}' % (name, ''.join('%s%%{%s}' % (f(p), v) for p, v in sorted(stops.items())))


def svg(viewbox, label, css, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" role="img" aria-label="%s">\n'
            '<style>%s\n@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>\n%s\n</svg>\n'
            % (viewbox, label, css, body))


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(text)
    print('wrote', os.path.relpath(path), '(%d KB)' % (len(text) // 1024 + 1))


# ---------------------------------------------------------------- mini icons
# Same segments as MINI in splicelogic-mini-events.jsx: [start, end, unique?] on 0–1000.
MINI = {
    'atss': ('#E69F00', [[20, 120, 1], [330, 450], [600, 720], [850, 960]],
             [[170, 260, 1], [330, 450], [600, 720], [850, 960]], []),
    'a5ss': ('#0072B2', [[40, 170], [330, 450], [600, 720], [850, 960]],
             [[40, 170], [330, 450], [450, 520, 1], [600, 720], [850, 960]], [(0, 450, 520)]),
    'se': ('#D55E00', [[40, 170], [600, 720], [850, 960]],
           [[40, 170], [330, 460, 1], [600, 720], [850, 960]], [(0, 330, 460)]),
    'mxe': ('#CC79A7', [[40, 170], [280, 380, 1], [640, 740], [870, 970]],
            [[40, 170], [460, 560, 1], [640, 740], [870, 970]], [(0, 460, 560), (1, 280, 380)]),
    'a3ss': ('#56B4E9', [[40, 170], [280, 340, 1], [340, 450], [600, 720], [850, 960]],
             [[40, 170], [340, 450], [600, 720], [850, 960]], [(1, 280, 340)]),
    'ri': ('#009E73', [[40, 170], [330, 440], [440, 580, 1], [580, 700], [850, 960]],
           [[40, 170], [330, 440], [580, 700], [850, 960]], []),
    'ates': ('#E3D31F', [[40, 170], [330, 450], [600, 720], [790, 880, 1]],
             [[40, 170], [330, 450], [600, 720], [910, 990, 1]], []),
}
SHARED = '#8A919C'   # shared exons once compared (mid grey reads on light and dark tiles)

# Icon timeline, one loop of ICON_T seconds: the scan sweeps 6–46 %, it crosses
# the down lane at ~34 %, where both lanes recolour; reset at 86–95 %.
ICON_T = 4.8
SCAN_KF = kf('scan', {0: 'transform:translateY(20px);opacity:0', 6: 'opacity:1', 46: 'transform:translateY(84px);opacity:1',
                      52: 'transform:translateY(84px);opacity:0', 100: 'transform:translateY(84px);opacity:0'})


def recolour(name, a, b, at=33, peak=None):
    st = {0: f'fill:{a}', at: f'fill:{a}', at + 5: f'fill:{b}', 86: f'fill:{b}', 95: f'fill:{a}', 100: f'fill:{a}'}
    if peak:
        st[at + 2.5] = f'fill:{peak}'
    return kf(name, st)


def scan_body(x0, x1, band=16):
    return (f'<g class="scan"><rect x="{x0}" y="-{band}" width="{x1 - x0}" height="{band}" fill="url(#band)"/>'
            f'<line x1="{x0}" x2="{x1}" y1="0" y2="0" stroke="{UP}" stroke-width="1.6" stroke-linecap="round"/></g>')


BAND = (f'<linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{UP}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{UP}" stop-opacity=".28"/></linearGradient>')


def mini_icon(code, col, up, down, ghosts):
    X = lambda v: 6 + v * 0.088
    lanes = [(up, 33, UP, 'u'), (down, 66, DOWN, 'd')]
    css = [f'.scan{{animation:scan {ICON_T}s linear infinite}}',
           '.us{fill:%s;animation:us %ss infinite}.ds{fill:%s;animation:ds %ss infinite}' % (SHARED, ICON_T, SHARED, ICON_T),
           '.ue,.de{fill:%s}.ue{animation:ue %ss infinite}.de{animation:de %ss infinite}' % (col, ICON_T, ICON_T),
           f'.gh{{animation:gh {ICON_T}s infinite}}',
           SCAN_KF, recolour('us', UP, SHARED), recolour('ds', DOWN, SHARED),
           recolour('ue', UP, col, peak='#9CC0FF'), recolour('de', DOWN, col, peak='#FF9A9D'),
           kf('gh', {0: 'opacity:0', 38: 'opacity:0', 43: 'opacity:1', 84: 'opacity:1', 90: 'opacity:0', 100: 'opacity:0'})]
    body = [f'<defs>{BAND}</defs>']
    for segs, y, c, k in lanes:
        body.append(f'<line x1="{f(X(segs[0][0]))}" x2="{f(X(segs[-1][1]))}" y1="{y}" y2="{y}" stroke="{c}" stroke-width="2.6"/>')
    for lane, s, e in ghosts:
        y = lanes[lane][1]
        body.append(f'<rect class="gh" x="{f(X(s))}" y="{y - 8}" width="{f(X(e) - X(s))}" height="16" rx="4.5" '
                    f'fill="{col}" fill-opacity=".14" stroke="{col}" stroke-width="1.3" stroke-dasharray="2.6 1.8"/>')
    for segs, y, c, k in lanes:
        for d, s in segments(segs, X, y, 16, 4.5):
            body.append(f'<path class="{k}{"e" if len(s) > 2 else "s"}" d="{d}"/>')
    body.append(scan_body(4, 96))
    return svg('0 0 100 100', f'splicelogic {code.upper()} animation icon', ''.join(css), '\n'.join(body))


# ---------------------------------------------------------------- event-types icon
# TX / SEG from splicelogic-events-v3.jsx; coded segments are where events are found.
SEG = {'Fa': [0, 50, 'F'], 'Fb': [80, 130, 'F'], 'E2': [190, 250], 'X5': [250, 275, '5'], 'E3': [340, 390, 'S'],
       'Ma': [450, 490, 'M'], 'Mb': [530, 570, 'M'], 'X3': [625, 650, '3'], 'E5': [650, 710], 'IR': [710, 780, 'I'],
       'E6': [780, 830], 'La': [880, 930, 'L'], 'Lb': [960, 1000, 'L']}
EVCOL = {'F': '#E69F00', '5': '#0072B2', 'S': '#D55E00', 'M': '#CC79A7', '3': '#56B4E9', 'I': '#009E73', 'L': '#E3D31F'}
TX = [(1, ['Fa', 'E2', 'Ma', 'E5', 'E6', 'La']), (1, ['Fb', 'E2', 'Ma', 'X3', 'E5', 'IR', 'E6', 'Lb']),
      (0, ['Fb', 'E2', 'E3', 'Ma', 'E5', 'IR', 'E6', 'Lb']), (0, ['Fb', 'E2', 'X5', 'Mb', 'E5', 'E6', 'Lb'])]


def events_icon():
    X = lambda v: 7 + v * 0.086
    ys = [22, 39, 61, 78]
    css = [f'.scan{{animation:scan {ICON_T}s linear infinite}}', SCAN_KF,
           '.us{fill:%s;animation:us %ss infinite}.ds{fill:%s;animation:ds %ss infinite}' % (SHARED, ICON_T, SHARED, ICON_T),
           recolour('us', UP, SHARED, at=38), recolour('ds', DOWN, SHARED, at=38)]
    for code, col in EVCOL.items():
        n = 'e' + ('n%s' % code if code.isdigit() else code)
        css.append('.%su{fill:%s;animation:%su %ss infinite}.%sd{fill:%s;animation:%sd %ss infinite}'
                   % (n, col, n, ICON_T, n, col, n, ICON_T))
        css.append(recolour(n + 'u', UP, col, at=38) + recolour(n + 'd', DOWN, col, at=38))
    body = [f'<defs>{BAND}</defs>']
    for (isup, names), y in zip(TX, ys):
        segs = sorted([SEG[n] for n in names])
        c, k = (UP, 'u') if isup else (DOWN, 'd')
        body.append(f'<line x1="{f(X(segs[0][0]))}" x2="{f(X(segs[-1][1]))}" y1="{y}" y2="{y}" stroke="{c}" stroke-width="2"/>')
        for d, s in segments(segs, X, y, 12, 3.2):
            cls = ('e' + ('n%s' % s[2] if s[2].isdigit() else s[2]) + k) if len(s) > 2 else k + 's'
            body.append(f'<path class="{cls}" d="{d}"/>')
    body.append(scan_body(4, 96, band=14))
    return svg('0 0 100 100', 'splicelogic event types animation icon', ''.join(css), '\n'.join(body))


# ---------------------------------------------------------------- prepare-exons icon
def prepare_icon():
    """exonsBy(txdb) list (two grey transcripts) unlists into one exon per row,
    then gene_id / tx_id / coefficient join on and the rows turn blue / red."""
    T = 6.0
    grey = '#9AA1AB'
    tx = [(17, [(10, 26), (38, 52), (66, 88)], UP), (31, [(10, 24), (46, 62)], DOWN)]
    css, body = [], []
    rows = [(y, s, e, c) for y, ex, c in tx for s, e in ex]
    for i, (y, s, e, c) in enumerate(rows):
        ry = 49 + i * 10
        dx, dy = 10 - s, ry - y
        a = 10 + i * 6
        css.append(kf(f'm{i}', {0: 'transform:translate(0,0);opacity:0;fill:' + grey, 5: 'opacity:1',
                                a: 'transform:translate(0,0);fill:' + grey,
                                a + 13: f'transform:translate({dx}px,{dy}px);fill:{grey}',
                                60: f'fill:{grey}', 66: f'fill:{c}',
                                86: f'transform:translate({dx}px,{dy}px);opacity:1;fill:{c}',
                                93: f'transform:translate({dx}px,{dy}px);opacity:0;fill:{c}',
                                94: 'transform:translate(0,0);opacity:0', 100: 'transform:translate(0,0);opacity:0'}))
        css.append(f'.m{i}{{transform:translate({dx}px,{dy}px);animation:m{i} {T}s cubic-bezier(.65,0,.35,1) infinite}}')  # static = table
        body.append(f'<path class="m{i}" fill="{c}" d="{rpath(s, e, y, 7, 2, 2)}"/>')
        # joined columns: gene_id, tx_id (grey) and the coefficient (lane colour)
        b = 50 + i * 1.5
        css.append(kf(f'c{i}', {0: 'opacity:0', b: 'opacity:0', b + 5: 'opacity:1', 86: 'opacity:1', 93: 'opacity:0', 100: 'opacity:0'}))
        css.append(f'.c{i}{{animation:c{i} {T}s infinite}}')
        body.append(f'<g class="c{i}"><path fill="{grey}" fill-opacity=".55" d="{rpath(40, 54, ry, 5, 2.5, 2.5)} {rpath(57, 68, ry, 5, 2.5, 2.5)}"/>'
                    f'<path fill="{c}" d="{rpath(72, 90, ry, 5, 2.5, 2.5)}"/></g>')
    # list brackets around the source transcripts, and a header rule for the table
    css.append(kf('lst', {0: 'opacity:0', 5: 'opacity:.8', 40: 'opacity:.8', 50: 'opacity:0', 100: 'opacity:0'}) + f'.lst{{opacity:0;animation:lst {T}s infinite}}')
    css.append(kf('tab', {0: 'opacity:0', 12: 'opacity:0', 20: 'opacity:.8', 86: 'opacity:.8', 93: 'opacity:0', 100: 'opacity:0'}) + f'.tab{{animation:tab {T}s infinite}}')
    body.insert(0, f'<g class="lst" fill="none" stroke="{grey}" stroke-width="1.4" stroke-linecap="round">'
                   f'<line x1="10" x2="88" y1="{f(17)}" y2="17" stroke-width="1" stroke-dasharray="1 2.5"/>'
                   f'<line x1="10" x2="62" y1="31" y2="31" stroke-width="1" stroke-dasharray="1 2.5"/>'
                   f'<path d="M6 9 H4 V39 H6 M94 9 H96 V39 H94"/></g>'
                   f'<line class="tab" x1="6" x2="94" y1="42.5" y2="42.5" stroke="{grey}" stroke-width="1.2"/>')
    return svg('0 0 100 100', 'splicelogic prepare exons animation icon', ''.join(css), '\n'.join(body))


# ---------------------------------------------------------------- hex logo
def logo():
    random.seed(7)
    L = 7.0                              # seconds per loop
    HEX = '300,0 600,174 600,523 300,697 0,523 0,174'
    INNER = '300,22 581,185 581,512 300,675 19,512 19,185'
    X = lambda v: 70 + v * 0.46
    up = [[40, 190], [560, 700], [830, 960]]
    down = [[40, 190], [330, 450, 1], [560, 700], [830, 960]]
    Y1, Y2, EH = 214, 308, 38
    SLATE = '#5D6879'
    EVC = '#F57A22'                      # SE orange (#D55E00) lifted for a dark ground

    # matrix rain: columns of A/C/G/T that fall forever, each with a bright head.
    STEP, N = 31, 24
    H = STEP * N
    glyphs = ''.join(f'<path id="g{c}" d="{text_d(MONO, c, 23, 0, 8, "middle")}"/>' for c in 'ACGT')
    cols, rain, rain_css = [], [], []
    for j in range(4):
        # opacity ramps up the column to a bright head at the bottom
        letters = ''.join(f'<use href="#g{random.choice("ACGT")}" y="{i * STEP}" '
                          + (f'fill="#D6E5FF"/>' if i == N - 1 else
                             f'fill="{UP}" opacity="{f((0.06 + 0.6 * (i / N) ** 2) * random.choice([1, 1, .6]))}"/>')
                          for i in range(N) if i == N - 1 or random.random() > 0.12)
        cols.append(f'<g id="col{j}">{letters}</g>')
    for i in range(14):
        x = 38 + i * 40.5
        dur = random.uniform(9, 16)
        rain.append(f'<g transform="translate({f(x)} 0)"><g class="rn" style="animation-duration:{f(dur)}s;'
                    f'animation-delay:-{f(random.uniform(0, dur))}s" opacity="{f(random.uniform(.45, .85))}">'
                    f'<use href="#col{i % 4}" y="{-H}"/><use href="#col{(i + 1) % 4}"/></g></g>')
    rain_css.append(kf('rn', {0: f'transform:translateY(0)', 100: f'transform:translateY({H}px)'}) + '.rn{animation:rn linear infinite}')

    # scan line: 6 % at y=150, 46 % at y=372; crosses tx1 at ~17 %, tx2 at ~34 %
    def scan_y(p):
        return 150 + (p - 6) / 40 * 222
    css = rain_css + [
        kf('scan', {0: 'transform:translateY(150px);opacity:0', 6: 'transform:translateY(150px);opacity:1',
                    46: 'transform:translateY(372px);opacity:1', 52: 'transform:translateY(372px);opacity:0',
                    100: 'transform:translateY(372px);opacity:0'}) + f'.scan{{animation:scan {L}s linear infinite}}',
        # the guides are revealed down to the scan line, and stay until the reset
        kf('reveal', {0: 'transform:translateY(150px)', 6: 'transform:translateY(150px)', 46: 'transform:translateY(372px)',
                      100: 'transform:translateY(372px)'}) + f'.rv{{animation:reveal {L}s linear infinite}}',
        kf('gd', {0: 'opacity:1', 84: 'opacity:1', 90: 'opacity:0', 99.9: 'opacity:0', 100: 'opacity:1'}) + f'.gd{{animation:gd {L}s infinite}}',
        kf('us', {0: f'fill:{UP}', 15: f'fill:{UP}', 18: 'fill:#A9C8FF', 22: f'fill:{UP}', 33: f'fill:{UP}', 38: f'fill:{SLATE}',
                  86: f'fill:{SLATE}', 94: f'fill:{UP}', 100: f'fill:{UP}'}) + f'.us{{fill:{SLATE};animation:us {L}s infinite}}',
        kf('ds', {0: f'fill:{DOWN}', 32: f'fill:{DOWN}', 35: 'fill:#FFA3A5', 39: f'fill:{SLATE}',
                  86: f'fill:{SLATE}', 94: f'fill:{DOWN}', 100: f'fill:{DOWN}'}) + f'.ds{{fill:{SLATE};animation:ds {L}s infinite}}',
        kf('de', {0: f'fill:{DOWN}', 32: f'fill:{DOWN}', 35: 'fill:#FFA3A5', 39: f'fill:{EVC}',
                  86: f'fill:{EVC}', 94: f'fill:{DOWN}', 100: f'fill:{DOWN}'}) + f'.de{{fill:{EVC};animation:de {L}s infinite}}',
        kf('glow', {0: 'opacity:0', 36: 'opacity:0', 41: 'opacity:1', 50: 'opacity:.55', 84: 'opacity:.55', 92: 'opacity:0', 100: 'opacity:0'})
        + f'.glow{{opacity:.55;animation:glow {L}s infinite}}',
        kf('gh', {0: 'opacity:0', 39: 'opacity:0', 44: 'opacity:1', 84: 'opacity:1', 90: 'opacity:0', 100: 'opacity:0'}) + f'.gh{{animation:gh {L}s infinite}}',
        kf('chip', {0: 'opacity:0;transform:scale(.6)', 43: 'opacity:0;transform:scale(.6)', 47: 'opacity:1;transform:scale(1.08)',
                    50: 'transform:scale(1)', 84: 'opacity:1;transform:scale(1)', 90: 'opacity:0;transform:scale(1)',
                    100: 'opacity:0;transform:scale(.6)'})
        + f'.chip{{transform-box:fill-box;transform-origin:center;animation:chip {L}s infinite}}',
        kf('blink', {0: 'opacity:1', 49.9: 'opacity:1', 50: 'opacity:0', 100: 'opacity:0'}) + '.cur{animation:blink 1.1s steps(1) infinite}',
    ]
    d = []
    d.append('<defs>'
             f'<clipPath id="hex"><polygon points="{INNER}"/></clipPath>'
             '<clipPath id="above"><rect class="rv" x="0" y="-700" width="600" height="700"/></clipPath>'
             '<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22D3EE"/>'
             f'<stop offset=".5" stop-color="{UP}"/><stop offset="1" stop-color="{DOWN}"/></linearGradient>'
             '<radialGradient id="bg" cx=".5" cy=".42" r=".65"><stop offset="0" stop-color="#18202C"/>'
             '<stop offset="1" stop-color="#07090D"/></radialGradient>'
             '<radialGradient id="hush" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#07090D" stop-opacity=".92"/>'
             '<stop offset=".7" stop-color="#07090D" stop-opacity=".7"/><stop offset="1" stop-color="#07090D" stop-opacity="0"/></radialGradient>'
             f'<linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{UP}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{UP}" stop-opacity=".32"/></linearGradient>'
             '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>'
             f'{glyphs}{"".join(cols)}</defs>')
    d.append(f'<polygon points="{HEX}" fill="url(#rim)"/>')
    d.append(f'<polygon points="{INNER}" fill="url(#bg)"/>')
    d.append('<g clip-path="url(#hex)">')
    d.append('<g>' + ''.join(rain) + '</g>')
    # quiet zones behind the transcripts and the wordmark so they read over the rain
    d.append('<ellipse cx="300" cy="262" rx="290" ry="105" fill="url(#hush)"/>')
    d.append('<ellipse cx="300" cy="490" rx="270" ry="95" fill="url(#hush)"/>')

    # guides: tx1's inner flank boundaries (E1 end, E3 start) carried down
    d.append(f'<g class="gd" clip-path="url(#above)" stroke="{EVC}" stroke-width="2.5" stroke-dasharray="7 6" opacity=".9">'
             f'<line x1="{f(X(190))}" x2="{f(X(190))}" y1="{Y1 + EH / 2}" y2="{Y2 + EH / 2 + 14}"/>'
             f'<line x1="{f(X(560))}" x2="{f(X(560))}" y1="{Y1 + EH / 2}" y2="{Y2 + EH / 2 + 14}"/></g>')
    for segs, y, c in ((up, Y1, UP), (down, Y2, DOWN)):
        d.append(f'<line x1="{f(X(segs[0][0]))}" x2="{f(X(segs[-1][1]))}" y1="{y}" y2="{y}" stroke="{c}" stroke-width="5" stroke-linecap="round"/>')
    # the skipped exon: dashed ghost on tx1, glow under tx2's exon
    gx0, gx1 = X(330), X(450)
    d.append(f'<rect class="gh" x="{f(gx0)}" y="{Y1 - EH / 2}" width="{f(gx1 - gx0)}" height="{EH}" rx="11" fill="{EVC}" fill-opacity=".14" '
             f'stroke="{EVC}" stroke-width="3" stroke-dasharray="8 6"/>')
    d.append(f'<rect class="glow" x="{f(gx0)}" y="{Y2 - EH / 2}" width="{f(gx1 - gx0)}" height="{EH}" rx="11" fill="{EVC}" filter="url(#blur)"/>')
    for segs, y, k in ((up, Y1, 'u'), (down, Y2, 'd')):
        for p, s in segments(segs, X, y, EH, 11):
            d.append(f'<path class="{k}{"e" if len(s) > 2 else "s"}" d="{p}"/>')
    # the event chip under the exon, as in the animations
    cx, cy = (gx0 + gx1) / 2, Y2 + EH / 2 + 32
    d.append(f'<g class="chip"><rect x="{f(cx - 40)}" y="{f(cy - 17)}" width="80" height="34" rx="17" fill="#2A1A10" stroke="{EVC}" stroke-width="2"/>'
             f'<circle cx="{f(cx - 19)}" cy="{f(cy)}" r="5.5" fill="{EVC}"/>'
             f'<path fill="#FFE3CF" d="{text_d(MONO, "SE", 22, cx + 8, cy + 8, "middle")}"/></g>')
    # scan line
    d.append(f'<g class="scan"><rect x="19" y="-70" width="562" height="70" fill="url(#band)"/>'
             f'<line x1="19" x2="581" y1="0" y2="0" stroke="{UP}" stroke-width="8" opacity=".5" filter="url(#blur)"/>'
             '<line x1="19" x2="581" y1="0" y2="0" stroke="#A9C8FF" stroke-width="2.5"/></g>')

    # wordmark, fitted to the hex
    size = 84
    w = text_width(SANS, 'splicelogic', size)
    size *= min(1, 452 / w)
    d.append(f'<path fill="#F4F6F8" d="{text_d(SANS, "splicelogic", size, 300, 492, "middle")}"/>')
    # code pill, like the code box in the animations
    code, cs = 'find_all_events(gr)', 21
    pw = text_width(MONO, '> ' + code, cs) + 48
    px = 300 - pw / 2
    tx0 = px + 22
    d.append(f'<rect x="{f(px)}" y="528" width="{f(pw)}" height="44" rx="12" fill="#0B0F15" stroke="#2A3343" stroke-width="2"/>')
    d.append(f'<path fill="#6B7686" d="{text_d(MONO, ">", cs, tx0, 557)}"/>')
    t1 = tx0 + text_width(MONO, '> ', cs)
    d.append(f'<path fill="#EEF2F6" d="{text_d(MONO, "find_all_events", cs, t1, 557)}"/>')
    t2 = t1 + text_width(MONO, 'find_all_events', cs)
    d.append(f'<path fill="#9AA4B2" d="{text_d(MONO, "(gr)", cs, t2, 557)}"/>')
    t3 = t2 + text_width(MONO, '(gr)', cs) + 3
    d.append(f'<rect class="cur" x="{f(t3)}" y="537" width="4" height="26" rx="1" fill="{UP}"/>')
    d.append('</g>')
    return svg('0 0 600 697', 'splicelogic logo', ''.join(css), '\n'.join(d))


write('splicelogic_logo_anim.svg', logo())
write('prepare-exons/icon.svg', prepare_icon())
write('event-types/icon.svg', events_icon())
for code, (col, up, down, ghosts) in MINI.items():
    write(f'{code}/icon.svg', mini_icon(code, col, up, down, ghosts))
