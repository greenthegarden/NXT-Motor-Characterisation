#!/usr/bin/env python

from pylab import *

wheel_diameter = 56/1000.0 # diameter of wheel in metres

import scipy.io as io
# import data from mat file
output = io.loadmat("output.mat", squeeze_me=True)

import numpy as np

motor_results = np.array(output['motor_results'])

#print len(motor_results)
#print motor_results[0]

import matplotlib.pyplot as plt

for motor_result in motor_results :
	port              = motor_result[0]
	measurement_times = np.array(motor_result[1])
	power_levels      = np.array(motor_result[2])
	angular_positions = np.array(motor_result[3])

	print("Processing results for motor on port {0}".format(port))

	measurement_times     = measurement_times - measurement_times[0]

	angular_positions     = np.unwrap(np.deg2rad(angular_positions), np.pi)
	angular_displacements = np.ediff1d(np.rad2deg(angular_positions), to_begin=0)
	linear_displacements  = (angular_displacements / 360.0) * np.pi * wheel_diameter * 100

	fig, ax1 = plt.subplots()
	ax1.plot(measurement_times, power_levels, 'b-')
	ax1.set_xlabel('Measurement Time (s)')
	# Make the y-axis label and tick labels match the line color.
	ax1.set_ylabel('Power Level', color='b')
	for tl in ax1.get_yticklabels():
		tl.set_color('b')
	ax2 = ax1.twinx()
	ax2.plot(measurement_times, angular_displacements, 'r-')
	ax2.set_ylabel('Angular Displacement (degrees)', color='r')
	for tl in ax2.get_yticklabels():
		tl.set_color('r')
	plt.show()
