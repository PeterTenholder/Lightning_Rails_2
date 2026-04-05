from calculations import magnetic_force, ohms_law_r, ohms_law_i, ohms_law_v, calculate_resistence, calculate_kinematics, calculate_velocity, calculate_lorentz_force, calculate_magnetic_field, calculate_new_velocity_with_kinematics
from config import *
import matplotlib.pyplot as plt


time = TIME # seconds
step_i = STEP # how many places the time is broken into
step = step_i

total_rounds = int(time/step_i)

for i in range(total_rounds):
    print(f'\nStep {i}')

    #assuming already have new location
    if RAIL_TOTAL_LENGTH <= CURRENT_POSITION:
        print(f"{RAIL_TOTAL_LENGTH} <= {CURRENT_POSITION}")
        print("Off the rails!")
        break
    new_resistence = calculate_resistence(l=CURRENT_POSITION)
    print(new_resistence)
    RESISTENCES.append(new_resistence)
    new_current = ohms_law_i(r=new_resistence + INTERNAL_RESISTANCE)
    CURRENTS.append(new_current)

    magnetic_field = calculate_magnetic_field(i=new_current)

    lorentz_force = calculate_lorentz_force(i=new_current, b=magnetic_field)

    v_old = VELOCITIES[-1] if VELOCITIES else 0


    friction_force = FRICTION_COEFFICIENT * PROJECTILE_MASS * 9.81
    net_force = lorentz_force - friction_force
    new_velocity = max(0, calculate_new_velocity_with_kinematics(f=net_force, v_old=v_old))

    print(f'Current Velocity: {new_velocity}m/s')
    VELOCITIES.append(new_velocity)

    dl = new_velocity * step_i
    CURRENT_POSITION = max(INITIAL_POSITION, dl + CURRENT_POSITION)

    print(f'Current Position on the rail: {CURRENT_POSITION}m out of {RAIL_TOTAL_LENGTH}m')


final_distance = calculate_kinematics()

num_steps = len(VELOCITIES)
time_per_step = STEP
times = [i * time_per_step for i in range(num_steps)]

plt.figure(figsize=(10, 6))

plt.subplot(3, 1, 1)
plt.plot(times, VELOCITIES)
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.title('Velocity vs Time')

plt.subplot(3, 1, 2)
plt.plot(times, CURRENTS)
plt.xlabel('Time (s)')
plt.ylabel('Current (A)')
plt.title('Current vs Time')

plt.subplot(3, 1, 3)
plt.plot(times, RESISTENCES)
plt.xlabel('Time (s)')
plt.ylabel('Resistance (Ohms)')
plt.title('Resistance vs Time')

plt.tight_layout()
plt.savefig('graph.png')
plt.show()
