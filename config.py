import os
import numpy as np

TIME = 4.0   #  max seconds to run but loop quits early when it leaves the rails
STEP = 1e-6  

# False = launch +x  loaded at beginning
# True  = launch -x loaded at far side
RAIL_POLARITY_REVERSED = False

RAIL_TOTAL_LENGTH = 0.22 # m
RAIL_DIAMETER_M = 0.0052# m
LOAD_DISTANCE_FROM_END_M = 0.01 # m where ball starts

PROJECTILE_MASS = 0.1933e-3 #kg, the mass is 0.1933g
ARMATURE_CONTACT_LENGTH_M = 0.005   

SUPPLY_CURRENT_A = 4.61  # constant amps measured when ball not rolling but connected

#Efficiency of supply current that actually ball has when rolling since the current drops during rolling
CONTACT_EFFICIENCY = 0.35

FRICTION_COEFFICIENT = 0.02

# Linear drag rolling it cant continue to keep going faster due to wrinkles and rail bends, sets terminal velocity
DRAG_COEFFICIENT = 0.002


# when it touches at a tiny spot and the spot acts like resistor
CONTACT_RESISTANCE = 0.005   # ohms, used for I^2 R power reporting only

RAIL_RESISTIVITY = 1.68e-8 # copper
MAGNETIC_PERMEABILITY = 4e-7 * np.pi

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
RAIL_SPACING_CSV = os.path.join(_THIS_DIR, "Rail Lengths.csv")
BFIELD_CSV = os.path.join(_THIS_DIR, "Magnetic Field Railgun Data.csv")
SPACING_IS_OUTER_TO_OUTER = True  # True if the measurements is outside rail to outside  rail
