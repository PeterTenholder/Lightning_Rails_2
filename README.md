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
| `SUPPLY_CURRENT_A`           | ELECTRICAL SOURCE  | Changes Force.                   |
| `RAIL_POLARITY_REVERSED`     | POLARITY           | Flip launch direction           |
| `LOAD_DISTANCE_FROM_END_M`   | RAIL GEOMETRY      | Where the ball is loaded        |
| `PROJECTILE_MASS`            | PROJECTILE         | F=ma                            |


## CSV inputs

`rail_spacing.csv` and `bfield.csv` hold the measured profiles of magnetic field (when turned off, just magnets) and distnace between rails and use 1cm inputs at each point.

## Output files

| File                      | What it shows                                          |
|---------------------------|--------------------------------------------------------|
| `B_profile.png`           | CSV B values + cubic spline. Sanity-check the fit.     |
| `d_profile.png`           | Outer + inner spacing + spline. Sanity-check the fit.  |
| `railgun_simulation.png`  | 3x3 trace dashboard from the run.                      |

The terminal also prints exit velocity, exit time, KE at exit, cumulative
I^2 R loss due to resistivity, and efficiency.

## Files

```
config.py            -- all adjustable parameters
calculations.py      -- physics formulas + CSV loader (rarely edited)
main.py              -- simulation loop and plots
rail_spacing.csv     -- measured rail spacing profile (replace with real data)
bfield.csv           -- measured external-magnet field profile
requirements.txt     -- numpy, matplotlib, scipy
```

## Authors

- Peter Tenholder
- Ishaan Raghavendra Rao
