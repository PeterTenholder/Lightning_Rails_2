import os
import numpy as np

TIME = 1.0   #  max seconds to run but loop quits early when it leaves the rails
STEP = 1e-6  

# False = launch +x  loaded at beginning
# True  = launch -x loaded at far side
RAIL_POLARITY_REVERSED = False

RAIL_TOTAL_LENGTH = 0.22 # m
RAIL_DIAMETER_M = 0.003# m
LOAD_DISTANCE_FROM_END_M = 0.08 # m where ball starts

PROJECTILE_MASS = 0.00005 #kg
ARMATURE_CONTACT_LENGTH_M = 0.005   

SUPPLY_CURRENT_A = 4.7  # constant DC curcuit amps 

FRICTION_COEFFICIENT = 0.05  
CONTACT_RESISTANCE = 0.005   # ohms used for I^2R reporting

# materials, values found online
RAIL_RESISTIVITY = 1.68e-8
MAGNETIC_PERMEABILITY = 4e-7 * np.pi

# rail_spacing.csv : position_m, spacing_m   
# bfield.csv       : position_m, B_tesla     just maget measurements
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
RAIL_SPACING_CSV = os.path.join(_THIS_DIR, "rail_spacing.csv")
BFIELD_CSV = os.path.join(_THIS_DIR, "Magnetic Field Raingun Data.csv")
SPACING_IS_OUTER_TO_OUTER = True  # set False if csv already stores inner gap, just helpful depending on which measurements you do or watt it to do

