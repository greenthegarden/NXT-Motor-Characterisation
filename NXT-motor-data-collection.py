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

port_lh_motor = PORT_D
port_rh_motor = PORT_A

# Define motors
BrickPi.MotorEnable[port_lh_motor] = 1 #Enable the left drive motor
BrickPi.MotorEnable[port_rh_motor] = 1 #Enable the right drive motor

POWER_MAX = 255
POWER_MIN = 70

def motor_control(powerLeft, powerRight) :
	BrickPi.MotorSpeed[port_lh_motor] = powerLeft
	BrickPi.MotorSpeed[port_rh_motor] = powerRight
	BrickPiUpdateValues()

def drive_forward(power_level) :
	motorControl(power_level,power_level)

def drive_backwards(power_level) :
	motor_control(-power_level, -power_level)

import angles

def sharp_turn_left() :
	motor_control(-POWER_MAX,POWER_MAX)

def sharp_turn_right() :
	motor_control(POWER_MAX,-POWER_MAX)

def turn_left(power) :
	motor_control(power, 0)

def turn_right(power) :
	motor_control(0, power)

# def turn_by_degrees(degrees) :
# 	initial_heading = angles.Angle(get_heading())
# 	required_heading = initial_heading + angles.Angle(degrees)
# 	if degrees > 0 :
# 		while heading - initiaal_heading > 0		# turn to right
# 			turn_right()
# 	if degrees < 0 ;
# 		while heading - initiaal_heading > 0		# turn to right
# 			turn_left()
#
# def turn_to_heading(requested_heading) :
# 	current_heading = get_heading()
# 	if not current_heading > (requested_heading - 1) and current_heading < (requested_heading + 1) :
# 		turn_by_degrees()

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


import numpy as np

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

def run_characterisation_drive(mode) :

	print("Load input power level signal from file {0}".format("signal.mat"))
	# import signal data from mat file
	signal = io.loadmat("signal.mat",squeeze_me=True)
	# extract data from signal data
	sample_rate   = signal['sample_rate']
	times         = signal['times']
	power_samples = signal['power']

	print("Starting NXT drive test")


	# create array for store results
	measurement_times     = []
	power_levels          = []
	lhm_angular_positions = []
	rhm_angular_positions = []
	headings              = []
	for power_sample in power_samples :
		if mode == "drive" :
			motor_control(int(power_sample),int(power_sample))
		elif mode == "left" :
			motor_control(int(power_sample),0)
		elif mode == "right" :
			motor_control(int(power_sample),0)
		measurement_times.append(time.time())
		power_levels.append(power_sample)
		lhm_angular_positions.append(motor_position(port_lh_motor))
		rhm_angular_positions.append(motor_position(port_rh_motor))
		headings.append(get_heading())
		time.sleep(sample_rate)
	motor_stop()

	# write data to mat file
	try :
		io.savemat("output.mat", {"measurement_times"    : measurement_times,
                              "power_levels"         : power_levels,
                              "rhm_angular_positions": rhm_angular_positions,
                              "lhm_angular_positions": lhm_angular_positions,
                              "headings"             : headings,
                              })
		print("Recorded data saved to file {0}".format("output.mat"))
	except :
		print("Failed to write data to file!!")

def run_characterisation_driving(sample_rate=0.1, lhm_power_level = 200, rhm_power_level = 150) :

#	lhm_power_level = 200
#	rhm_power_level = 150

	sample_times = np.arange(0, 10, sample_rate)

	measurement_times     = []
	lhm_power_levels      = []
	rhm_power_levels      = []
	lhm_angular_positions = []
	rhm_angular_positions = []
	headings              = []

	for sample_time in sample_times :
		motor_control(lhm_power_level,rhm_power_level)
		measurement_times.append(time.time())
		lhm_power_levels.append(lhm_power_level)
		rhm_power_levels.append(rhm_power_level)
		lhm_angular_positions.append(motor_position(port_lh_motor))
		rhm_angular_positions.append(motor_position(port_rh_motor))
		headings.append(get_heading())
		time.sleep(sample_rate)
	motor_stop()

	# write data to mat file
	try :
		io.savemat("drive.mat", {"measurement_times"    : measurement_times,
														 "lhm_power_levels"     : lhm_power_levels,
														 "rhm_power_levels"     : rhm_power_levels,
														 "lhm_angular_positions": lhm_angular_positions,
														 "rhm_angular_positions": rhm_angular_positions,
														 "headings"             : headings,
														 })
	print("Recorded data saved to file {0}".format("drive.mat"))
	except :
		print("Failed to write data to file!!")


#---------------------------------------------------------------------------------------
# Run experiments
#
#---------------------------------------------------------------------------------------

drive_forward_characterisation = False
turn_left_characterisation = False
turn_right_characterisation = False
drive = True

if drive_forward_characterisation :
	run_characterisation_drive("forward")
if turn_left_characterisation :
	run_characterisation_drive("left")
if turn_right_characterisation :
	run_characterisation_drive("right")

if drive :
	run_characterisation_driving(sample_rate=0.1, lhm_power_level = 200, rhm_power_level = 150)
