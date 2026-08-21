---
title: "Dynamics of music popularity"
open: true
weight: 2
supervisor: peter-harrison
thumbnail: "/images/topics/eras-tour.jpg"
thumbnail_credit:
  author: "Ronald Woan"
  license: "CC BY-SA 2.0"
  license_url: "https://creativecommons.org/licenses/by-sa/2.0/"
cosupervisors:
  - manuel-anglada-tort
  - daniel-mullensiefen
  - harin-lee
projects:
  - pop
  - emotions
  - memory
---

Why do some songs become popular and not others? Why do certain artists manage to sell millions of albums whereas others barely manage a thousand? Why do some genres capture audiences for decades and others quietly peter out?

These questions are challenging to answer because they involve the intersection of multiple complex phenomena. We have music itself, an intricate and highly varied cultural practice that has developed in many strands over centuries. We have the context of the music and its consumption, including the public personas of the musicians, the physical spaces in which the music is played, and the social makeup of the music’s audiences. We have the psychology of the listener, in particular psychological processes of pleasure, liking, memory, and meaning, all operating to determine listeners’ decisions to consume one musical track or album over another. We then have societal factors, including the commercial (e.g. how do radio stations decide which artists to promote?) and the social (e.g. how do people choose music to recommend to their friends), many of which are now shaped by digital technologies (e.g. music recommendation systems; social media platforms). All of these systems interact to determine music popularity.

Our goal is to develop a comprehensive computational model of these processes. We will approach this using linked data across several modalities:

* Music audio and derived features;
* Popularity data (e.g. sales, streams, radio plays);
* Listener responses collected using behavioural experiments;
* Listener-level streaming data (e.g. track listening times, skips, likes).

This work would be part of an international collaboration including the research team of a well-known music streaming platform, as well as Manuel Anglada-Tort (Goldsmiths College), Daniel Müllensiefen (University of Hamburg), and Harin Lee (Kings College, Cambridge).

Newcomers are welcome to choose a particular part of this landscape to focus on. Here are some ideas:

**Music audio analysis.** Music modelling will be a big part of the above project. In particular, we need algorithms that can automatically quantify relevant aspects of musical style. These algorithms will need to work with audio input, and they will need to generalise over a wide range of musical styles and cultures.

**Popularity analysis.** Music popularity is by no means unitary. This project could study the best way to operationalise popularity, compiling, critiquing, and developing measures covering both commercial success, critical reception, and social media penetration. It could then examine how these different measures relate to each other, uncovering underlying causal relationships between consumption, evaluation, and social media.

**Listener testing.** We hypothesise that popular songs are often psychologically distinctive. Perhaps they elicit particularly high enjoyment in listeners, or perhaps they are particularly prone to elicit earworms, or perhaps they capture some contemporary feeling or mood in a distinctive way. Can we design behavioural experiments to capture these differences, and eventually predict future potential from early psychological testing?

**Streaming data analysis.** Behavioural experiments are typically limited in terms of both sample size (maximum a few thousand participants) and ecological validity (the music listening is rather unnatural). An exciting alternative is enabled by our music streaming company collaboration, which gives us access to a massive dataset of listener behaviour covering actions such as track listening times, skips, and likes. We can use this dataset to study how different songs elicit different kinds of user behaviours, and potentially identify early markers of a track’s future potential.

**Artificial market experiments.** A famous paper by Salganik et al. (2006) constructed artificial markets where thousands of participants (real humans\!) downloaded songs with or without knowledge of other participants’ choices. The results showed that this social information produced a strong ‘richer-get-richer’ feedback loop, where popular songs became more popular due to herding effects. The authors posited that such effects might explain why music popularity is so hard to predict. We would build on this paper, developing more advanced artificial market experiments to study the impact of social media and music recommendation systems on popularity dynamics. Coupled with computer simulations, this would provide a causal complement to the observational studies described above.

## *References*

Salganik et al. (2006), Experimental study of inequality and unpredictability in an artificial cultural market. *Science* *311*, pp. 854-856. https://doi.org/10.1126/science.1121066

## See also

- [Computational music cognition](/topics/computational-music-cognition/)
