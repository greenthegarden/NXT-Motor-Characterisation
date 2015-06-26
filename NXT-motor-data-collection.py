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

# setup the serial port for communication
BrickPiSetup()

# Configure sensors on BrickPi
BrickPiSetupSensors()

#PORT_LH_MOTOR = config['motor_ports_cfg']['PORT_LH_MOTOR']
#PORT_RH_MOTOR = config['motor_ports_cfg']['PORT_RH_MOTOR']
PORT_LH_MOTOR = PORT_D
PORT_RH_MOTOR = PORT_A

# Define motors
BrickPi.MotorEnable[PORT_LH_MOTOR] = 1 #Enable the left drive motor
BrickPi.MotorEnable[PORT_RH_MOTOR] = 1 #Enable the right drive motor

POWER_MAX = int(config['motor_spec_cfg']['POWER_MAX'])
POWER_MIN = int(config['motor_spec_cfg']['POWER_MIN'])

def motor_control(powerLeft, powerRight) :
	BrickPi.MotorSpeed[PORT_LH_MOTOR] = powerLeft
	BrickPi.MotorSpeed[PORT_RH_MOTOR] = powerRight
	BrickPiUpdateValues()

def motor_stop() :
	motor_control(0,0)

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

import scipy.io as io
import time

def run_characterisation_drive(sample_rate     = float(config['test_defaults_cfg']['SAMPLE_RATE']),
                               duration        = int(config['test_defaults_cfg']['DURATION']),
                               lhm_power_level = int(config['test_defaults_cfg']['LHM_POWER_LEVEL']),
                               rhm_power_level = int(config['test_defaults_cfg']['RHM_POWER_LEVEL']),
                               ) :

	print("Power levels => lhm: {0}, rhm: {1}".format(lhm_power_level,rhm_power_level))

	measurement_times     = []
	lhm_power_levels      = []
	rhm_power_levels      = []
	lhm_angular_positions = []
	rhm_angular_positions = []
	if config['imu_cfg'] == 'True' :
		headings              = []

	init_time = time.time()

	while time.time() < init_time + duration :
		measurement_start = time.time()
		motor_control(lhm_power_level,rhm_power_level)
		measurement_times.append(time.time())
		lhm_power_levels.append(lhm_power_level)
		rhm_power_levels.append(rhm_power_level)
		lhm_angular_positions.append(motor_position(PORT_LH_MOTOR))
		rhm_angular_positions.append(motor_position(PORT_RH_MOTOR))
		if config['imu_cfg'] == 'True' :
			headings.append(get_heading())
		time.sleep(sample_rate-float(time.time()-measurement_start))
	motor_stop()

	# write data to mat file
	try :
		outfile = config['file_cfg']['OUT_FILE'] + "lhm-" + str(lhm_power_level) + "_rhm-" + str(rhm_power_level) + "_" + str(int(time.time())) + ".mat"
		if config['imu_cfg'] == 'True' :
			io.savemat(outfile, {"measurement_times"    : measurement_times,
                                             "lhm_power_levels"     : lhm_power_levels,
                                             "rhm_power_levels"     : rhm_power_levels,
                                             "lhm_angular_positions": lhm_angular_positions,
                                             "rhm_angular_positions": rhm_angular_positions,
                                             "headings"             : headings,
                                             })
                else :
 			io.savemat(outfile, {"measurement_times"    : measurement_times,
                                             "lhm_power_levels"     : lhm_power_levels,
                                             "rhm_power_levels"     : rhm_power_levels,
                                             "lhm_angular_positions": lhm_angular_positions,
                                             "rhm_angular_positions": rhm_angular_positions,
                                             })
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
	print("-s <sample_rate> to set the sample rate. Default is {0} secs".format(config['test_defaults_cfg']['SAMPLE_RATE']))
	print("-d <duration> to set the collection durration. Default is {0} secs".format(config['test_defaults_cfg']['DURATION']))
	print("-l <lhm_power_level> to set the power level for the left-hand motor. Default is {0}".format(config['test_defaults_cfg']['LHM_POWER_LEVEL']))
	print("-r <rhm_power_level> to set the power level for the right-hand motor. Default is {0}".format(config['test_defaults_cfg']['RHM_POWER_LEVEL']))

def main(argv) :
	sample_rate     = float(config['test_defaults_cfg']['SAMPLE_RATE'])
	duration        = int(config['test_defaults_cfg']['DURATION'])
	lhm_power_level = int(config['test_defaults_cfg']['LHM_POWER_LEVEL'])
	rhm_power_level = int(config['test_defaults_cfg']['RHM_POWER_LEVEL'])
	try:
		opts, args = getopt.getopt(argv,"hs:d:l:r:",["sample_rate=","duration=","lhm_power_level=","rhm_power_level="])
	except getopt.GetoptError :
		print_help()
		sys.exit(2)
	for opt, arg in opts :
		if opt == '-h' :
			 print_help()
			 sys.exit()
		elif opt in ("-s", "--sample_rate") :
			 sample_rate = float(arg)
		elif opt in ("-d", "--duration") :
			 duration = int(arg)
		elif opt in ("-l", "--lhm_power_level") :
			 lhm_power_level = int(arg)
		elif opt in ("-r", "--rhm_power_level") :
			 rhm_power_level = int(arg)
	print("Sample rate is {0}".format(sample_rate))
	print("Duration is {0} seconds".format(duration))
	print("LHM Power Level is {0}".format(lhm_power_level))
	print("RHM Power Level is {0}".format(rhm_power_level))

	run_characterisation_drive(sample_rate, duration, lhm_power_level, rhm_power_level)


if __name__ == "__main__":
   main(sys.argv[1:])
