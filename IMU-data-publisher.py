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
bus = smbus.SMBus(1)

#import time
from LSM9DS0 import *
#import datetime


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

def readGYRz() :
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
# Collect and publish sensor data
#
#---------------------------------------------------------------------------------------

import math

import numpy as np

M_PI       = np.pi
RAD_TO_DEG = 180.0/M_PI
G_GAIN     = float(config['imu_cfg']['G_GAIN']) # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
LP         = float(config['imu_cfg']['LP'])     # Loop period = 41ms.   This needs to match the time it takes each loop to run
AA         = float(config['imu_cfg']['AA'])     # Complementary filter constant

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0

#Change the rotation value of the accelerometer to -/+ 180 and move the Y axis '0' point to up.
#Two different pieces of code are used depending on how your IMU is mounted.
# if chip is on top use 'up' else use 'down'
IMU_ORIENTATION = str(config['imu_cfg']['IMU_ORIENTATION']).lower()

import time
MEASUREMENT_INTERVAL = float(config['imu_cfg']['MEASUREMENT_INTERVAL'])

while True :
	measurement_time = time.time()

	#Read accelerometer,gyroscope and magnetometer  values
	ACCx = readACCx()
	ACCy = readACCy()
	ACCz = readACCz()
	GYRx = readGYRx()
	GYRy = readGYRx()
	GYRz = readGYRx()
	MAGx = readMAGx()
	MAGy = readMAGy()
	MAGz = readMAGz()

	##Convert Accelerometer values to degrees
	AccXangle =  (math.atan2(ACCy,ACCz)+M_PI)*RAD_TO_DEG
	AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG

	#Convert Gyro raw to degrees per second
	rate_gyr_x =  GYRx * G_GAIN
	rate_gyr_y =  GYRy * G_GAIN
	rate_gyr_z =  GYRz * G_GAIN

	#Calculate the angles from the gyro. LP = loop period
	gyroXangle+=rate_gyr_x*LP
	gyroYangle+=rate_gyr_y*LP
	gyroZangle+=rate_gyr_z*LP

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
    CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
    CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle

	#Calculate heading
	heading = 180 * math.atan2(MAGy,MAGx)/M_PI
	if heading < 0:
	 	heading += 360

	#Normalize accelerometer raw values.
    accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
	accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)

	#Calculate pitch and roll
	pitch = math.asin(accXnorm)
	roll = -math.asin(accYnorm/math.cos(pitch))

	#Calculate the new tilt compensated values
	magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
	magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)

	#Calculate tiles compensated heading
    tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI
    if tiltCompensatedHeading < 0:
    	tiltCompensatedHeading += 360

	client.publish("pibot/imu/accxangle", str({'value':'{0:.3f}'.format(AccXangle), 'time':measurement_time}))
	client.publish("pibot/imu/accyangle", str({'value':'{0:.3f}'.format(AccYangle), 'time':measurement_time}))
	client.publish("pibot/imu/rate_gyr_x", str({'value':'{0:.3f}'.format(rate_gyr_x), 'time':measurement_time}))
	client.publish("pibot/imu/rate_gyr_y", str({'value':'{0:.3f}'.format(rate_gyr_y), 'time':measurement_time}))
	client.publish("pibot/imu/rate_gyr_z", str({'value':'{0:.3f}'.format(rate_gyr_z), 'time':measurement_time}))
	client.publish("pibot/imu/gyroxangle", str({'value':'{0:.3f}'.format(gyroXangle), 'time':measurement_time}))
	client.publish("pibot/imu/gyroyangle", str({'value':'{0:.3f}'.format(gyroYangle), 'time':measurement_time}))
	client.publish("pibot/imu/gyrozangle", str({'value':'{0:.3f}'.format(gyroZangle), 'time':measurement_time}))
	client.publish("pibot/imu/cfanglex", str({'value':'{0:.3f}'.format(CFangleX), 'time':measurement_time}))
	client.publish("pibot/imu/cfangley", str({'value':'{0:.3f}'.format(CFangleY), 'time':measurement_time}))
	client.publish("pibot/imu/heading", str({'value':'{0:.1f}'.format(heading), 'time':measurement_time}))
	client.publish("pibot/imu/accxnorm", str({'value':'{0:.1f}'.format(accXnorm), 'time':measurement_time}))
	client.publish("pibot/imu/accynorm", str({'value':'{0:.1f}'.format(accYnorm), 'time':measurement_time}))
	client.publish("pibot/imu/pitch", str({'value':'{0:.1f}'.format(pitch*RAD_TO_DEG), 'time':measurement_time}))
	client.publish("pibot/imu/roll", str({'value':'{0:.1f}'.format(roll*RAD_TO_DEG), 'time':measurement_time}))
	client.publish("pibot/imu/magxcomp", str({'value':'{0:.1f}'.format(magXcomp), 'time':measurement_time}))
	client.publish("pibot/imu/magycomp", str({'value':'{0:.1f}'.format(magYcomp), 'time':measurement_time}))
	client.publish("pibot/imu/tiltcompensatedheading", str({'value':'{0:.1f}'.format(tiltCompensatedHeading), 'time':measurement_time}))

	time.sleep(MEASUREMENT_INTERVAL-(time.time()-measurement_time))
