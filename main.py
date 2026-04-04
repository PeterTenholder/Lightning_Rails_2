from calculations import magnetic_force, ohms_law_r, ohms_law_i, ohms_law_v, calculate_resistence, calculate_kinematics, calculate_velocity, calculate_lorentz_force, calculate_magnetic_field, calculate_new_velocity_with_kinematics
from config import *

time = 5 # seconds
step_i = 0.1 # how many places the time is broken into
step = step_i

total_rounds = int(time/step_i)

for i in range(total_rounds):
    print(f'\nStep {i}')

    #assuming already have new location
    if RAIL_TOTAL_LENGTH <= CURRENT_POSITION:
        print(f"{RAIL_TOTAL_LENGTH} <= {CURRENT_POSITION}")
        print("Off the rails!")
        break
    new_resistence = calculate_resistence()
    print(new_resistence)
    RESISTENCES.append(new_resistence)
    new_current = ohms_law_i(r=new_resistence + INTERNAL_RESISTANCE)
    CURRENTS.append(new_current)

    magnetic_field = calculate_magnetic_field(i=new_current)

    lorentz_force = calculate_lorentz_force(i=new_current, b=magnetic_field)

    v_old = VELOCITIES[-1] if VELOCITIES else 0
    new_velocity = calculate_new_velocity_with_kinematics(f=lorentz_force, v_old=v_old)    #note q calculation comes form i = dq/dt thoguh maybe check it
    print(f'Current Velocity: {new_velocity}m/s')
    VELOCITIES.append(new_velocity)

    dl = new_velocity * step_i
    CURRENT_POSITION = dl + CURRENT_POSITION

    print(f'Current Position on the rail: {CURRENT_POSITION}m out of {RAIL_TOTAL_LENGTH}m')


final_distance = calculate_kinematics()


