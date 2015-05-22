#!/usr/bin/env python

from pylab import *

wheel_diameter = 56/1000.0 # diameter of wheel in metres

import scipy.io as io
# import data from mat file
output = io.loadmat("output.mat", squeeze_me=True)

import numpy as np

measurement_times     = np.array(output['measurement_times'])
power_levels          = np.array(output['power_levels'])
rhm_angular_positions = np.array(output['rhm_angular_positions'])
lhm_angular_positions = np.array(output['lhm_angular_positions'])

measurement_times         = measurement_times - measurement_times[0]

rhm_angular_positions     = np.unwrap(np.deg2rad(rhm_angular_positions), np.pi)
rhm_angular_displacements = np.ediff1d(np.rad2deg(rhm_angular_positions), to_begin=0)
rhm_linear_displacements  = (rhm_angular_displacements / 360.0) * np.pi * wheel_diameter * 100
#rhm_linear_displacements = (rhm_angular_displacements / 2.0) * wheel_diameter * 100

lhm_angular_positions     = np.unwrap(np.deg2rad(lhm_angular_positions), np.pi)
lhm_angular_displacements = np.ediff1d(np.rad2deg(lhm_angular_positions), to_begin=0)
lhm_linear_displacements  = (lhm_angular_displacements / 360.0) * np.pi * wheel_diameter * 100
#rhm_linear_displacements = (lhm_angular_displacements / 2.0) * wheel_diameter * 100

# figure()
# plot(measurement_times, rhm_angular_positions)
# plot(measurement_times, lhm_angular_positions)
#
# figure()
# plot(measurement_times, rhm_angular_displacements)
# plot(measurement_times, lhm_angular_displacements)
#
# figure()
# plot(measurement_times, rhm_linear_displacements)
# plot(measurement_times, lhm_linear_displacements)
#
# show()

import numpy as np
import matplotlib.pyplot as plt

fig, ax1 = plt.subplots()
ax1.plot(measurement_times, power_levels, 'b-')
ax1.set_xlabel('Measurement Time (s)')
# Make the y-axis label and tick labels match the line color.
ax1.set_ylabel('Power Level', color='b')
for tl in ax1.get_yticklabels():
	tl.set_color('b')

ax2 = ax1.twinx()
ax2.plot(measurement_times, rhm_angular_displacements, 'r-')
ax2.set_ylabel('Angular Displacement (degrees)', color='r')
for tl in ax2.get_yticklabels():
	tl.set_color('r')
plt.show()
