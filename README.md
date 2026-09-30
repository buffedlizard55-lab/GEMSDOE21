# GEMSDOE21 — audited fault-discovery research & submission hub

**Start here every session: read this whole README, including the full original prompt below.**

## Submission first

The project will publish a locally range/grid/hash-verified **historical H19-4 GeoTIFF** at the very top of its GitHub Pages site, with a unique transport filename, a copyable short note, and an [executive submission guide](docs/executive-summary.html). This is the file the user associates with **0.1894**, not a newly validated improvement. Renaming the same predictions does not create a new experiment and does not justify another weekly slot.

Site: https://buffedlizard55-lab.github.io/GEMSDOE21/ . Do not claim this deployment is live until its build is verified.

## Research standard and core values

**Maximize P(Win):** prefer reproducible geological discovery, falsifiable hypotheses, whole-segment buffered validation, exact official scoring, multiplicity correction and honest negative results over public-leaderboard probing. The goal is to compete for the top prize; no score or prize is guaranteed.

**Own the Outcome:** download/prepare data autonomously where authorized, deliver an obvious usable `.tif`, protect format/provenance integrity, execute three real review passes, and report any blocker instead of inventing success. Keep a reusable source/knowledge registry with precise official links and a dated, permitted-source feed. Do not evade rules using multiple accounts.

## Initial audit (2026-09-30)

* This checkout starts with an 11-byte README and no code, tests, data, site or prior-session notes. The statement that an existing GPU pipeline has only a data-placement blocker does **not** describe this checkout.
* Inspected 19GEMSDOE main @ `a3aca62fdb2be428f4245e22570cbc54082b2c15`. Its H19 exporter needs an untracked H19 arm-prediction cache, and the snapshot does not contain the code that generates it. Prior claims of full reproducibility must be qualified.
* Its training script assigns sampled uncatalogued pixels negative targets; its default sparse scorer removes known-pixel FP penalties but can still award TP recovery from masked known predictions. These are not the requested PU/exact-mask validation assumptions.
* Competition target is **fault traces indicative of geothermal resources**, not confirmed vents/reservoirs. A hot well or aligned magnetic edge is not proof of an unmapped permeable fault.
* Current inspected leaderboard snapshot: DARD **0.3168**, smrtdoog5 **0.1894**, extradr19 **0.1855**. Source: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ . Account best does not identify a submission file; all prompt file-to-score associations remain USER-REPORTED unless separately established.
* Official metric: `DTI = TP_w / (TP_w + 0.2 FP_w + 0.8 FN_w + epsilon)`, triangular 300m support. Known faults are masked **pixel-exactly**, not buffered; only NEW ground truth earns distance credit. https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ and https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4 .
* A genuinely automatic DrivenData leaderboard/upload feed is not implemented: its Terms prohibit automatic monitoring, and there is no authorized DrivenData session. https://www.drivendata.org/termsofuse/ . Scheduled updates will target permitted official data/GitHub only; label the leaderboard as a snapshot.

## Locked candidate plan, before code/results

See [research/preregistration-h21.md](research/preregistration-h21.md), which defines mechanisms, confounders, layers, exact fixed parameters, expected metric decomposition, whole-component holdout, nnPU risk and four-member Bonferroni family.

| Rank | Hypothesis | Expected local ΔDTI (not a leaderboard forecast) | Cost / viability |
|---|---|---:|---|
| 1 | H21-1: co-oriented gravity/RTP edges persistent across 100–300m smoothing scales | +0.008 dense; +0.004 sparse | Low–medium; test first, existing physical data |
| 2 | H21-2: repeated consistent drainage offsets across a scarp | +0.005 | High; official NHDPlus HR product retrieval/extent check required |
| 3 | H21-3: unit-interior versus lithologic-contact contextual discrimination | +0.004 | Medium; official SGMC/GeMS version/file retrieval required |
| 4 | H21-4: well-depth/background-conduction-corrected thermal residual | +0.003 | Medium–high; blocked by missing depth/measurement metadata |

**No new candidate recommendation unless it beats a reproducible clean current-best comparator on the same registered holdout.** Missing H19 generation provenance blocks that claim; frozen full-catalogue predictions are not a holdout comparator.

## Limitations and next work

No GPU is exposed here; a CPU-only PU experiment does not need one. Data mirrors supplied by the user are transport, not independent official verification. The template mirror reportedly contains known positives although the official description says an all-absence sample; recheck locally and flag the mismatch. Current hidden labels, expert mapping coverage and private score are unavailable. Eligibility, official registration, final upload and AI-use disclosure remain the entrant's responsibility, not agent-verifiable facts. See [research/next-session.md](research/next-session.md) for the actual end-of-session handoff once generated.

