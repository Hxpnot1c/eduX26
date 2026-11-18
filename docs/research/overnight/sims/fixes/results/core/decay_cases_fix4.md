# w3-06 first-principles cases (real code, settings.toml as is)

Part `ped_values`: prior 0.300, starting half-life 2.00 days.

## p_now on one part, by days since each student's last evidence

| student | d0 | d1 | d2 | d3 | d4 | d5 | d7 | d10 | d14 | d21 | d30 | d60 | half-life | clock |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U untouched | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 2.0 | none |
| W one wrong check | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 1.0 | none |
| WW two wrong checks | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 1.0 | none |
| C one right check | 0.646 | 0.591 | 0.545 | 0.506 | 0.473 | 0.445 | 0.403 | 0.361 | 0.331 | 0.309 | 0.302 | 0.300 | 4.0 | set |
| WC wrong then right (same day) | 0.447 | 0.404 | 0.374 | 0.352 | 0.337 | 0.326 | 0.313 | 0.305 | 0.301 | 0.300 | 0.300 | 0.300 | 2.0 | set |
| CCC right on days 0, 2, 6 | 0.894 | 0.869 | 0.845 | 0.821 | 0.799 | 0.778 | 0.738 | 0.685 | 0.624 | 0.539 | 0.462 | 0.344 | 16.0 | set |

## Crossing times for student C (one right check), t = h·log2(p_known / target)

- below `new` (0.40): level drops to new: 2.8 days
- below untouched U (prior): 4.4 days
- below W (one wrong, never right): 8.5 days
- below WW (two wrong, never right): 9.7 days
- student CCC (half-life 16 d, p_known 0.894) falls below U after 25.2 days and below W after 41.4 days from the last right answer

## Review gap after a right answer vs crossing time (scheduling shares from settings.toml)

| days to exam | review gap (days) | C's p_now when the review falls due | below U? | below W? |
|---|---|---|---|---|
| 150 | 37.5 | 0.001 | yes | yes |
| 90 | 22.5 | 0.013 | yes | yes |
| 61 | 15.2 | 0.046 | yes | yes |
| 45 | 6.8 | 0.201 | yes | no |
| 30 | 4.5 | 0.296 | yes | no |
| 14 | 2.1 | 0.449 | no | no |
| 10 | 1.0 | 0.543 | no | no |
| 5 | 1.0 | 0.543 | no | no |

## Propagation onto a prerequisite never answered right (prereq_boost, no clock)

- after right answer 1 on `ped_values` (day 0): `ped_values` 0.646, `ped_formula` 0.300 (new), `ped_formula` clock none
- after right answer 2 on `ped_values` (day 2): `ped_values` 0.830, `ped_formula` 0.300 (new), `ped_formula` clock none
- after right answer 3 on `ped_values` (day 4): `ped_values` 0.922, `ped_formula` 0.300 (new), `ped_formula` clock none
- after right answer 4 on `ped_values` (day 6): `ped_values` 0.964, `ped_formula` 0.300 (new), `ped_formula` clock none
- after right answer 5 on `ped_values` (day 8): `ped_values` 0.983, `ped_formula` 0.300 (new), `ped_formula` clock none
- after right answer 6 on `ped_values` (day 10): `ped_values` 0.992, `ped_formula` 0.300 (new), `ped_formula` clock none
- day 40: `ped_values` 0.888, `ped_formula` 0.300 (never answered, never decays)
- day 100: `ped_values` 0.725, `ped_formula` 0.300 (never answered, never decays)

## Exchange nudges with no check (transfer + constructive labels)

- after 3 exchanges: 0.300 (new)
- after 4 exchanges: 0.300 (new)
- after 8 exchanges: 0.300 (new)
- after 10 exchanges: 0.300 (new)
- after 14 exchanges: 0.300 (new)
- after 15 exchanges: 0.300 (new)
- 90 days later: 0.300 (new); review queued: {'reason': 'untested', 'due': '2027-01-11T17:08:00+00:00'}

## Untouched priors vs propagation.queue_band (learner.candidates; not called by live code)

- `ped_definition`: difficulty 0.30, prior 0.360, half-life 2.40
- `ped_formula`: difficulty 0.50, prior 0.300, half-life 2.00
- `ped_values`: difficulty 0.50, prior 0.300, half-life 2.00
- `pes_definition`: difficulty 0.50, prior 0.300, half-life 2.00
- `pes_formula`: difficulty 0.50, prior 0.300, half-life 2.00
- `yed_definition`: difficulty 0.50, prior 0.300, half-life 2.00
- `tax_supply_shift`: difficulty 0.70, prior 0.240, half-life 1.60  <- below band floor 0.30: never a candidate while untouched
- `tax_incidence_split`: difficulty 0.70, prior 0.240, half-life 1.60  <- below band floor 0.30: never a candidate while untouched
- `externality_tax_eval`: difficulty 0.50, prior 0.300, half-life 2.00

