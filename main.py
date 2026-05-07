import os
import sys
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    ARMATURE_CONTACT_LENGTH_M,
    CONTACT_RESISTANCE,
    FRICTION_COEFFICIENT,
    LOAD_DISTANCE_FROM_END_M,
    PROJECTILE_MASS,
    RAIL_DIAMETER_M,
    RAIL_POLARITY_REVERSED,
    RAIL_TOTAL_LENGTH,
    STEP,
    SUPPLY_CURRENT_A,
    TIME,
)
from calculations import (
    calculate_b_rail,
    calculate_friction_force_max,
    calculate_lorentz_force,
    calculate_rail_resistance,
    load_field_and_spacing_profiles,
)


def initial_conditions():
    # ball starts on opposite side of where it exits
    if RAIL_POLARITY_REVERSED:
        return RAIL_TOTAL_LENGTH - LOAD_DISTANCE_FROM_END_M, -1
    return LOAD_DISTANCE_FROM_END_M, +1


def has_exited(pos, sign):
    # off the rail = done
    return pos >= RAIL_TOTAL_LENGTH if sign > 0 else pos <= 0.0


def run_simulation(b_at, gap_at, verbose=False):
    pos, launch_sign = initial_conditions()
    velocity = 0.0
    current = SUPPLY_CURRENT_A
    total_steps = int(TIME / STEP)

    # logs for plotting 
    times, positions, velocities = [], [], []
    b_magnet_log, b_rail_log, b_total_log, gap_log = [], [], [], []
    f_lorentz_log, f_friction_log, f_net_log = [], [], []
    rail_R_log, ke_log, i2r_cum_log = [], [], []
    cumulative_i2r = 0.0

    for step_idx in range(total_steps):
        if has_exited(pos, launch_sign):
            if verbose:
                print(f"  exited at x={pos*100:.2f} cm (step {step_idx})")
            break
        b_magnet = float(b_at(pos))
        gap = float(gap_at(pos))
        b_rail_mag = calculate_b_rail(current, gap)
        b_total = b_magnet + launch_sign * b_rail_mag
        f_lorentz_signed = launch_sign * calculate_lorentz_force(current, b_total, gap)
        f_friction_max = calculate_friction_force_max(b_total)
        if velocity == 0.0:
            if abs(f_lorentz_signed) <= f_friction_max:
                f_net = 0.0
                f_friction_signed = f_lorentz_signed  
            else:
                f_friction_signed = np.sign(f_lorentz_signed) * f_friction_max
                f_net = f_lorentz_signed - f_friction_signed
        else:
            f_friction_signed = np.sign(velocity) * f_friction_max
            f_net = f_lorentz_signed - f_friction_signed

        #new velocity
        velocity_new = velocity + (f_net / PROJECTILE_MASS) * STEP

        #weird velocity flip debug
        if velocity != 0.0 and np.sign(velocity_new) != np.sign(velocity):
            if abs(f_lorentz_signed) <= f_friction_max:
                velocity_new = 0.0
        #new velocity
        pos += velocity_new * STEP

        # rail resistance grows w length
        rail_R = calculate_rail_resistance(abs(pos))
        cumulative_i2r += (current ** 2) * (rail_R + CONTACT_RESISTANCE) * STEP

        
        times.append(step_idx * STEP)
        positions.append(pos)
        velocities.append(velocity_new)
        b_magnet_log.append(b_magnet)
        b_rail_log.append(launch_sign * b_rail_mag)
        b_total_log.append(b_total)
        gap_log.append(gap)
        f_lorentz_log.append(f_lorentz_signed)
        f_friction_log.append(f_friction_signed)
        f_net_log.append(f_net)
        rail_R_log.append(rail_R)
        ke_log.append(0.5 * PROJECTILE_MASS * velocity_new ** 2)
        i2r_cum_log.append(cumulative_i2r)

        velocity = velocity_new

    # returns as np arrays for easy plotting
    return {
        "exit_velocity": velocities[-1] if velocities else 0.0,
        "exit_time": times[-1] if times else 0.0,
        "launch_sign": launch_sign,
        "times": np.asarray(times),
        "positions": np.asarray(positions),
        "velocities": np.asarray(velocities),
        "b_magnet": np.asarray(b_magnet_log),
        "b_rail": np.asarray(b_rail_log),
        "b_total": np.asarray(b_total_log),
        "gap": np.asarray(gap_log),
        "f_lorentz": np.asarray(f_lorentz_log),
        "f_friction": np.asarray(f_friction_log),
        "f_net": np.asarray(f_net_log),
        "rail_R": np.asarray(rail_R_log),
        "ke": np.asarray(ke_log),
        "i2r_cumulative": np.asarray(i2r_cum_log),
    }


