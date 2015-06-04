#!/usr/bin/env python

#---------------------------------------------------------------------------------------
# Load configuration values
#
#---------------------------------------------------------------------------------------

# see https://wiki.python.org/moin/ConfigParserShootout
from configobj import ConfigObj
config = ConfigObj('NXT-motor-data-collection.cfg')


#---------------------------------------------------------------------------------------
# Enable logging
#
#---------------------------------------------------------------------------------------

#import logging

#logging.basicConfig(level=logging.DEBUG,
#logging.basicConfig(filename='pibot.log',
                    #level=logging.DEBUG,
                    #format='%(asctime)s %(levelname)5s %(module)13s: %(message)s')
#logger = logging.getLogger(__name__)


#---------------------------------------------------------------------------------------
# Configuration for BrickPi and NXT motors
#
#---------------------------------------------------------------------------------------

from BrickPi import *

POWER_MAX = int(config['motor_spec_cfg']['POWER_MAX'])
POWER_MIN = int(config['motor_spec_cfg']['POWER_MIN'])

# setup the serial port for communication
BrickPiSetup()

# Configure sensors on BrickPi
BrickPiSetupSensors()

motor_ports = [PORT_A, PORT_D]
#motor_ports = [PORT_A, PORT_D, PORT_C]

# Define motors
for motor_port in motor_ports :
	BrickPi.MotorEnable[motor_port] = 1

def motor_control(port, power_level) :
	BrickPi.MotorSpeed[port] = power_level
	BrickPiUpdateValues()

def motor_drive(port, power_level) :
	motor_control(port, power_level)

def motor_stop(port) :
	motor_control(port, 0)

def motor_position(port, position_print=False) :
	result = BrickPiUpdateValues()
	if not result :
		position = (BrickPi.Encoder[port]%720)/2.0
		if position_print :
			print("position: {0}".format(position))
		return position
	else :
		return -1


#---------------------------------------------------------------------------------------
# Definition of experiments
#
#---------------------------------------------------------------------------------------

def run_encoder_calibration() :
	power_level = POWER_MIN
	for motor_port in motor_ports :
		print("Motor on port {0}".format(motor_port))
		# get position
		position = motor_position(motor_port)		# if motor not near zero rotate until at zero
		if position is not -1 :
			while position > 1 :
				motor_drive(motor_port, power_level)
				position = motor_position(motor_port,True)
				if position is not -1 :
					if position < 1 and position > 359 :
						motor_drive(motor_port,power_level)
				time.sleep(.05)
			motor_stop(motor_port)

def run_motor_characterisation(sample_file="signal.mat") :

	print("Load input power level signal from file {0}".format(sample_file))
	# load signal
	import scipy.io as io
	# import data from mat file
	signal = io.loadmat(sample_file,squeeze_me=True)
	# extract data from signal data
	sample_rate   = signal['sample_rate']
	times         = signal['times']
	power_samples = signal['power']

	print("Starting NXT motor test")

	import time

	# create array for store results for each motor
	motor_results     = [[] for x in motor_ports]

	for idx, value in enumerate(motor_results) :
		motor_port = int(motor_ports[idx])
		print("Testing motor on port {0}".format(motor_port))
		ports             = []
		measurement_times = []
		power_levels      = []
		angular_positions = []
		ports.append(motor_port)
		for power_sample in power_samples :
			measurement_start = time.time()
			motor_drive(motor_port,int(power_sample))
			position = motor_position(motor_port)
			if position is not -1 :
				measurement_times.append(time.time())
				power_levels.append(power_sample)
				angular_positions.append(position)
			time.sleep(sample_rate-(time.time()-measurement_start))
		motor_stop(motor_port)
		value.append(ports)
		value.append(measurement_times)
		value.append(power_levels)
		value.append(angular_positions)

	# write data to mat file
	try :
		outfile = "output_" + str(int(time.time())) + ".mat"
		io.savemat(outfile, {"motor_results" : motor_results})
		print("Recorded data saved to file {0}".format(outfile))
	except :
		print("Failed to write data to file!!")


#---------------------------------------------------------------------------------------
# Run experiments
#
#---------------------------------------------------------------------------------------

import sys, getopt, os

def print_help() :
	print("{0}".format(os.path.basename(__file__)))
	print("-e to run encoder calibration")
	print("-m to run motor characterisation")
	print("-i <samplefile.mat> to specify a specifc sample mat file")

def main(argv) :

	encoder_calibration = False
	motor_characterisation = False
	sample_file = config['file_cfg']['SAMPLE_FILE']

	try:
		opts, args = getopt.getopt(argv,"hemi:",["samplefile="])
	except getopt.GetoptError:
		print_help()
		sys.exit(2)
	for opt, arg in opts :
		if opt == '-h':
			 print_help()
			 sys.exit()
		elif opt in ("-e"):
			 encoder_calibration = True
		elif opt in ("-m"):
			 motor_characterisation = True
		elif opt in ("-i", "--samplefile"):
			 sample_file = arg

	if encoder_calibration :
		print("Running encoder calibration")
		run_encoder_calibration()
	if motor_characterisation :
		print("Running motor characterisation with samplefile {0}".format(sample_file))
		run_motor_characterisation(sample_file)

if __name__ == "__main__":
   main(sys.argv[1:])
