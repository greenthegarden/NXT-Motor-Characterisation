#!/usr/bin/env python

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

# setup the serial port for communication
BrickPiSetup()

# Configure sensors on BrickPi
BrickPiSetupSensors()

motor_ports = [PORT_A, PORT_D, PORT_C]

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
	power_level = 70
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

def run_motor_characterisation() :

	print("Load input power level signal from file {0}".format("signal.mat"))
	# load signal
	import scipy.io as io
	# import data from mat file
	signal = io.loadmat("signal.mat",squeeze_me=True)
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
		measurement_times = []
		power_levels      = []
		angular_positions = []
		for power_sample in power_samples :
			motor_drive(motor_port,int(power_sample))
			position = motor_position(motor_port)
			if position is not -1 :
				measurement_times.append(time.time())
				power_levels.append(power_sample)
				angular_positions.append(position)
			time.sleep(sample_rate)
		motor_stop(motor_port)
#		value.append(motor_port)
		value.append(measurement_times)
		value.append(power_levels)
		value.append(angular_positions)

	# write data to mat file
#	try :
	io.savemat("output.mat", {"motor_results" : motor_results})
	print("Recorded data saved to file {0}".format("output.mat"))
#	except :
#		print("Failed to write data to file!!")

#---------------------------------------------------------------------------------------
# Run experiments
#
#---------------------------------------------------------------------------------------

encoder_calibration = False
motor_characterisation = True

if encoder_calibration :
	run_encoder_calibration()
if motor_characterisation :
	run_motor_characterisation()
