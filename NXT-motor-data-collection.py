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
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
LP = 0.041      # Loop period = 41ms.   This needs to match the time it takes each loop to run
AA =  0.90      # Complementary filter constant

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

	heading = 180 * math.atan2(readMAGy(),readMAGx())/M_PI

	if heading < 0 :
		heading += 360;

	logger.info("AccXangle: %d, Heading: %d, gyroZangle: %d" % (AccXangle, heading, gyroZangle))


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

import time

def motor_characterisation() :

	# load signal
	import scipy.io as io
	# import data from mat file
	signal = io.loadmat("signal.mat", squeeze_me=True)

	sample_rate  = signal['sample_rate']
	times        = signal['times']
	power_levels = signal['power']

	print "Power levels loaded"
	print "Running motors"

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

#---------------------------------------------------------------------------------------
# Run experiments
#
#---------------------------------------------------------------------------------------

encoder_calibration = True
motor_characterisation = True

encoder_calibration()
motor_characterisation()
