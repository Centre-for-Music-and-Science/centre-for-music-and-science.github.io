---
title: "Machine learning of artistic fingerprints in jazz"
date: 2026-04-10
draft: false
url: "/jazz-piano-fingerprints-ml"
_build:
  list: never
sitemap:
  exclude: true
---

This page hosts online resources for the paper “Machine learning of artistic fingerprints in jazz” by Huw Cheston, Reuben Bance, and Peter Harrison, published in *Nature Machine Intelligence*.

## Abstract

Artists are often recognizable through collections of distinctive patterns (‘fingerprints’) in their work. Identifying such traits has important applications in authorship attribution, education, cultural heritage research and historical analysis. Here we focus on music, a domain with a rich tradition of theoretical and mathematical analysis. We train a variety of supervised learning models to identify 20 iconic jazz musicians from a curated dataset of 84 h of recordings. In particular, we introduce a multi-input architecture that represents four musical domains separately: melody, harmony, rhythm and dynamics. This design allows us to accurately identify individual performers (our best model obtains 94% accuracy across 20 classes) and to examine which musical elements most strongly distinguish between individual artists. We release open-source implementations of our models and an accompanying web application for exploring our results.

## Links

- [Paper (Nature Machine Intelligence)](https://doi.org/10.1038/s42256-026-01279-9)
- [Open-source model implementations](https://github.com/HuwCheston/deep-pianist-identification)
- [Web app for exploring jazz piano styles](https://huwcheston.github.io/ImprovID-app/index.html)