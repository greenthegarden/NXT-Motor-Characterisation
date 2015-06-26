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
G_GAIN     = float(config['imu_cfg']['G_GAIN']) # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
LP         = float(config['imu_cfg']['LP'])     # Loop period = 41ms.   This needs to match the time it takes each loop to run
AA         = float(config['imu_cfg']['AA'])     # Complementary filter constant

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

#Change the rotation value of the accelerometer to -/+ 180 and move the Y axis '0' point to up.
#Two different pieces of code are used depending on how your IMU is mounted.
# if chip is on top use 'up' else use 'down'
IMU_ORIENTATION = str(config['imu_cfg']['IMU_ORIENTATION']).lower()


#---------------------------------------------------------------------------------------
# Modules and methods to support MQTT
#
#---------------------------------------------------------------------------------------

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc) :

	print("Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if the connection is lost
	# the subscriptions will be renewed when reconnecting.

# 	print("Subscribing to topics ...")
# 	for topic in config['mqtt_topics']['TOPICS'] :
# 		client.subscribe(topic)
# 		print("{0}".format(topic))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg) :
	print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()

client.connect(config['mqtt_cfg']['MQTT_BROKER_IP'],
               int(config['mqtt_cfg']['MQTT_BROKER_PORT']),
               int(config['mqtt_cfg']['MQTT_BROKER_PORT_TIMEOUT'])
               )

print("Connected to MQTT broker at {0}".format(config['mqtt_cfg']['MQTT_BROKER_IP']))

# link to callback functions
client.on_connect = on_connect
client.on_message = on_message

client.loop_start()


#---------------------------------------------------------------------------------------
# Definition of experiments
#
#---------------------------------------------------------------------------------------

while True:
	measurement_start = time.time()

	AccXangle =  (math.atan2(readACCy(),readACCz())+M_PI)*RAD_TO_DEG;
	client.publish("pibot/imu/accxangle", str({'value':'{0:.3f}'.format(AccXangle), 'time':time.time()}))

	AccYangle =  (math.atan2(readACCz(),readACCx())+M_PI)*RAD_TO_DEG;
	client.publish("pibot/imu/accyangle", str({'value':'{0:.3f}'.format(AccYangle), 'time':time.time()}))

	#Convert Gyro raw to degrees per second
	rate_gyr_x =  readGYRx() * G_GAIN
	client.publish("pibot/imu/rate_gyr_x", str({'value':'{0:.3f}'.format(rate_gyr_x), 'time':time.time()}))

	rate_gyr_y =  readGYRy() * G_GAIN
	client.publish("pibot/imu/rate_gyr_y", str({'value':'{0:.3f}'.format(rate_gyr_y), 'time':time.time()}))

	rate_gyr_z =  readGYRz() * G_GAIN
	client.publish("pibot/imu/rate_gyr_z", str({'value':'{0:.3f}'.format(rate_gyr_z), 'time':time.time()}))


	#Calculate the angles from the gyro. LP = loop period
	gyroXangle+=rate_gyr_x*LP;
	client.publish("pibot/imu/gyroxangle", str({'value':'{0:.3f}'.format(gyroXangle), 'time':time.time()}))

	gyroYangle+=rate_gyr_y*LP;
	client.publish("pibot/imu/gyroyangle", str({'value':'{0:.3f}'.format(gyroYangle), 'time':time.time()}))

	gyroZangle+=rate_gyr_z*LP;
	client.publish("pibot/imu/gyrozangle", str({'value':'{0:.3f}'.format(gyroZangle), 'time':time.time()}))

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
	client.publish("pibot/imu/cfanglex", str({'value':'{0:.3f}'.format(CFangleX), 'time':time.time()}))

	CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle;
	client.publish("pibot/imu/cfangley", str({'value':'{0:.3f}'.format(CFangleY), 'time':time.time()}))

#	logger.info("AccXangle: %d, Heading: %d, gyroZangle: %d" % (AccXangle, heading, gyroZangle))

	heading = 180 * math.atan2(readMAGy(),readMAGx())/M_PI
	if heading < 0 :
		heading += 360;
	client.publish("pibot/imu/heading", str({'value':'{0:.1f}'.format(heading), 'time':time.time()}))
#	logger.info("Heading: %d" % (heading))

	time.sleep(LP-(time.time()-measurement_start))

