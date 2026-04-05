import numpy as np
from config import *



def magnetic_force(q, v, b):
    force = q * (np.cross(v, b))
    return force # returns as a 3d vector

def ohms_law_r(i, v):
    resistence = i / v
    return resistence
def ohms_law_i(v=VOLTAGE, r=1):
    i = v / r
    return i 
def ohms_law_v():
    return

def calculate_resistence(resistivity=RAIL_RESISTIVITY, l=CURRENT_POSITION, w=RAIL_WIDTH, h=RAIL_HEIGTH):
    # multiply by 2 to account for both rails, assuming they are equal 
    r = 2 * (resistivity * l) / (w * h)
    return r

def calculate_kinematics():
    return

def calculate_velocity(f, q, b, theta):
    v = f / (q * b * np.sin(theta))
    return v

def calculate_lorentz_force(i=0, d=DISTANCE_BETWEEN_RAILS, b=0):
    #d is distance between rails
    f = i * d * b
    return f

def calculate_magnetic_field(mew=MAGNETIC_PERMEABILITY, i=0, d=DISTANCE_BETWEEN_RAILS):
    # Two rails carry current in opposite directions, fields add between them
    # Each rail contributes mew*i / (2*pi*d), doubled for both rails
    b = (mew * i) / (np.pi * d)
    return b

def calculate_new_velocity_with_kinematics(m=PROJECTILE_MASS, f=0, v_old=0, t=STEP):
    v_new = v_old + (f/m) * t
    return v_new