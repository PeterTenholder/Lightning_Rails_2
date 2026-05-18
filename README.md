# Lightning Rails 2

## How to run it

```
.venv/bin/python main.py
```

Outputs are written to the project root: `B_profile.png`, `d_profile.png`,
`railgun_simulation.png`.

## Things that can be changed

In `config.py` every parameter is tunable. The most common things to change are:

| Parameter                    | Section            | Why change it             |
|------------------------------|--------------------|---------------------------------|
| `SUPPLY_CURRENT_A`           | ELECTRICAL SOURCE  | Changes Force.                  |
| `RAIL_POLARITY_REVERSED`     | POLARITY           | Flip launch direction           |
| `LOAD_DISTANCE_FROM_END_M`   | RAIL GEOMETRY      | Where the ball is loaded        |
| `PROJECTILE_MASS`            | PROJECTILE         | F=ma                            |


## CSV inputs

`rail_spacing.csv` and `bfield.csv` hold the measured profiles of magnetic field (when turned off, just magnets) and distnace between rails and use 1cm inputs at each point.

## Output files

| File                      | What it shows                                          |
|---------------------------|--------------------------------------------------------|
| `B_profile.png`           | Field values across the railgun                        |
| `d_profile.png`           | Spacing of railgun                                     |
| `railgun_simulation.png`  | 3x3 dashboard from the run.                            |



## Authors

- Peter Tenholder
- Ishaan Raghavendra Rao