def print_design_summary(raw):
    x0, sign = initial_conditions()
    print("=" * 60)
    print("RAILGUN DESIGN SUMMARY")
    print("=" * 60)
    print(f"Polarity reversed   : {RAIL_POLARITY_REVERSED}")
    print(f"Launch direction    : {'+x' if sign > 0 else '-x'}")
    print(f"Initial position    : {x0*100:.2f} cm")
    print(f"Rail length         : {RAIL_TOTAL_LENGTH*100:.2f} cm")
    print(f"Load distance       : {LOAD_DISTANCE_FROM_END_M*100:.2f} cm from end")
    print(f"Travel distance     : {(RAIL_TOTAL_LENGTH - LOAD_DISTANCE_FROM_END_M)*100:.2f} cm")
    print(f"Rail diameter       : {RAIL_DIAMETER_M*1000:.2f} mm")
    print(f"Inner gap range     : {raw['spacing_inner'].min()*1000:.2f} - {raw['spacing_inner'].max()*1000:.2f} mm")
    print(f"B_magnet range      : {raw['b_values'].min()*1000:.1f} - {raw['b_values'].max()*1000:.1f} mT")
    print(f"Supply current      : {SUPPLY_CURRENT_A:.1f} A")
    print(f"Projectile mass     : {PROJECTILE_MASS*1000:.3f} g")
    print(f"Friction coefficient: {FRICTION_COEFFICIENT}")
    print(f"Armature contact    : {RAIL_DIAMETER_M*1000:.2f} x {ARMATURE_CONTACT_LENGTH_M*1000:.2f} mm")
    print()


def plot_input_profiles(raw, b_at, gap_at):
    x_dense = np.linspace(0.0, RAIL_TOTAL_LENGTH, 600)

    # Magnetic   field plot
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(raw["b_positions"]*100, raw["b_values"]*1000, "o", label="csv", color="darkorange")
    ax.plot(x_dense*100, b_at(x_dense)*1000, "-", label="cubic spline", color="navy", linewidth=1.2)
    ax.set_xlabel("Position (cm)"); ax.set_ylabel("B_magnet (mT)")
    ax.set_title("External magnet field B_magnet(x)")
    ax.grid(True, alpha=0.3); ax.legend()
    plt.tight_layout(); plt.savefig("B_profile.png", dpi=150, bbox_inches="tight"); plt.close(fig)

    # Spacing plot for rails
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(raw["spacing_positions"]*100, raw["spacing_outer"]*1000, "o", label="raw outer-to-outer", color="gray")
    ax.plot(raw["spacing_positions"]*100, raw["spacing_inner"]*1000, "o", label="inner gap (-2D)", color="darkorange")
    ax.plot(x_dense*100, gap_at(x_dense)*1000, "-", label="inner-gap spline", color="navy", linewidth=1.2)
    ax.set_xlabel("Position (cm)"); ax.set_ylabel("Spacing (mm)")
    ax.set_title("Rail spacing d(x)")
    ax.grid(True, alpha=0.3); ax.legend()
    plt.tight_layout(); plt.savefig("d_profile.png", dpi=150, bbox_inches="tight"); plt.close(fig)


