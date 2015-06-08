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
# Following code to read data from a USB Optical Mouse
# See: http://www.orangecoat.com/how-to/read-and-decode-data-from-your-mouse-using-this-pyusb-hack
# Requires pyusb to be installed
#---------------------------------------------------------------------------------------

if config['usb_mouse_cfg']['USE_MOUSE'] == 'True' :

	import sys
	import usb.core
	import usb.util
	import usb.control

	# decimal vendor and product values
	dev = usb.core.find(idVendor=int(config['usb_mouse_cfg']['ID_VENDOR']), idProduct=int(config['usb_mouse_cfg']['ID_PRODUCT']))
	# or, uncomment the next line to search instead by the hexidecimal equivalent
	#dev = usb.core.find(idVendor=0x45e, idProduct=0x77d)

	print("configuration: {0}".format(usb.control.get_configuration(dev)))
	print("status: {0}".format(usb.control.get_status(dev)))

	# first endpoint
	interface = 0
	endpoint = dev[0][(0,0)][0]

	def read_mouse() :
		global endpoint
		try :
			data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
			print data
		except usb.core.USBError as e :
			data = None

#---------------------------------------------------------------------------------------
# Following code to read data from a BerryIMU
# See: http://ozzmaker.com/2014/12/11/berryimu/#
# Copied directly from BerryIMU/python-LSM9DS0-gryo-accel-compass/berryIMU.py
#---------------------------------------------------------------------------------------

import smbus
import time
import math
from LSM9DS0 import *
import datetime
bus = smbus.SMBus(1)

import numpy as np

RAD_TO_DEG = 57.29578
M_PI       = np.pi
G_GAIN     = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
LP         = 0.041  # Loop period = 41ms.   This needs to match the time it takes each loop to run
AA         = 0.90   # Complementary filter constant

def writeACC(register,value) :
	bus.write_byte_data(ACC_ADDRESS , register, value)
	return -1

def writeMAG(register,value) :
	bus.write_byte_data(MAG_ADDRESS, register, value)
	return -1

def writeGRY(register,value) :
	bus.write_byte_data(GYR_ADDRESS, register, value)
	return -1

def readACCx() :
	acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_X_L_A)
	acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_X_H_A)
	acc_combined = (acc_l | acc_h <<8)
	return acc_combined  if acc_combined < 32768 else acc_combined - 65536

def readACCy() :
	acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Y_L_A)
	acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Y_H_A)
	acc_combined = (acc_l | acc_h <<8)
	return acc_combined  if acc_combined < 32768 else acc_combined - 65536

def readACCz() :
	acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Z_L_A)
	acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Z_H_A)
	acc_combined = (acc_l | acc_h <<8)
	return acc_combined  if acc_combined < 32768 else acc_combined - 65536

def readMAGx() :
	mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_X_L_M)
	mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_X_H_M)
	mag_combined = (mag_l | mag_h <<8)
	return mag_combined  if mag_combined < 32768 else mag_combined - 65536

def readMAGy() :
	mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_Y_L_M)
	mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_Y_H_M)
	mag_combined = (mag_l | mag_h <<8)
	return mag_combined  if mag_combined < 32768 else mag_combined - 65536

def readMAGz() :
	mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_Z_L_M)
	mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_Z_H_M)
	mag_combined = (mag_l | mag_h <<8)
	return mag_combined  if mag_combined < 32768 else mag_combined - 65536

def readGYRx() :
	gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_X_L_G)
	gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_X_H_G)
	gyr_combined = (gyr_l | gyr_h <<8)
	return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536

def readGYRy():
	gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_Y_L_G)
	gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_Y_H_G)
	gyr_combined = (gyr_l | gyr_h <<8)
	return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536

def readGYRz():
	gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_Z_L_G)
	gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_Z_H_G)
	gyr_combined = (gyr_l | gyr_h <<8)
	return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536

#initialise the accelerometer
writeACC(CTRL_REG1_XM, 0b01100111) #z,y,x axis enabled, continuos update,  100Hz data rate
writeACC(CTRL_REG2_XM, 0b00100000) #+/- 16G full scale

#initialise the magnetometer
writeMAG(CTRL_REG5_XM, 0b11110000) #Temp enable, M data rate = 50Hz
writeMAG(CTRL_REG6_XM, 0b01100000) #+/-12gauss
writeMAG(CTRL_REG7_XM, 0b00000000) #Continuous-conversion mode

#initialise the gyroscope
writeGRY(CTRL_REG1_G, 0b00001111) #Normal power mode, all axes enabled
writeGRY(CTRL_REG4_G, 0b00110000) #Continuos update, 2000 dps full scale

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0


def imu_reading() :

	AccXangle =  (math.atan2(readACCy(),readACCz())+M_PI)*RAD_TO_DEG;
	AccYangle =  (math.atan2(readACCz(),readACCx())+M_PI)*RAD_TO_DEG;

	#Convert Gyro raw to degrees per second
	rate_gyr_x =  readGYRx() * G_GAIN
	rate_gyr_y =  readGYRy() * G_GAIN
	rate_gyr_z =  readGYRz() * G_GAIN

	#Calculate the angles from the gyro. LP = loop period
	gyroXangle+=rate_gyr_x*LP;
	gyroYangle+=rate_gyr_y*LP;
	gyroZangle+=rate_gyr_z*LP;

	#Change the rotation value of the accelerometer to -/+ 180 and move the Y axis '0' point to up.
	#Two different pieces of code are used depending on how your IMU is mounted.
	# if chip is on top use 'up' else use 'down'
	IMU_ORIENTATION = 'down' # or 'up'

	if IMU_ORIENTATION == 'up' :
		# If IMU is up the correct way
		AccXangle -= 180.0
		if AccYangle > 90 :
			AccYangle -= 270.0
		else:
			AccYangle += 90.0
	else :
		# IMU is upside down
		if AccXangle > 180 :
			AccXangle -= 360.0
		AccYangle-=90
		if (AccYangle >180) :
			AccYangle -= 360.0

	#Complementary filter used to combine the accelerometer and gyro values.
	CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle;
	CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle;

