#!/usr/bin/env python

#---------------------------------------------------------------------------------------
# Load configuration values
#
#---------------------------------------------------------------------------------------

# see https://wiki.python.org/moin/ConfigParserShootout
from configobj import ConfigObj
config = ConfigObj('NXT-motor-characterisation-analysis.cfg')


#---------------------------------------------------------------------------------------
# Run analysis
#
#---------------------------------------------------------------------------------------

from pylab import *

import sys, getopt, os

def print_help() :
	print("{0} -i <matfile>".format(os.path.basename(__file__)))

def main(argv) :
	matfile = ''
	try:
		opts, args = getopt.getopt(argv,"hi:",["matfile="])
	except getopt.GetoptError:
		print_help()
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print_help()
			sys.exit()
		elif opt in ("-i", "--matfile"):
			matfile = arg
	print("matfile to process {0}".format(matfile))

	try :
		# import data from mat file
		import scipy.io as io
		output = io.loadmat(matfile, squeeze_me=True)
		print("Loaded mat file")
	except :
		print("Failed to load mat file {0}".format(matfile))
		sys.exit(2)

	import numpy as np

	motor_results = np.array(output['motor_results'])

	#print len(motor_results)
	#print motor_results[0]

	wheel_diameter = float(config['robot_specifics_cfg']['WHEEL_DIAMETER'])/1000.0 # diameter of wheel in metres

	import matplotlib.pyplot as plt

	for motor_result in motor_results :
		port              = motor_result[int(config['results_index_cfg']['PORT_IDX'])]
		measurement_times = np.array(motor_result[int(config['results_index_cfg']['MEASUREMENT_TIMES_IDX'])])
		power_levels      = np.array(motor_result[int(config['results_index_cfg']['POWER_LEVELS_IDX'])])
		angular_positions = np.array(motor_result[int(config['results_index_cfg']['ANGULAR_POSITIONS_IDX'])])

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

if __name__ == "__main__":
   main(sys.argv[1:])