def plot_results(result):
    # 3x3 grid: 
    # row 0 = motion
    # row 1 = fields/forces 
    # row 2 = energy
    t = result["times"] * 1000 #miliseconds
    pos_cm = result["positions"] * 100

    fig, axes = plt.subplots(3, 3, figsize=(16, 11))
    fig.suptitle("Railgun simulation -- measured B(x), spacing(x), constant I", fontsize=13)

    # row 0 motion
    axes[0, 0].plot(t, result["velocities"], color="steelblue")
    axes[0, 0].axhline(0, color="black", linewidth=0.6, linestyle="--")
    axes[0, 0].set(xlabel="Time (ms)", ylabel="Velocity (m/s)", title="Velocity vs time")

    axes[0, 1].plot(t, pos_cm, color="purple")
    axes[0, 1].set(xlabel="Time (ms)", ylabel="Position (cm)", title="Position vs time")

    axes[0, 2].plot(pos_cm, result["velocities"], color="darkgreen")
    axes[0, 2].set(xlabel="Position (cm)", ylabel="Velocity (m/s)", title="Velocity vs position")

    # row one field forces


    axes[1, 0].plot(t, result["b_magnet"]*1000, label="B_magnet", color="darkorange")
    axes[1, 0].plot(t, result["b_rail"]*1000, label="B_rail (signed)", color="crimson")
    axes[1, 0].plot(t, result["b_total"]*1000, label="B_total", color="navy")
    axes[1, 0].set(xlabel="Time (ms)", ylabel="B (mT)", title="Field at armature")
    axes[1, 0].legend(fontsize=8)

    axes[1, 1].plot(t, result["gap"]*1000, color="teal")
    axes[1, 1].set(xlabel="Time (ms)", ylabel="Inner gap (mm)", title="Inner gap at armature")

    axes[1, 2].plot(t, result["f_lorentz"]*1000, label="F_lorentz", color="navy")
    axes[1, 2].plot(t, result["f_friction"]*1000, label="F_friction", color="crimson")
    axes[1, 2].plot(t, result["f_net"]*1000, label="F_net", color="black", linewidth=1.0)
    axes[1, 2].axhline(0, color="black", linewidth=0.4, linestyle="--")
    axes[1, 2].set(xlabel="Time (ms)", ylabel="Force (mN)", title="Forces")
    axes[1, 2].legend(fontsize=8)

    # row 2 energy
    axes[2, 0].plot(t, result["ke"]*1000, color="darkgreen")
    axes[2, 0].set(xlabel="Time (ms)", ylabel="KE (mJ)", title="Kinetic energy")

    axes[2, 1].plot(t, result["i2r_cumulative"], color="firebrick")
    axes[2, 1].set(xlabel="Time (ms)", ylabel="I^2 R loss (J)", title="Cumulative I^2 R")

    axes[2, 2].plot(t, result["rail_R"]*1000, color="darkorange")
    axes[2, 2].set(xlabel="Time (ms)", ylabel="Rail R (mOhm)", title="Rail resistance")
    for ax in axes.flat:
        ax.grid(True, alpha=0.3)




    plt.tight_layout()
    plt.savefig("railgun_simulation.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def report_efficiency(result):
    # ke out vs energy dumped into resistence
    # ke / energy loss as power - percent for every x J into rails ball had %J of kinetic energy
    if result["exit_time"] <= 0 or result["i2r_cumulative"].size == 0:
        print("Efficiency           : n/a (didn't move)")
        return
    ke_exit = result["ke"][-1]
    i2r_total = result["i2r_cumulative"][-1]
    if i2r_total > 0:
        print(f"KE at exit           : {ke_exit*1000:.4f} mJ")
        print(f"Cumulative I^2 R loss: {i2r_total:.4f} J")
        print(f"Efficiency (KE/I^2R) : {ke_exit/i2r_total*100:.4f} %")
    else:
        print("Efficiency           : n/a")


def main():
    # load measurements, print run setup, plots 
    b_at, gap_at, raw = load_field_and_spacing_profiles()
    print_design_summary(raw)
    plot_input_profiles(raw, b_at, gap_at)
    print("Saved input profiles to B_profile.png, d_profile.png")
    print("-" * 60)
    # now done with field and distance

    #run sim
    result = run_simulation(b_at, gap_at, verbose=True)

    #final position
    final_pos = result["positions"][-1]*100 if result["positions"].size else 0.0
    print(f"Exit velocity        : {result['exit_velocity']:.4f} m/s")
    print(f"Exit time            : {result['exit_time']*1000:.3f} ms")
    print(f"Final position       : {final_pos:.2f} cm")
    report_efficiency(result)

    plot_results(result)
    print("\nSaved trace plots to railgun_simulation.png")


if __name__ == "__main__":
    main()
