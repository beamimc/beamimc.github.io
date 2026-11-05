# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Personal academic website (https://beamimc.github.io/) built with Hugo on top of the `hugo-coder` theme.

## Commands

```bash
bash scripts/fetch-workflows.sh   # fetch workflow HTMLs into static/ (needed before serving/building)
hugo server                       # local dev server with live reload
hugo --gc --minify                # production build into public/ (what CI runs)
hugo new content/<section>/<name>/index.md
bash scripts/sync-splicelogic-animations.sh   # copy splicelogic animation HTMLs from ../splicelogic-annimations
bash scripts/record-splicelogic-summary.sh    # record the splicelogic summary animation to MP4 (needs Chrome, Node 22+, ffmpeg)
python3 scripts/make-splicelogic-icons.py <font dir>   # regenerate splicelogic logo + tile icons (needs fontTools)
python3 scripts/make-ptbp1-cover.py   # regenerate the animated PTBP1 project cover (content/projects/ptbp1-splicelogic/cover.svg)
python3 scripts/make-splain-logo-gif.py   # regenerate the animated splain logo GIF from splain_logo.png (needs Pillow, numpy, scipy)
```

- Requires Hugo **extended** (CI pins 0.167.0) and Dart Sass. There are no tests or linters.
- Deploys automatically via [.github/workflows/hugo.yml](.github/workflows/hugo.yml) on push to `main`, on manual dispatch, and daily at 06:00 UTC (to pick up new workflow HTMLs).
- `public/`, `resources/`, and the fetched `static/projects/ptbp1-splicelogic/*_workflow.html` files are gitignored; don't commit them.

## Architecture

**Theme is vendored, not a submodule.** `themes/hugo-coder/` is committed directly. Don't edit it; override instead by placing a file at the same relative path at the repo root (Hugo's lookup order prefers root `layouts/`, `assets/`). Existing overrides:
- `assets/scss/_variables.scss` is a full copy of the theme's file. Changes: fonts (Inter body, JetBrains Mono code), slate light / navy dark colours, and the aqua-blue `$link-color` / `$link-color-dark`.
- `layouts/_partials/head/extensions.html` loads the Google web fonts (Inter, JetBrains Mono, Space Grotesk).
- `layouts/_partials/header.html` is a sticky bar: site title, the `[[menu.main]]` tabs as a pill (the current section gets `.active`), and the dark-mode toggle. The toggle keeps the id `dark-mode-toggle` because the theme's `coder.js` finds it by id. `float.html` is intentionally empty, which removes the theme's floating toggle.
- `layouts/_partials/footer.html` replaces the theme's footer (copyright from `params.since` / `params.author`, plus the rubber duck).
- `assets/css/custom.css` holds site-wide styles, loaded through `params.customCSS`.

**Homepage** (`layouts/_partials/home.html`) is a hero followed by `home/sections.html`. Almost all of its text comes from `[params]` in `hugo.toml`, not from templates:
- `home/author.html`: mono eyebrow from `params.info`, headline `params.hero.greeting` (markdown; `**bold**` gets the accent colour), `params.hero.bio`, and a typewriter line from `params.typewriter` (a string or a list of phrases).
- `home/social.html`: `[[params.social]]` as outlined buttons next to the "See my work" button. The theme's `fa-2x` is stripped from the icons. The rubber duck (`static/images/duck.svg`) is the favicon (`params.faviconSVG`) and sits in the footer.
- `home/sections.html`: numbered sections (01, 02, ...), each only if its source exists. Software: every `/software` entry, linking to its own page if `details = true`, else `docs`, else `repo`. Projects: the first 3 by weight. Experience: the first 4 entries of the first section in `data/experience.yaml`. New entries show up on the homepage automatically.

