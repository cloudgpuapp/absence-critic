<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# From Wald’s Notebook: The Armor That Is Not There

**Document 01 — Origin of the Insight**  
*Engineering narrative, starting from Abraham Wald’s point of view*  
*Prepared for the Bulletproof Model Shield Program*

---

## 1. The Room in 1943

I am looking at a set of diagrams of B-17s that returned from missions over Germany. The wings, the fuselage, the tail—everywhere there are clusters of holes. The engines and the cockpit areas are almost clean. The obvious recommendation, the one the officers keep repeating, is to put the armor where the holes are densest. More steel on the wings. More plating on the fuselage.

They are measuring the wrong population.

These are only the planes that came back. The holes I can see are the hits that were not fatal. The planes that took hits in the engines, the cockpit, the fuel lines—they are not in the hangar. Their damage maps do not exist. The absence of holes in those regions on the surviving aircraft is not evidence that those regions were rarely hit. It is evidence that a hit there usually prevented the aircraft from returning.

The armor must go where the holes are *not*.

That is the entire insight. Everything else is estimation under missing data.

## 2. What I Actually Did

I did not simply point at the empty spaces and say “armor there.” I built a method to estimate, for each region of the aircraft, the probability that a hit in that region would bring the plane down, using only the damage observed on the planes that returned, the number of planes that did not return, and a reasonable assumption about where hits land.

The key quantities:

- The observed distribution of damage on survivors.
- The number of aircraft lost (the non-survivors).
- An assumption (or prior) about the spatial distribution of hits if survival were not a filter.

From these I could invert the selection process. Regions that showed fewer hits on returning aircraft than their exposed area would predict were the regions in which a hit was more likely to be lethal. Those were the places that needed armor.

The method is general. Whenever the data you can observe have already been filtered by survival, the pattern of what is present tells you something about what is missing—if you are willing to model the filter.

## 3. The Principle, Stated Precisely

> When the only samples you can examine are the ones that survived a selection process, the visible damage marks the places that are *not* fatal. The critical vulnerabilities are in the places where the survivors show no damage, because damage there removed the sample from observation.

This is not a heuristic. It is a bias correction. Ignoring it produces systematically wrong decisions: you reinforce what can already be survived and leave unprotected what cannot.

## 4. Why This Matters Beyond Aircraft

Any system that learns from, or is evaluated only on, the outputs that “made it back” is subject to the same filter:

- Published papers are the studies that survived peer review and author persistence.
- Documented success stories are the projects that did not die quietly.
- Training corpora of text are the writings that were produced, published, indexed, and not deleted.
- Benchmark scores are the tasks for which someone bothered to create a clean test set and for which the model produced an answer that could be scored.

In each case the non-survivors—the null results, the abandoned attempts, the unwritten knowledge, the silent failures—are absent from the record. A model or a decision process that treats the surviving record as representative will systematically under-estimate risk in the empty regions and over-estimate the reliability of patterns that appear only among survivors.

## 5. The Engineering Implication

If we are going to build models that are robust under real-world selection pressures, we cannot train and evaluate them solely on the planes that came back. We must:

1. Explicitly model the selection process that produced the data we have.
2. Actively seek or reconstruct information about the non-survivors.
3. Attach a reasoning process whose job is to look for the holes that are *not* there and to adjust confidence and recommendations accordingly.

That process is the shield.

The rest of this design package specifies how to build it.
