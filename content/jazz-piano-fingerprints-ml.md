---
title: "Machine Learning of Artistic Fingerprints in Jazz"
date: 2026-04-10
draft: false
url: "/jazz-piano-fingerprints-ml"
_build:
  list: never
sitemap:
  exclude: true
---

This page hosts online resources for a working paper entitled "Machine Learning of Artistic Fingerprints in Jazz" by Huw Cheston, Reuben Bance, and Peter Harrison.

## Abstract

Artists are often recognisable through collections of distinctive patterns ("fingerprints") in their work. Identifying such traits has important applications in authorship attribution, education, historical analysis, and education. In this paper, we focus on music, a domain with a rich tradition of theoretical and mathematical analysis. We train a variety of supervised-learning models to identify 20 iconic jazz musicians from a curated dataset of 84 hours of recordings. Our models include a novel multi-input architecture that represents four musical domains separately: melody, harmony, rhythm, and dynamics. This design allows us both to improve performer identification versus the state of the art (our best model obtains 94% accuracy across 20 classes) and to examine which musical elements most strongly distinguish individual artists. We release open-source implementations of our models and an accompanying web application for exploring our results.

## Links

- [Open-source model implementations](https://github.com/HuwCheston/deep-pianist-identification)
- [Web app for exploring jazz piano styles](https://huwcheston.github.io/ImprovID-app/index.html)