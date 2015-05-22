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

port_rh_motor = PORT_A
port_lh_motor = PORT_D

# Define motors
BrickPi.MotorEnable[port_rh_motor] = 1 #Enable the right drive motor
BrickPi.MotorEnable[port_lh_motor] = 1 #Enable the left drive motor

def motorControl(powerLeft, powerRight) :
	BrickPi.MotorSpeed[port_lh_motor] = powerLeft
	BrickPi.MotorSpeed[port_rh_motor] = powerRight
	BrickPiUpdateValues()

def motorDrive(power_level) :
	motorControl(power_level,power_level)

def motorStop() :
	motorControl(0,0)


#---------------------------------------------------------------------------------------
# Definition of experiments
#
#---------------------------------------------------------------------------------------

def encoder_calibration() :
	power = 70
	ports = [port_rh_motor, port_lh_motor]

	for port in ports :
		print("Motor on port {0}".format(port))
		# get position
		result = BrickPiUpdateValues()
		if not result :
			position = (BrickPi.Encoder[port]%720)/2.0
			print("position: {0}".format(position))
		# if motor not near zero rotate until at zero
		while position > 1 :
			BrickPi.MotorSpeed[port] = power
			result = BrickPiUpdateValues()
			if not result :
				position = (BrickPi.Encoder[port]%720)/2.0
				print("position: {0}".format(position))
				if position < 1 and position > 359 :
					BrickPi.MotorSpeed[port] = 0
					BrickPiUpdateValues()
			time.sleep(.05)

		BrickPi.MotorSpeed[port] = 0
		BrickPiUpdateValues()


def motor_characterisation() :

	print("Load input power level signal from file {0}".format("signal.mat"))

	# load signal
	import scipy.io as io
	# import data from mat file
	signal = io.loadmat("signal.mat", squeeze_me=True)

	sample_rate  = signal['sample_rate']
	times        = signal['times']
	power_levels = signal['power']

	print("Starting NXT motor test")

	import time

	measurement_times    = []
	rhm_angular_postions = []
	lhm_angular_postions = []

	for power_level in power_levels :
		motorDrive(int(power_level))
		result = BrickPiUpdateValues()
		if not result :
			measurement_times.append(time.time())
			# motor readings
			rhm_angular_positions.append((BrickPi.Encoder[port_rh_motor]%720)/2.0)
			lhm_angular_positions.append((BrickPi.Encoder[port_lh_motor]%720)/2.0)
		time.sleep(sample_rate)

	# write data to mat file
	io.savemat("output.mat", {"times"                : times,
                            "power_levels"         : power_levels,
                            "measurement_times"    : measurement_times,
                            "rhm_angular_positions": rhm_angular_positions,
                            "lhm_angular_positions": lhm_angular_positions,
                            })

	print("Recorded data saved to file {0}".format("output.mat"))

#---------------------------------------------------------------------------------------
# Run experiments
#
#---------------------------------------------------------------------------------------

encoder_calibration = True
motor_characterisation = True

encoder_calibration()
motor_characterisation()