**Layout reuse via front matter**, which is the main thing you can't see from the file tree:
- `content/projects/_index.md` sets `type = 'software'`, so Projects and Software both render with the card grid in `layouts/software/list.html`. That template's CSS is inline in a `<style>` block, not in `custom.css`.
- Card fields come from each child page's front matter: `description`, `tags`, `weight` (order), `repo`, `docs`, `preprint`, `logo` (defaults to `logo.*` in the bundle), `cover` (defaults to `cover.*`, which switches the card to the wide-image variant), and `details = true` (makes the whole card link to the page).
- `layout = 'page-section'` makes a section `_index.md` render like a single page (`layouts/page-section.html`) instead of a post list.
- `layout = 'embed'` plus `doc = '<path under static/>'` renders a page that's a full-width iframe of a PDF or HTML file (`layouts/embed.html`).
- `{{< embed doc="..." aspect="16/9" >}}` puts the same frame inline in a page's text. A `.mp4`/`.webm` `doc` becomes a GIF-like video (autoplay, muted, loop, no controls; optional `poster`); anything else is an iframe.
- `{{< link-tiles >}}` (`layouts/_shortcodes/link-tiles.html`) renders the current section's child pages as tiles, followed by external `[[links]]` from front matter. A tile uses the child's `icon.*` bundle image if it has one, otherwise its Font Awesome `icon` param.

`content/projects/ptbp1-splicelogic/` uses all of these together: a `page-section` landing page with `link-tiles`, where each child is an `embed` page pointing at files in `static/projects/ptbp1-splicelogic/`. The two workflow HTMLs are downloaded from the public `beamimc/splicelogic-paper` repo by `scripts/fetch-workflows.sh`. Only the poster PDF is committed.

`content/software/splicelogic/` is the same pattern under Software. `details = true` makes its Software-page card open it. The homepage card opens it too (`home/sections.html` also honours `details`). It is a `page-section` with three `{{< link-tiles group="..." >}}` blocks (`walkthrough`, `event`, `links`): `group` filters the children and the `[[links]]` by their `group` param. Each child is an `embed` page with `aspect = '16/9'` (fixed-ratio frame) and `group` (adds previous/next links to siblings in that group). The summary animation plays inline on the landing page as a GIF-like `{{< embed >}}` video, `summary.mp4` (+ `summary-poster.jpg`). It is recorded from `../splicelogic-annimations/splicelogic-summary-standalone.html` by `scripts/record-splicelogic-summary.sh` (which uses `scripts/record-animation.mjs` to step headless Chrome frame by frame with the play bar hidden, then ffmpeg), so rerun that after changing the summary animation. The 9 animation standalones (about 1.4 MB each, committed) live in `static/software/splicelogic/animations/`. They come from the local `../splicelogic-annimations` project (not a git repo), so rerun `bash scripts/sync-splicelogic-animations.sh` after rebuilding them there.
- The animated hex logo `splicelogic_logo_anim.svg` and every child's `icon.svg` are generated by `scripts/make-splicelogic-icons.py` (pure CSS keyframes, with text converted to IBM Plex paths; it needs fontTools and the Plex TTFs, see its docstring). Edit the script and regenerate, not the SVGs. An `icon.svg` tile icon fills its slot (`.link-tile-icon-art`).

**Data-driven pages**: Experience and Talks are generated from `data/experience.yaml` and `data/talks.yaml` by `layouts/experience/list.html` and `layouts/talks/list.html`. Edit the YAML, not the markdown. Talks are sorted newest-first by each entry's `sort` field (`YYYY-MM`). `dates` is display text only, except that an Experience entry whose `dates` contains "Present" gets the `.current` class (on the page and on the homepage).

**Images**: `layouts/_partials/card-image-src.html` resizes raster card images to webp but passes GIF and SVG through unchanged, so animated logos (e.g. `splicelogic_logo.svg`) keep animating.

`markup.goldmark.renderer.unsafe = true`, so raw HTML in markdown is rendered. Top-nav tabs are defined by `[[menu.main]]` in `hugo.toml`.
