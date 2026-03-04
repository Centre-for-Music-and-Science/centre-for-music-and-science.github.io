---
title: "GlobalMood"
summary: "A large-scale cross-cultural dataset for music emotion recognition, featuring 1,182 tracks from 5 countries with multilingual participant ratings."
image: "/images/datasets/globalmood_logo.png"
repo: "https://github.com/harin-git/GlobalMood"
publication: "lee-globalmood"
weight: 1
---

## Overview

GlobalMood is a large-scale cross-cultural dataset for music emotion recognition (MER), featuring **1,182 music tracks** from **5 countries** (with plans to expand to over 20 countries), **multilingual participant ratings** in 5 languages (Arabic, Spanish, French, Korean, English), and **mood descriptors** freely elicited through an iterative chain process across participants.

## Dataset Description

The dataset contains four main CSV files:

- **`songmeta_GlobalMood.csv`** (70KB): Song metadata including YouTube video IDs, countries, artists, and titles
- **`rawrating_GlobalMood.csv`** (30MB): Individual participant ratings for each song-mood pair
- **`meanrating_GlobalMood.csv`** (6.3MB): Aggregated mean ratings across participants in each country
- **`chains_GlobalMood.csv`** (5.9MB): Tags provided by participants in chains during the elicitation phase

## Experimental Design

The experiment was implemented using the PsyNet framework. Participants rated how well each mood tag represents the mood expressed or conveyed by the music using a 5-point scale (1 = Not expressing at all, 5 = Extremely expressing).

## Citation

If you use this dataset in your research, please cite:

Lee, H., Çelen, E., Harrison, P. M. C., Anglada-Tort, M., van Rijn, P., Park, M., Schönwiesner, M., & Jacoby, N. (2025). GlobalMood: A cross-cultural benchmark for music emotion recognition. *Proceedings of the 26th International Society for Music Information Retrieval Conference (ISMIR)*.

## License

This project is licensed under the MIT License.
