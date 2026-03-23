---
title: Gibbs Sampling with People
date: 2020-01-01
methods:
- large-scale-online-experiments
abstract: A core problem in cognitive science and machine learning is to understand
  how humans derive semantic representations from perceptual objects, such as color
  from an apple, pleasantness from a musical chord, or seriousness from a face. Markov
  Chain Monte Carlo with People (MCMCP) is a prominent method for studying such representations,
  in which participants are presented with binary choice trials constructed such that
  the decisions follow a Markov Chain Monte Carlo acceptance rule. However, while
  MCMCP has strong asymptotic properties, its binary choice paradigm generates relatively
  little information per trial, and its local proposal function makes it slow to explore
  the parameter space and find the modes of the distribution. Here we therefore generalize
  MCMCP to a continuous-sampling paradigm, where in each iteration the participant
  uses a slider to continuously manipulate a single stimulus dimension to optimize
  a given criterion such as 'pleasantness'. We formulate both methods from a utility-theory
  perspective, and show that the new method can be interpreted as 'Gibbs Sampling
  with People' (GSP). Further, we introduce an aggregation parameter to the transition
  step, and show that this parameter can be manipulated to flexibly shift between
  Gibbs sampling and deterministic optimization. In an initial study, we show GSP
  clearly outperforming MCMCP; we then show that GSP provides novel and interpretable
  results in three other domains, namely musical chords, vocal emotions, and faces.
  We validate these results through large-scale perceptual rating experiments. The
  final experiments use GSP to navigate the latent space of a state-of-the-art image
  synthesis network (StyleGAN), a promising approach for applying GSP to high-dimensional
  perceptual spaces. We conclude by discussing future cognitive applications and ethical
  implications.
bibtex: |-
  @inproceedings{NEURIPS2020_7880d722,
    author = {Harrison, Peter M. C. and Marjieh, Raja and Adolfi, Federico and van Rijn, Pol and Anglada-Tort, Manuel and Tchernichovski, Ofer and Larrouy-Maestri, Pauline and Jacoby, Nori},
    booktitle = {Advances in Neural Information Processing Systems},
    editor = {H. Larochelle and M. Ranzato and R. Hadsell and M.F. Balcan and H. Lin},
    pages = {10659--10671},
    publisher = {Curran Associates, Inc.},
    title = {Gibbs Sampling with People},
    url = {https://proceedings.neurips.cc/paper_files/paper/2020/file/7880d7226e872b776d8b9f23975e2a3d-Paper.pdf},
    volume = {33},
    year = {2020}
  }
# generated from bibtex; do not edit manually
journal: Advances in Neural Information Processing Systems
citation_apa: Harrison, P. M. C., Marjieh, R., Adolfi, F., van Rijn, P., Anglada-Tort,
  M., Tchernichovski, O., Larrouy-Maestri, P., & Jacoby, N. (2020). Gibbs Sampling
  with People. <em>Advances in Neural Information Processing Systems</em>. https://proceedings.neurips.cc/paper_files/paper/2020/file/7880d7226e872b776d8b9f23975e2a3d-Paper.pdf
citation_mla: Harrison, P. M. C., et al.. “Gibbs Sampling with People”. <em>Advances
  in Neural Information Processing Systems</em>, 2020, https://proceedings.neurips.cc/paper_files/paper/2020/file/7880d7226e872b776d8b9f23975e2a3d-Paper.pdf.
citation_chicago: Harrison, Peter M. C., Raja Marjieh, Federico Adolfi, Pol van Rijn,
  Manuel Anglada-Tort, Ofer Tchernichovski, Pauline Larrouy-Maestri, and Nori Jacoby.
  2020. “Gibbs Sampling with People”. In <em>Advances in Neural Information Processing
  Systems</em>. https://proceedings.neurips.cc/paper_files/paper/2020/file/7880d7226e872b776d8b9f23975e2a3d-Paper.pdf.
citation_ieee: '[1] P. M. C. Harrison, “Gibbs Sampling with People”, 2020. [Online].
  Available: https://proceedings.neurips.cc/paper_files/paper/2020/file/7880d7226e872b776d8b9f23975e2a3d-Paper.pdf'
authors: Harrison, P. M. C., Marjieh, R., Adolfi, F., van Rijn, P., Anglada-Tort,
  M., Tchernichovski, O., Larrouy-Maestri, P., & Jacoby, N.
link: https://proceedings.neurips.cc/paper_files/paper/2020/file/7880d7226e872b776d8b9f23975e2a3d-Paper.pdf
---
