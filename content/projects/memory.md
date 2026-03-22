---
title: "Memory"
summary: "Building computational models that capture the time-course of melodic memory formation and recall."
people: 
    - "david-whyatt"
    - "peter-harrison"
thumbnail: "/images/projects/memory.png"
---

## Computational Modelling of Melodic Memory
This project develops computational models of how listeners form and retain memories of melodies. By combining behavioural experiments with information-theoretic modelling, we investigate how statistical regularities in music interact with cognitive constraints to shape melodic memory. The work has implications for understanding both music cognition and broader memory processes.

Our work so far has been concerned with collecting and organising the vast range of different computational representations of melodies. By producing granular, interpretable features for our computational models, we can make inferences as to which aspects of melody are memorable on what time-courses, and begin to develop our understanding of how melodies are represented cognitively. Our taxonomy of features is available as an [<u>open-source Python package</u>](https://github.com/dmwhyatt/melody-features/).

We have spent much time exploring the structure of these different features, and have prepared an [<u>interactive visualization</u>](https://dmwhyatt.github.io/essen_new/) such that you can explore, too! This example shows one possible way in which we can simplify a complex network of related melodic features into higher-level latent constructs that relate to larger melodic structural concepts. This allows us to make highly interpretable memory models without sacrificing any detail on the melody level.

<iframe
  src="https://dmwhyatt.github.io/essen_new/"
  width="100%"
  height="750"
  style="border: none;"
  loading="lazy"
  title="3D Factor Network - interactive visualization of melodic features"
></iframe>