#	logger.info("AccXangle: %d, Heading: %d, gyroZangle: %d" % (AccXangle, heading, gyroZangle))

def get_heading() :
	heading = 180 * math.atan2(readMAGy(),readMAGx())/M_PI
	if heading < 0 :
		heading += 360;
#	logger.info("Heading: %d" % (heading))
	return heading


#---------------------------------------------------------------------------------------
# Definition of experiments
#
#---------------------------------------------------------------------------------------

import scipy.io as io
import time

def run_characterisation_drive(sample_rate     = float(config['test_defaults_cfg']['SAMPLE_RATE']),
                               lhm_power_level = int(config['test_defaults_cfg']['LHM_POWER_LEVEL']),
                               rhm_power_level = int(config['test_defaults_cfg']['RHM_POWER_LEVEL'])
                               ) :

	print("Power levels => lhm: {0}, rhm: {1}".format(lhm_power_level,rhm_power_level))

	measurement_times     = []
	lhm_power_levels      = []
	rhm_power_levels      = []
	lhm_angular_positions = []
	rhm_angular_positions = []
	headings              = []

	init_time = time.time()

	while time.time() < init_time + int(config['test_defaults_cfg']['DURATION']) :
		measurement_start.append(time.time())
		motor_control(lhm_power_level,rhm_power_level)
		measurement_times.append(time.time())
		lhm_power_levels.append(lhm_power_level)
		rhm_power_levels.append(rhm_power_level)
		lhm_angular_positions.append(motor_position(PORT_LH_MOTOR))
		rhm_angular_positions.append(motor_position(PORT_RH_MOTOR))
		headings.append(get_heading())
		time.sleep(sample_rate-(time.time()-measurement_start))
	motor_stop()

	# write data to mat file
	try :
		outfile = config['file_cfg']['OUT_FILE'] + "lhm-" + str(lhm_power_level) + "_rhm-" + str(rhm_power_level) + "_" + str(int(time.time())) + ".mat"
		io.savemat(outfile, {"measurement_times"    : measurement_times,
                         "lhm_power_levels"     : lhm_power_levels,
                         "rhm_power_levels"     : rhm_power_levels,
                         "lhm_angular_positions": lhm_angular_positions,
                         "rhm_angular_positions": rhm_angular_positions,
                         "headings"             : headings,
                         })
		print("Recorded data saved to file {0}".format(outfile))
	except :
		print("Failed to write data to file!!")


#---------------------------------------------------------------------------------------
# Run experiments
#
#---------------------------------------------------------------------------------------

import sys, getopt

def main(argv) :
	sample_rate     = float(config['test_defaults_cfg']['SAMPLE_RATE'])
	duration        = int(config['test_defaults_cfg']['DURATION'])
	lhm_power_level = int(config['test_defaults_cfg']['LHM_POWER_LEVEL'])
	rhm_power_level = int(config['test_defaults_cfg']['RHM_POWER_LEVEL'])
	try:
		opts, args = getopt.getopt(argv,"hs:d:l:r:",["sample_rate=","duration=","lhm_power_level=","rhm_power_level="])
	except getopt.GetoptError:
		print 'NXT-motor-data-collection.py -s <sample_rate> -l <lhm_power_level> -r <rhm_power_level>'
		sys.exit(2)
	for opt, arg in opts :
		if opt == '-h':
			 print 'NXT-motor-data-collection.py -s <sample_rate> -l <lhm_power_level> -r <rhm_power_level>'
			 sys.exit()
		elif opt in ("-s", "--sample_rate"):
			 sample_rate = float(arg)
		elif opt in ("-d", "--duration"):
			 duration = int(arg)
		elif opt in ("-l", "--lhm_power_level"):
			 lhm_power_level = int(arg)
		elif opt in ("-r", "--rhm_power_level"):
			 rhm_power_level = int(arg)
	print("Sample rate is {0}".format(sample_rate))
	print("Duration is {0}".format(duration))
	print("LHM Power Level is {0}".format(lhm_power_level))
	print("RHM Power Level is {0}".format(rhm_power_level))

	if config['usb_mouse_cfg']['USE_MOUSE'] == 'True' :
		# if the OS kernel already claimed the device, which is most likely true
		# thanks to http://stackoverflow.com/questions/8218683/pyusb-cannot-set-configuration
		if dev.is_kernel_driver_active(interface) is True :
			# tell the kernel to detach
			dev.detach_kernel_driver(interface)
			# claim the device
			usb.util.claim_interface(dev, interface)

	run_characterisation_drive(sample_rate, lhm_power_level, rhm_power_level)

	if config['usb_mouse_cfg']['USE_MOUSE'] == 'True' :
		# release the device
		usb.util.release_interface(dev, interface)
		# reattach the device to the OS kernel
		dev.attach_kernel_driver(interface)


if __name__ == "__main__":
   main(sys.argv[1:])
