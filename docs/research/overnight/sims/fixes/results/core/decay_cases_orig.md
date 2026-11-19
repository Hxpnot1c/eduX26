# w3-06 first-principles cases (real code, settings.toml as is)

Part `ped_values`: prior 0.300, starting half-life 2.00 days.

## p_now on one part, by days since each student's last evidence

| student | d0 | d1 | d2 | d3 | d4 | d5 | d7 | d10 | d14 | d21 | d30 | d60 | half-life | clock |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U untouched | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 2.0 | none |
| W one wrong check | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 0.149 | 1.0 | none |
| WW two wrong checks | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 0.120 | 1.0 | none |
| C one right check | 0.646 | 0.543 | 0.457 | 0.384 | 0.323 | 0.272 | 0.192 | 0.114 | 0.057 | 0.017 | 0.004 | 0.000 | 4.0 | set |
| WC wrong then right (same day) | 0.447 | 0.316 | 0.224 | 0.158 | 0.112 | 0.079 | 0.040 | 0.014 | 0.003 | 0.000 | 0.000 | 0.000 | 2.0 | set |
| CCC right on days 0, 2, 6 | 0.833 | 0.798 | 0.764 | 0.731 | 0.700 | 0.671 | 0.615 | 0.540 | 0.454 | 0.335 | 0.227 | 0.062 | 16.0 | set |

## Crossing times for student C (one right check), t = h·log2(p_known / target)

- below `new` (0.40): level drops to new: 2.8 days
- below untouched U (prior): 4.4 days
- below W (one wrong, never right): 8.5 days
- below WW (two wrong, never right): 9.7 days
- student CCC (half-life 16 d, p_known 0.833) falls below U after 23.6 days and below W after 39.8 days from the last right answer

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

- after right answer 1 on `ped_values` (day 0): `ped_values` 0.646, `ped_formula` 0.369 (new), `ped_formula` clock none
- after right answer 2 on `ped_values` (day 2): `ped_values` 0.777, `ped_formula` 0.433 (developing), `ped_formula` clock none
- after right answer 3 on `ped_values` (day 4): `ped_values` 0.884, `ped_formula` 0.479 (developing), `ped_formula` clock none
- after right answer 4 on `ped_values` (day 6): `ped_values` 0.945, `ped_formula` 0.506 (developing), `ped_formula` clock none
- after right answer 5 on `ped_values` (day 8): `ped_values` 0.975, `ped_formula` 0.520 (developing), `ped_formula` clock none
- after right answer 6 on `ped_values` (day 10): `ped_values` 0.988, `ped_formula` 0.527 (developing), `ped_formula` clock none
- day 40: `ped_values` 0.840, `ped_formula` 0.527 (never answered, never decays)
- day 100: `ped_values` 0.607, `ped_formula` 0.527 (never answered, never decays)

## Exchange nudges with no check (transfer + constructive labels)

- after 3 exchanges: 0.398 (new)
- after 4 exchanges: 0.433 (developing)
- after 8 exchanges: 0.576 (developing)
- after 10 exchanges: 0.644 (developing)
- after 14 exchanges: 0.763 (secure)
- after 15 exchanges: 0.788 (secure)
- 90 days later: 0.788 (secure); review queued: {'reason': 'untested', 'due': '2027-01-11T17:08:00+00:00'}

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

