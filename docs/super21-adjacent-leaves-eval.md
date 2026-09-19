# Super-board (21x21) leaves: adjacent-dictionary evaluation

Eight English-family lexica did not get dedicated super-board leavegen
runs (CSW24, NWL20, OSW2, OSW3, OSW4, CSW07, CSW15, TWL14), on the
expectation that a closely related edition's leaves would perform about
as well without the multi-hour training cost. This page records the
head-to-head evaluation used to pick which existing `_super21.klv2` file
each of those eight lexica ships with (as a symlink, not a copy -- see
bottom).

Method: for each target lexicon, race the candidate leaf files against
each other playing that lexicon's own super-board self-play games
(mirrored pairs, `-wmp false` throughout since WMP cannot represent any
language's super-board tile counts -- see the KLV/BitRack note in the
main leaves doc). 500,000 pairs per matchup unless noted. All matches
run on the same machine/build as the rest of the super-board leavegen
work.

## CSW family (CSW07, CSW15, CSW24)

Candidates: CSW21 and CSW12 (both have dedicated super leaves). CSW07
additionally got a three-way test including OSWI, since OSWI (2000) is
the direct historical predecessor of the whole CSW line.

| target | matchup | result (P1 per pair) | verdict |
|---|---|---|---|
| CSW07 | CSW21 vs CSW12 | -0.15 &plusmn; 0.12, CI [-0.39, 0.09] | null |
| CSW07 | OSWI vs CSW21 | +0.38 &plusmn; 0.16, CI [0.07, 0.69] | OSWI wins (barely significant) |
| CSW07 | OSWI vs CSW12 | -0.20 &plusmn; 0.14, CI [-0.48, 0.08] | null |
| CSW15 | CSW21 vs CSW12 | -0.17 &plusmn; 0.12, CI [-0.40, 0.07] | null |
| CSW24 | CSW21 vs CSW12 | +0.11 &plusmn; 0.12, CI [-0.12, 0.35] | null |

CSW07 is a genuine three-way near-tie: OSWI beats CSW21 by a hair
(the only comparison in this whole table that clears significance), but
is statistically indistinguishable from CSW12, and CSW12 in turn is
indistinguishable from CSW21. No candidate loses significantly to
either of the others. **Picked CSW12** for CSW07, since it has the best
(non-significant) point estimate against both alternatives.

CSW15 and CSW24 only tested CSW21 vs CSW12, both null, and the sign
flips between the two lexica (CSW12 favored on CSW15, CSW21 favored on
CSW24) -- consistent with pure noise rather than a real edge either
way. **Picked CSW12 for CSW15, CSW21 for CSW24**, matching whichever had
the (non-significant) favorable point estimate for that specific
lexicon. Treat both as coin flips, not real wins.

## OSW family (OSW2, OSW3, OSW4)

Candidates: OSW1 and OSWI (both have dedicated super leaves; OSWI is
english-family per its `OSW`-prefixed name but is a much later,
much larger word list than OSW1-4).

| target | matchup | result (P1 per pair) | verdict |
|---|---|---|---|
| OSW2 | OSW1 vs OSWI | +1.76 &plusmn; 0.19, CI [1.40, 2.13] | **OSW1 wins clearly** |
| OSW3 | OSW1 vs OSWI | +0.20 &plusmn; 0.18, CI [-0.16, 0.55] | null |
| OSW4 | OSW1 vs OSWI | -0.28 &plusmn; 0.18, CI [-0.63, 0.08] | null |

OSW2's result is decisive and real -- OSW1's leaves are clearly better
for OSW2 than the much-later OSWI's. OSW3 and OSW4 are both null,
with the point estimate flipping direction between them (OSW1 favored
on OSW3, OSWI favored on OSW4). **Picked OSW1 for OSW2 (real win),
OSW1 for OSW3 (coin flip, favorable point estimate), OSWI for OSW4
(coin flip, favorable point estimate)**.

## TWL family (TWL14)

Candidates: TWL98 and TWL06 (both have dedicated super leaves).

| target | matchup | result (P1 per pair) | verdict |
|---|---|---|---|
| TWL14 | TWL98 vs TWL06 | -0.45 &plusmn; 0.15, CI [-0.74, -0.15] | **TWL06 wins clearly** |

Significant and unambiguous. **Picked TWL06 for TWL14.**

## NWL family (NWL20)

Only one same-family candidate exists (NWL23 -- no dedicated NWL20
super leaves were ever built). Ran a 20,000-pair sanity check against
an untrained zero-value baseline on NWL20's own games rather than a
real head-to-head, just to confirm NWL23's leaves aren't secretly bad
for NWL20's (older, shorter) word list.

| target | matchup | result (P1 per pair) | verdict |
|---|---|---|---|
| NWL20 | NWL23 vs zero-value baseline | +188.4 &plusmn; 1.3, CI [185.9, 190.9] (20,000 pairs) | NWL23 is clearly sane |

**Picked NWL23 for NWL20** (only candidate; confirmed non-broken).

## Final picks

| lexicon lacking dedicated leaves | ships with | basis |
|---|---|---|
| CSW07 | CSW12 | 3-way near-tie, best composite point estimate |
| CSW15 | CSW12 | coin flip (null result) |
| CSW24 | CSW21 | coin flip (null result) |
| OSW2 | OSW1 | real, significant win |
| OSW3 | OSW1 | coin flip (null result) |
| OSW4 | OSWI | coin flip (null result) |
| TWL14 | TWL06 | real, significant win |
| NWL20 | NWL23 | only candidate; sanity-checked |

Only OSW2 and TWL14 have a real, statistically clear winner among their
candidates. The rest (CSW07, CSW15, CSW24, OSW3, OSW4) are close enough
that the pick shouldn't be read as "this file is better" -- it's "we
had to pick one, and this is the (non-significant) favorite." If any of
these lexica turn out to matter enough to be worth it, they're good
candidates for a real dedicated super-board leavegen run later.

## Implementation: symlinks, not copies

Each of the eight `data/lexica/<LEX>_super21.klv2` files above is a
**symlink** to the winning candidate's actual file (e.g.
`CSW24_super21.klv2 -> CSW21_super21.klv2`), not a byte copy. This
keeps it obvious in the repo that these lexica are intentionally
sharing leaves rather than each having independently-trained values,
and avoids storing the same ~4.3MB payload eight extra times.
