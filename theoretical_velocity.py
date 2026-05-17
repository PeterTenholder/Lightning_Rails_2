import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    DRAG_COEFFICIENT,
    FRICTION_COEFFICIENT,
    PROJECTILE_MASS,
    STEP,
    SUPPLY_CURRENT_A,
    TIME,
)
from calculations import (
    calculate_b_rail,
    calculate_friction_force_max,
    calculate_lorentz_force,
    load_field_and_spacing_profiles,
)

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TRIAL_CSV = os.path.join(_THIS_DIR, "AP Physics C Final Project Data Analysis.csv")


COL_NOTE = 6   # Item/Specifications -- carries the group A/B label
COL_DIST = 7   # Distance (cm)
COL_TIME = 8   # Time (s)
COL_START = 9  # Starting Point (cm)
COL_END = 10   # Ending Point (cm)
COL_VAVG = 11  # Velocity (m/s) 


def _maybe_float(cell):
    try:
        return float(cell)
    except (TypeError, ValueError):
        return None


def load_trials():
    trials = []
    group = "A"  #default
    with open(TRIAL_CSV, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) <= COL_VAVG:
                continue
            note = row[COL_NOTE].lower()
            if "same direction" in note:
                group = "B"
            elif "opposite direction" in note:
                group = "A"

            dist_cm = _maybe_float(row[COL_DIST])
            time_s = _maybe_float(row[COL_TIME])
            start_cm = _maybe_float(row[COL_START])
            end_cm = _maybe_float(row[COL_END])
            v_avg = _maybe_float(row[COL_VAVG])
            if None in (dist_cm, time_s, start_cm, end_cm, v_avg):
                continue

            trials.append({
                "group": group,
                "start_cm": start_cm,
                "end_cm": end_cm,
                "dist_cm": dist_cm,
                "time_s": time_s,
                "v_avg_measured": v_avg,
            })
    return trials


def estimate_endpoint_velocity(b_at, gap_at, start_m, end_m, group,
                               current=None, mu=None, drag_b=None,
                               step=None, time_max=None):
    
    if current is None:
        current = SUPPLY_CURRENT_A
    if mu is None:
        mu = FRICTION_COEFFICIENT
    if drag_b is None:
        drag_b = DRAG_COEFFICIENT
    if step is None:
        step = STEP
    if time_max is None:
        time_max = TIME

    pos = start_m
    # Launch direction comes from the real start->end ordering, not config.
    launch_sign = 1 if end_m >= start_m else -1

    def reached_end(p):
        return p >= end_m if launch_sign > 0 else p <= end_m

    velocity = 0.0
    last_velocity = 0.0
    total_steps = int(time_max / step)
    step_count = 0

    for _ in range(total_steps):
        if reached_end(pos):
            break
        step_count += 1

        b_magnet = float(b_at(pos))
        gap = float(gap_at(pos))
        b_rail_mag = calculate_b_rail(current, gap)

        if group == "B":
            b_total = -b_magnet + launch_sign * b_rail_mag
        else:
            b_total = b_magnet + launch_sign * b_rail_mag

        f_lorentz_signed = launch_sign * calculate_lorentz_force(current, b_total, gap)
        f_friction_max = calculate_friction_force_max(mu=mu)

        if velocity == 0.0:
            if abs(f_lorentz_signed) <= f_friction_max:
                f_net = 0.0
            else:
                f_friction_signed = np.sign(f_lorentz_signed) * f_friction_max
                f_net = f_lorentz_signed - f_friction_signed
        else:
            f_friction_signed = np.sign(velocity) * f_friction_max
            f_drag = drag_b * velocity
            f_net = f_lorentz_signed - f_friction_signed - f_drag

        velocity_new = velocity + (f_net / PROJECTILE_MASS) * step

        # static-friction stall guard (same as main.py)
        if velocity != 0.0 and np.sign(velocity_new) != np.sign(velocity):
            if abs(f_lorentz_signed) <= f_friction_max:
                velocity_new = 0.0

        pos += velocity_new * step
        velocity = velocity_new
        last_velocity = velocity_new

    reached = reached_end(pos)

    # Average velocity over the simulated run
    elapsed_time = step_count * step
    travel_dist = abs(pos - start_m)
    v_avg_theo = travel_dist / elapsed_time if elapsed_time > 0 else 0.0

    return {
        "v_avg_theo": v_avg_theo,
        "v_endpoint": abs(last_velocity),
        "launch_sign": launch_sign,
        "reached_end": reached,
    }


def print_header():
    print("=" * 72)
    print("Shared constants used by the model (from config.py):")
    print(f"  Supply current   I       : {SUPPLY_CURRENT_A:.4f} A")
    print(f"  Static friction  mu_s    : {FRICTION_COEFFICIENT:.4f}  ")
    print(f"  Kinetic friction mu_k    : {FRICTION_COEFFICIENT:.4f}")
    print(f"  Drag coefficient drag_b  : {DRAG_COEFFICIENT:.4f}  N/(m/s)")
    print(f"  Projectile mass  m       : {PROJECTILE_MASS*1000:.4f} g")
    print(f"  Integrator step  STEP    : {STEP:.1e} s")
    print()
    print("Group A = permanent magnets OPPOSING the induced rail field "
          "(model like  main.py)")
    print("Group B = permanent magnets ALIGNED with the induced rail field ")
    print("v_avg_measured (m/s) is column 11 of the sheet: distance / time, "
          "an average over the run.")
    print("v_theo_avg (m/s) is the model's matching run average: travelled "
          "distance / elapsed sim time.")
    print("=" * 72)
    print()


def main():
    b_at, gap_at, _ = load_field_and_spacing_profiles()
    trials = load_trials()

    print_header()

    header = (f"{'#':>3}  {'Grp':>3}  {'start(cm)':>9}  {'end(cm)':>8}  "
              f"{'sign':>4}  {'v_theo_avg(m/s)':>15}  "
              f"{'v_avg_meas(m/s)':>15}")
    print(header)
    print("-" * len(header))

    for i, t in enumerate(trials, start=1):
        start_m = t["start_cm"] / 100.0  
        end_m = t["end_cm"] / 100.0
        res = estimate_endpoint_velocity(
            b_at, gap_at, start_m, end_m, t["group"]
        )

        v_theo = res["v_avg_theo"]
        v_meas = t["v_avg_measured"]
        flag = "" if res["reached_end"] else "  <- did not reach endpoint"

        print(f"{i:>3}  {t['group']:>3}  {t['start_cm']:>9.2f}  "
              f"{t['end_cm']:>8.2f}  {res['launch_sign']:>4d}  "
              f"{v_theo:>15.4f}  {v_meas:>15.4f}{flag}")

    print("-" * len(header))
    print(f"Total trials: {len(trials)}  "
          f"(Group A: {sum(1 for t in trials if t['group'] == 'A')}, "
          f"Group B: {sum(1 for t in trials if t['group'] == 'B')})")


if __name__ == "__main__":
    main()
