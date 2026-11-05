+++
title = 'splicelogic'
description = 'R/Bioconductor package to obtain splicing events from sets of transcripts.'
weight = 1
tags = ['R', 'Bioconductor','alternative splicing', 'RNA-seq', 'bioinformatics']
# Custom fields used by the card + detail page (all optional):
repo = 'https://github.com/thelovelab/splicelogic'
docs = 'https://thelovelab.github.io/splicelogic/'
# Animated hex, made by scripts/make-splicelogic-icons.py. splicelogic_logo.svg
# (matrix-rain version) and splicelogic_logo.png (original still) are kept.
logo = 'splicelogic_logo_anim.svg'
details = true        # the card opens this page
# Render like a plain page (layouts/page-section.html) instead of a post list
layout = 'page-section'
# Each subfolder is an animation page (layouts/embed.html) shown as a tile
# below; `group` picks which {{< link-tiles >}} block it appears in. The
# standalone HTMLs live in static/software/splicelogic/animations/ (copied by
# scripts/sync-splicelogic-animations.sh).

[[links]]
name = 'splicelogic on GitHub'
url = 'https://github.com/thelovelab/splicelogic'
icon = 'fa-brands fa-github'
description = 'Source code and issues'
group = 'links'

[[links]]
name = 'splicelogic vignette'
url = 'https://thelovelab.github.io/splicelogic/'
icon = 'fa-solid fa-book'
description = 'Package docs and tutorial'
group = 'links'
+++

splicelogic is an R/Bioconductor package that turns sets of transcripts into discrete splicing events. Within each gene it compares two groups of transcripts, `up` and `down`, using their full exon structures, and reports each difference as a splicing event. The two groups can be any partition of the transcripts, such as novel versus annotated, or disease versus control. They can also come from a differential transcript usage (DTU) analysis, where the sign of each transcript's effect estimate decides its group.

{{< embed doc="software/splicelogic/animations/summary.mp4" poster="software/splicelogic/animations/summary-poster.jpg" aspect="16/9" title="How find_all_events() works" >}}

## Links

{{< link-tiles group="links" >}}

## How it works

Start with how the exon table is built, then see how every up and down transcript pair is compared.

{{< link-tiles group="walkthrough" >}}

## How each `find_` function works

See how each `find_` function spots its event type.

{{< link-tiles group="event" >}}
