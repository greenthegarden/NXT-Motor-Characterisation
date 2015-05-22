#!/usr/bin/env python

from pylab import *

wheel_diameter = 56/1000.0 # diameter of wheel in metres

import scipy.io as io
# import data from mat file
output = io.loadmat("output.mat", squeeze_me=True)

import numpy as np

times                 = np.array(output['times'])
power_levels          = np.array(output['power_levels'])
measurement_times     = np.array(output['measurement_times'])
rhm_angular_positions = np.array(output['rhm_angular_positions'])
lhm_angular_positions = np.array(output['lhm_angular_positions'])

rhm_angular_positions     = np.unwrap(np.deg2rad(rhm_angular_positions), np.pi)
rhm_angular_displacements = np.ediff1d(np.rad2deg(rhm_angular_positions), to_begin=0)
rhm_linear_displacements  = (rhm_angular_displacements / 360.0) * np.pi * wheel_diameter * 100
#rhm_linear_displacements = (rhm_angular_displacements / 2.0) * wheel_diameter * 100

lhm_angular_positions     = np.unwrap(np.deg2rad(lhm_angular_positions), np.pi)
lhm_angular_displacements = np.ediff1d(np.rad2deg(lhm_angular_positions), to_begin=0)
lhm_linear_displacements  = (lhm_angular_displacements / 360.0) * np.pi * wheel_diameter * 100
#rhm_linear_displacements = (lhm_angular_displacements / 2.0) * wheel_diameter * 100

figure()
plot(times, power_levels)

figure()
plot(measurement_times, rhm_angular_positions)
plot(measurement_times, lhm_angular_positions)

figure()
plot(measurement_times, rhm_angular_displacements)
plot(measurement_times, lhm_angular_positions)

figure()
plot(measurement_times, rhm_linear_displacements)
plot(measurement_times, lhm_angular_positions)

show()
