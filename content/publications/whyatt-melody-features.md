---
title: 'melody-features: A Python Package for Symbolic Melody Analysis'
date: 2025-12-16
# generated from bibtex; do not edit manually
authors: Whyatt, D. M., & Harrison, P. M. C.
journal: 'Conference: Digital Music Research Network 20'
doi: https://www.qmul.ac.uk/dmrn/media/dmrn/DMRN-20-Abstracts-15-Dec.pdf
abstract: |
  We introduce *melody-features*, an open-source Python package designed to consolidate 7 of the leading computational melody analysis toolboxes into a single common resource. In particular, we reimplement or wrap the following toolboxes:

  - FANTASTIC (Müllensiefen, 2009)
  - SIMILE/melsim (Frieler & Müllensiefen, 2004; Silas & Frieler, 2025)
  - IDyOM (Pearce, 2005)
  - jSymbolic (McKay & Fujinaga, 2006)
  - MIDI Toolbox (Eerola & Toiviainen, 2004)
  - Partitura (Cancino-Chacón et al., 2022)

  We also implement various additional features that complement and/or extend the toolboxes above. The resulting package contains > 200 features covering many aspects of pitch and rhythm (see Table 1 for a summary; see https://github.com/dmwhyatt/melody-features for a full list). We anticipate that the resulting package should make it much easier for researchers to apply a diverse set of analysis approaches in diverse scenarios, including music cognition research, MIR, computational composition and music visualisation.

  Though code written in Python is often slower than that of other languages, our implementation is designed to be efficient in terms of reusing computations and taking advantage of parallel processing. This makes many of our implementations equally as fast or even more performant than the reference implementations, especially through the use of the heavily optimised top-level `get_all_features()` function.

  In our presentation, we will illustrate the use of the package with a generic MIR style classification task, predicting whether a given melody from the Essen Folksong Collection originates from Europe or China. We performed a logistic regression, trained using an 80/20 train/test split over 5 folds with an l2 regularisation penalty. This model achieved an accuracy of 98.97% across a balanced testing set of 874 melodies, only misclassifying 9 melodies, and produces a highly intuitive set of feature importances.
bibtex: |-
  @article{whyatt-melody-features,
    author = {Whyatt, D. M. and Harrison, P. M. C.},
    title = {melody-features: A Python Package for Symbolic Melody Analysis},
    journal = {Conference: Digital Music Research Network 20},
    year = {2025},
    url = {https://www.qmul.ac.uk/dmrn/media/dmrn/DMRN-20-Abstracts-15-Dec.pdf}
  }
# generated from bibtex; do not edit manually
citation_apa: 'Whyatt, D. M., & Harrison, P. M. C. (2025). Melody-features: a python
  package for symbolic melody analysis. <em>Conference: Digital Music Research Network
  20</em>. https://www.qmul.ac.uk/dmrn/media/dmrn/DMRN-20-Abstracts-15-Dec.pdf'
---

