# physics + csv loader. tune values via config.py

import csv
import numpy as np
from scipy.interpolate import interp1d

from config import (
    ARMATURE_CONTACT_LENGTH_M,
    BFIELD_CSV,
    FRICTION_COEFFICIENT,
    MAGNETIC_PERMEABILITY,
    PROJECTILE_MASS,
    RAIL_DIAMETER_M,
    RAIL_RESISTIVITY,
    RAIL_SPACING_CSV,
    SPACING_IS_OUTER_TO_OUTER,
)


def _load_two_column_csv(path):
    xs, ys = [], []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            if not row:
                continue
            xs.append(float(row[0]))
            ys.append(float(row[1]))
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if xs.size < 4:
        raise ValueError(f"{path}: need >=4 rows for cubic interp")
    if not np.all(np.diff(xs) > 0):
        raise ValueError(f"{path}: positions must be strictly increasing")
    if not np.all(np.isfinite(ys)):
        raise ValueError(f"{path}: non-finite values")
    return xs, ys


def load_field_and_spacing_profiles():
    bx, b_vals = _load_two_column_csv(BFIELD_CSV)
    sx, s_vals = _load_two_column_csv(RAIL_SPACING_CSV)

    if SPACING_IS_OUTER_TO_OUTER:
        inner_gap = s_vals - 2.0 * RAIL_DIAMETER_M
    else:
        inner_gap = s_vals.copy()

    if np.any(inner_gap <= 0):
        raise ValueError("inner gap went negative -- check RAIL_DIAMETER_M vs spacing csv")

    # smooth curves through the csv points -- call b_at(x) / gap_at(x) for any x
    b_at = interp1d(bx, b_vals, kind="cubic", bounds_error=False,
                    fill_value=(b_vals[0], b_vals[-1]))
    gap_at = interp1d(sx, inner_gap, kind="cubic", bounds_error=False,
                      fill_value=(inner_gap[0], inner_gap[-1]))
    raw = {
        "b_positions": bx, "b_values": b_vals,
        "spacing_positions": sx, "spacing_outer": s_vals, "spacing_inner": inner_gap,
    }
    return b_at, gap_at, raw


def calculate_rail_resistance(armature_position):
    area = np.pi * (RAIL_DIAMETER_M / 2.0) ** 2
    return 2.0 * RAIL_RESISTIVITY * armature_position / area


def calculate_b_rail(current, inner_gap):
    return MAGNETIC_PERMEABILITY * current / (np.pi * inner_gap)


def calculate_lorentz_force(current, b_total, inner_gap):
    return current * b_total * inner_gap


def calculate_magnetic_pressure_normal_force(b_total):
    pressure = (b_total ** 2) / (2.0 * MAGNETIC_PERMEABILITY)
    return pressure * RAIL_DIAMETER_M * ARMATURE_CONTACT_LENGTH_M


def calculate_friction_force_max(b_total, mass=PROJECTILE_MASS, mu=FRICTION_COEFFICIENT):
    return mu * (mass * 9.81 + calculate_magnetic_pressure_normal_force(b_total))
