# Mitigating the risks of counterhate replies on Twitter

This repository contains the corpus and code of the *SEM-23 paper "Not All Counterhate Tweets Elicit the Same Replies: A Fine-Grained Analysis". Authors: Abdullah Albanyan, Ahmed Hassan, and Eduardo Blanco.
<br />
<!--[[paper link](https://ojs.aaai.org/index.php/AAAI/article/view/21284)]
[[supplementary materials](/Docs/hate-twitter-supplemental.pdf)]-->

## Introduction
In this study, we aim to identify the kind of replies counterhate tweets elicit. Specifically, we investigate replies to counterhate tweets beyond whether the reply agrees or disagrees with the counterhate tweet by answering the following questions:

* Q1: Does the reply _agree_ with the counterhate tweet?
* If Q1 is _No_ (the reply disagrees with the counterhate tweet):
   * Q2: _Supports_ the hateful tweet?
   * Q3: _Attacks the author_ of the counterhate tweet?
* If Q1 is _Yes_ (the reply agrees with the counterhate tweet):
   * Q4: Adds _additional counterhate_?



## Example

The following Twitter thread originating with a hateful tweet. In the first example, the reply not only agrees with the counterhate tweet, but also adds additional counterhate:

<p align="center">
 <kbd>
<img  src="Docs/figs/reply1.png" width=50% height=50%>
  </kbd>
</p>

On the other hand, the second reply not only disagrees with the counterhate tweet, but also shows support for the hateful tweet:
<p align="center">
 <kbd>
<img src="Docs/figs/reply2.png" width=50% height=50%>
  </kbd>
</p>

<!-- ****************************************************************************************** 
## Citation

```
@article{Albanyan_Blanco_2022,
  title = {Pinpointing Fine-Grained Relationships between Hateful Tweets and Replies},
  volume = {36},
  url = {https://ojs.aaai.org/index.php/AAAI/article/view/21284},
  doi = {10.1609/aaai.v36i10.21284},
  abstractnote = {Recent studies in the hate and counter hate domain have provided the grounds for investigating how to detect this pervasive content in social media. These studies mostly work with synthetic replies to hateful content written by annotators on demand rather than replies written by real users. We argue that working with naturally occurring replies to hateful content is key to study the problem. Building on this motivation, we create a corpus of 5,652 hateful tweets and replies. We analyze their fine-grained relationships by indicating whether the reply (a) is hate or counter hate speech, (b) provides a justification, (c) attacks the author of the tweet, and (d) adds additional hate. We also present linguistic insights into the language people use depending on these fine-grained relationships. Experimental results show improvements (a) taking into account the hateful tweet in addition to the reply and (b) pretraining with related tasks.},
  number = {10},
  journal = {Proceedings of the AAAI Conference on Artificial Intelligence},
  author = {Albanyan, Abdullah and Blanco, Eduardo},
  year = {2022},
  month = jun,
  pages = {10418-10426},
  month_numeric = {6}
}
```
-->