## Full original user prompt (verbatim session brief)

<details>
<summary>Read the entire request before every session. This is a specification and historical/user-reported information, not independent evidence.</summary>

```text
Review the repo. 

There should be an easy to download submission tif file as described by the prompt.  Read the entire prompt.

Research and Discovery Standard (read first, every session): Treat this as a research program, not a leaderboard-probing exercise — the two produce different behavior even at the same submission budget. Before writing any code, state a specific, falsifiable geological hypothesis: name the physical mechanism a signature should indicate, name at least one non-fault process that produces the same pattern, and write down the predicted direction and rough size of the score change before testing it. Validate exclusively on a hide-and-recover holdout that withholds whole known fault segments (with a buffer) from every input the model sees and mirrors the organizer-confirmed scoring behavior exactly — pixel-exact masking of known faults, no credit for a near-miss against the wrong label. Because the competition's entire premise is that the training catalogue is incomplete, treat every unlabeled pixel as unlabeled, not confirmed-negative, and train and score accordingly, rather than optimizing against the false assumption that "absent from the training raster" means "no fault." Decompose the actual metric — a 0.2/0.8-weighted precision–recall trade, from the official definition — and test each candidate against that decomposition, not against how convincing the map looks. Once several hypotheses are running against the same holdout, pre-register each one's predicted effect before looking and correct for testing multiple candidates at once; the improvement that survives is the one that beat a documented prediction, not the best of an uncorrected batch. Log every rejected hypothesis and why — a negative result narrows the next one and is worth writing down for Phase 2's expert reviewers, who read the reasoning behind a flagged fault, not just the pixel mask. All of this runs inside our one repo, on our one account, against our own holdout: a score bought by testing more variants against the live leaderboard instead of a real holdout isn't a result, it's the same uncorrected-comparisons error this whole standard exists to catch.

Here are the results from our groups submissions, separated by ....:

GEMSDOE1

[https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html)

GEMSDOE SCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/6GEMSDOE/](https://buffedlizard55-lab.github.io/6GEMSDOE/)

6GEMSDOE SCORE: 0.0286

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.1193

1 · SUBMIT FIRST

f347b70daa

Pindrop nodes

....

GEMSDOE2

[https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html)

GEMSDOE2 SCORE: 0.1560

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.0830

2 · SUBMIT SECOND37f9d5b855

Pindrop catalogue-gap target SECOND SYSTEM

....

[https://buffedlizard55-lab.github.io/GEMSDOE4/](https://buffedlizard55-lab.github.io/GEMSDOE4/)

GEMSDOE 4 SCORE: 0.0343

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.1152

3 · CONTROL · UPLOAD LAST

4e03fc9705

Pindrop dense ridge control

....

[https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html)

5GEMSDOE SCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/7GEMSDOE/](https://buffedlizard55-lab.github.io/7GEMSDOE/)

7GEMSDOE SCORE: 0.1461

....

[https://buffedlizard55-lab.github.io/8GEMSDOE/](https://buffedlizard55-lab.github.io/8GEMSDOE/)

8GEMSDOESCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html)

9GEMSDOE SCORE: 0.0107

....

[https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html)

11GEMSDOE SCORE: 0.0202

....

[https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html)

12GEMSDOE SCORE:0.1294

r7-nms3-dem10-scarp_0c9199f14e62

[https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html)

12GEMSDOE SCORE:0.1294

r7-nms3-dem10-scarp_0c9199f14e62_allfinite

SDCF9

....

[https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html)

15GEMSDOE SCORE: 0.0782

gems-tso1-20260929T005627Z-conj_alteration_mag

smashi34

....

[https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html)

14GEMSDOE SCORE: 0.0020

smrtdoog5

....

[https://buffedlizard55-lab.github.io/GEMSDOE10/](https://buffedlizard55-lab.github.io/GEMSDOE10/)

10GEMSDOE SCORE:

h16-continuation-20260927T065521077735Z-3431b83c7c: 0.0461

h20-dem10-scarp-thin-20260927T155223039488Z-ffc91a1686: 0.0921

H25-ctx-ridge-20260927T232947704150Z-6452ae1d00: 0.1280

h28-dotted-ridge-20260928T020256236880Z-6452ae1d00: 

wbg1

....

[https://buffedlizard55-lab.github.io/13GEMSDOE/](https://buffedlizard55-lab.github.io/13GEMSDOE/)

13GEMSDOE SCORE:

....

[https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html)

16GEMSDOE SCORE:

h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan: 0.1855

h18-3a-topo-geophys-x-complexity-prior-20260930-c502dfab-nan: 

h18-4-usgs-geologic-map-faults-gap-20260930-aef8f42c-nan: 

extradr19

....

[https://buffedlizard55-lab.github.io/17GEMSDOE/](https://buffedlizard55-lab.github.io/17GEMSDOE/)

17GEMSDOE SCORE:0.0187

17GEMSDOE_F-ensemble-2pct_20260930T050626Z

....

[https://buffedlizard55-lab.github.io/18GEMSDOE/](https://buffedlizard55-lab.github.io/18GEMSDOE/)

18GEMSDOE SCORE: 0.0297

....

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan: 

....

20GEMSDOE SCORE:

....

21GEMSDOE SCORE:

....

22GEMSDOE SCORE:

....

23GEMSDOE SCORE:

....

24GEMSDOE SCORE:

....

25GEMSDOE SCORE:

....

26GEMSDOE SCORE:

....

27GEMSDOE SCORE:

....

HIGHEST SCORE SO FAR IS THE FOLLOWING

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

We need to study the highest score we have achieved so far which is 19GEMSDOE.

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.1855?  

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the specific layer(s) involved, the physical signature being targeted (e.g., an edge-detection or curvature transform), why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before touching a weekly submission slot — do not spend a submission slot on an idea that hasn't beaten the current holdout best. If a candidate can't be validated without new external data, name the specific free, official source needed and check it's obtainable before proposing the idea as viable.

Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.                      

Verify no hallucinations.    

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

We need to quickly look at the results and our results.

We have a good understanding of how our hypothesis, methodology, calculations, analysis are done so we should be able to figure out a way to score higher on the leaderboard using previous results and scoring that we have across the sites listed above.  We need to come up with distinct and unique strategies to score higher in this competition leaderboard.  We need to start doing heavy and deep research into the part of the project that matters the most, which is the scientific discovery of geothermal vents.  We should store all of our information and knowledge that we can gather from official verified sources.  This will serve as a starting point for other projects as well.  We need to think outside the box but still be grounded in proper scientific research, we are ultimately aiming for a top prize that many others are competing for.  So it's important to be contrarian but be smart about it.  We need to find sources of data that others are over looking or areas of the project when it comes to geothermal vents.  We need to do deep research and critical thinking and come up with new hypothesis to test.

Use these sites as a starting point for understanding how our group has generated submissions in the past.  

GEMSDOE1

[https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html)

GEMSDOE SCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/6GEMSDOE/](https://buffedlizard55-lab.github.io/6GEMSDOE/)

6GEMSDOE SCORE: 0.0286

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.1193

1 · SUBMIT FIRST

f347b70daa

Pindrop nodes

....

GEMSDOE2

[https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html)

GEMSDOE2 SCORE: 0.1560

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.0830

2 · SUBMIT SECOND37f9d5b855

Pindrop catalogue-gap target SECOND SYSTEM

....

[https://buffedlizard55-lab.github.io/GEMSDOE4/](https://buffedlizard55-lab.github.io/GEMSDOE4/)

GEMSDOE 4 SCORE: 0.0343

....

GEMSDOE3

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

GEMSDOE3 SCORE: 0.1152

3 · CONTROL · UPLOAD LAST

4e03fc9705

Pindrop dense ridge control

....

[https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html)

5GEMSDOE SCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/7GEMSDOE/](https://buffedlizard55-lab.github.io/7GEMSDOE/)

7GEMSDOE SCORE: 0.1461

....

[https://buffedlizard55-lab.github.io/8GEMSDOE/](https://buffedlizard55-lab.github.io/8GEMSDOE/)

8GEMSDOESCORE: 0.1563

....

[https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html)

9GEMSDOE SCORE: 0.0107

....

[https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html)

11GEMSDOE SCORE: 0.0202

....

[https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html)

12GEMSDOE SCORE:0.1294

r7-nms3-dem10-scarp_0c9199f14e62

[https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html)

12GEMSDOE SCORE:0.1294

r7-nms3-dem10-scarp_0c9199f14e62_allfinite

SDCF9

....

[https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html)

15GEMSDOE SCORE: 0.0782

gems-tso1-20260929T005627Z-conj_alteration_mag

smashi34

....

[https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html)

14GEMSDOE SCORE: 0.0020

smrtdoog5

....

[https://buffedlizard55-lab.github.io/GEMSDOE10/](https://buffedlizard55-lab.github.io/GEMSDOE10/)

10GEMSDOE SCORE:

h16-continuation-20260927T065521077735Z-3431b83c7c: 0.0461

h20-dem10-scarp-thin-20260927T155223039488Z-ffc91a1686: 0.0921

H25-ctx-ridge-20260927T232947704150Z-6452ae1d00: 0.1280

h28-dotted-ridge-20260928T020256236880Z-6452ae1d00: 

wbg1

....

[https://buffedlizard55-lab.github.io/13GEMSDOE/](https://buffedlizard55-lab.github.io/13GEMSDOE/)

13GEMSDOE SCORE:

....

[https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html)

16GEMSDOE SCORE:

h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan: 0.1855

h18-3a-topo-geophys-x-complexity-prior-20260930-c502dfab-nan: 

h18-4-usgs-geologic-map-faults-gap-20260930-aef8f42c-nan: 

extradr19

....

[https://buffedlizard55-lab.github.io/17GEMSDOE/](https://buffedlizard55-lab.github.io/17GEMSDOE/)

17GEMSDOE SCORE:0.0187

17GEMSDOE_F-ensemble-2pct_20260930T050626Z

....

[https://buffedlizard55-lab.github.io/18GEMSDOE/](https://buffedlizard55-lab.github.io/18GEMSDOE/)

18GEMSDOE SCORE: 0.0297

....

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan: 

....

20GEMSDOE SCORE:

....

21GEMSDOE SCORE:

....

22GEMSDOE SCORE:

....

23GEMSDOE SCORE:

....

24GEMSDOE SCORE:

....

25GEMSDOE SCORE:

....

26GEMSDOE SCORE:

....

27GEMSDOE SCORE:

....

HIGHEST SCORE SO FAR IS THE FOLLOWING

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

We need to study the highest score we have achieved so far which is 19GEMSDOE.

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

19GEMSDOE SCORE:

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.1855?  

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

0.3049	is the highest score right now so we need to design a new strategy, research, testing, analyzing, and generating submission system than the current website.  It should be unique, take unique approaches to generating a submission that can score higher than .3049.  

Put this prompt into the repo readme and read it everytime we work on the project as a starting point to make sure we are building what we are aiming for and have a strong base to continue building and improving on making something useful for everyday use.  It should solve the problem of having to manually check everything ourselves and having an up to date current feed.

Review the repo. 

The following is taken from the Arena AI team and I think it makes a good point on building a successful project, so let's keep the Core Values and Own the Outcome as a focal point when building, developing, researching, suggesting upgrades, and implementing the work.

Our Core Values

Maximize P(Win)

“Maximize the Probability of Winning”: our decision making framework. In every decision, we weigh tradeoffs, assess risk, and choose the path that maximizes the probability that Arena succeeds. We set aside our emotions and make tough decisions in order to maximize P(Win). “Maximize P(Win)” frees us from constraints and clarifies that we must put Arena first.

Own the Outcome

We own results end to end — not just our individual slice of the work. When problems arise and we have the means to act, we do so without waiting for permission or assignment. We treat failure and success as signals and use them to improve. At Arena, we stay accountable to the final outcome.

Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.                      

Verify no hallucinations.    

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

We need to focus on being able to generate a submission into the competition.  

The site should be able to generate a TIF file that is required for submission.  It should be as easy as download to click a File to submit into the competition.  This needs to be in the executive summary or the very beginning of the site.  it should be obvious when you visit the site.

I tried to submit the document that i downloaded from the site but it returned this error on the submission form:

"Predicted values must be in range [0, 1]"

Also we need to give it a unique name and A short comment to help you or your team tell submissions apart later e.g. clustering with k=25

Here is the submission page when i click submit file

New submission

File to submitNo file chosen

You can submit a single-band GeoTIFF (.tif) file, or a .zip file containing a single GeoTIFF, with your predictions. It must match the submission format's CRS, shape, and geotransform. You may wish to review the competition rules first.

Note (optional)

A short comment to help you or your team tell submissions apart later e.g. clustering with k=25

Create a executive summary subpage that explains exactly how to make a submission into the contest.

Work on the next steps from the previous sessions first.

The goal of this project is to place top of the leaderboard in this competition.  The following is the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)

We need to create a project that can compete and place top of the leaderboard.  We need to understand the problem, collect all the data and organize it into a clean easily auditable table with official verified links for manual verification.  

This is the guidelines we need to follow.[https://www.drivendata.org/competitions/306/competition-doe-gems/](https://www.drivendata.org/competitions/306/competition-doe-gems/)

Get familiar with the problem through the overview and problem description,[https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/). You might also want to reference additional resources available on the about page,[https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/).

Download the data from the data,[https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), tab.  

Create and train your own model. This reference solution,[https://github.com/drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) implements a simple approach.

Use your model to generate predictions that match the submission format.

Tell me what are you limitations and what you need access to during this project.  We will need to find free publicly available sources and data from official and verified sources if we are to use 3rd party or external data.  

this pdf outlines how submissions must be entered into the competition.  

[https://docs.nlr.gov/docs/fy26osti/96647.pdf](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

You must be able to do your own research, deep research, scientific literature research and organize the knowledge so that we can critically think through the problem and generate a solution through scientific and free publicly available information.  this must be done autonomously and must be constantly reviewed and improved upon.  Provide suggestions and improvements and implement them.

❌ No DrivenData auth → cannot auto-download training_features.tif, labels.tif, sample_submission.tif, 1m_DEM_links.csv from [https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (verified redirect to login)

See below for links from the above site.  See attached files for links from the above site.

[https://gdr.openei.org/submissions/1391](https://gdr.openei.org/submissions/1391)

Download competition data from [https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (requires login) to data/

See links below for competition data:

[https://www.dropbox.com/scl/fi/aemhtutjgcp6tr3tint94/GEMS_96647.pdf?rlkey=rek210cj2smnmzb8n0sla1vmd&amp;st=wz4kofki&amp;dl=0](https://www.dropbox.com/scl/fi/aemhtutjgcp6tr3tint94/GEMS_96647.pdf?rlkey=rek210cj2smnmzb8n0sla1vmd&st=wz4kofki&dl=0)

[https://www.dropbox.com/scl/fi/6rgvnuady818ol8yqgis4/example_submission.tif?rlkey=kbykilvau066xuogoosbf4cq8&amp;st=8junzdyw&amp;dl=0](https://www.dropbox.com/scl/fi/6rgvnuady818ol8yqgis4/example_submission.tif?rlkey=kbykilvau066xuogoosbf4cq8&st=8junzdyw&dl=0)

[https://www.dropbox.com/scl/fi/t7fyt03qdh9egyme0itwo/existing_faults.tif?rlkey=yiao96uluqdkipf0h5vju71jf&amp;st=rnino7ya&amp;dl=0](https://www.dropbox.com/scl/fi/t7fyt03qdh9egyme0itwo/existing_faults.tif?rlkey=yiao96uluqdkipf0h5vju71jf&st=rnino7ya&dl=0)

[https://www.dropbox.com/scl/fi/3vz9o0wwavi26xaeoxlwr/gems-geodawn-numerical-features.tif?rlkey=je8d8fepqfbst9lnwsq9rkplu&amp;st=zj1lag1r&amp;dl=0](https://www.dropbox.com/scl/fi/3vz9o0wwavi26xaeoxlwr/gems-geodawn-numerical-features.tif?rlkey=je8d8fepqfbst9lnwsq9rkplu&st=zj1lag1r&dl=0)

[https://www.dropbox.com/scl/fi/ig0mban712ns1atphgphe/Digital-elevation-model-links-JSON.pdf?rlkey=zm77f1vbtt2if8hlruymptnu3&amp;st=srhhir10&amp;dl=0](https://www.dropbox.com/scl/fi/ig0mban712ns1atphgphe/Digital-elevation-model-links-JSON.pdf?rlkey=zm77f1vbtt2if8hlruymptnu3&st=srhhir10&dl=0)

Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.                      

Verify no hallucinations.    

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

Site creation

Create a github page for this repo that has clean ui, user friendly, simple and easy to use.  It should be organized and clean.  

It should include all relevant information in an easy to read format with official verified links as sources for review.  Work line by line verify everything no hallucinations.

**The single remaining blocker to training is data placement**: run `bash scripts/download_competition_data.sh` on any unrestricted machine into `data/`, then `python scripts/prepare_data.py` — after that the full train→inference→validate pipeline is ready to run (GPU needed for training; metric/losses/validation all verified working here on CPU).

you need to complete the above task by yourself.  Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.                      

Verify no hallucinations.    

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

Run this task through multiple passes.

Pass 1: Implement the task completely and verify the result.

Pass 2: Review your work for bugs, missing requirements, incorrect assumptions, and edge cases. Fix everything you find.

Pass 3: Re-check the entire implementation against the original request. Improve accuracy, reliability, completeness, and code quality. Fix any remaining issues.

Do not stop after the first pass. Each pass must build on the previous one. Before finishing, verify that the final result fully satisfies the original request.  Work line by line verify everything no hallucinations.

Go ahead and create a pull request and then merge the pull request onto the main. Make suggestions for what work still needs to be done and any limitations that is in the way of a successful project.  It should be worked on in this next session or the next session.  Work line by line verify everything no hallucinations.
```

</details>
