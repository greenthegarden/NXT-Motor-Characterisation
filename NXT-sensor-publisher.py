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

PORT_SENSOR_ULTRASONIC = PORT_1

# Define sensors
BrickPi.SensorType[PORT_SENSOR_ULTRASONIC] = TYPE_SENSOR_ULTRASONIC_CONT   #Set the type of sensor at PORT_1

#Send the properties of sensors to BrickPi
BrickPiSetupSensors()


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

client.connect(config['mqtt_configuration']['MQTT_BROKER_IP'],
               int(config['mqtt_configuration']['MQTT_BROKER_PORT']),
               int(config['mqtt_configuration']['MQTT_BROKER_PORT_TIMEOUT'])
               )

print("Connected to MQTT broker at {0}".format(config['mqtt_configuration']['MQTT_BROKER_IP']))

# link to callback functions
client.on_connect = on_connect
client.on_message = on_message

client.loop_start()


#---------------------------------------------------------------------------------------
# Collect and publish sensor data
#
#---------------------------------------------------------------------------------------

import time

MEASUREMENT_INTERVAL = float(config['nxt_sensor_cfg']['MEASUREMENT_INTERVAL'])

while True:
	measurement_start = time.time()

	result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors
	if not result :
		client.publish("pibot/nxt_sensor/ultrasonic", str({'value':'{0:.1f}'.format(BrickPi.Sensor[PORT_SENSOR_ULTRASONIC]), 'time':time.time()}))
#		print BrickPi.Sensor[PORT_SENSOR_ULTRASONIC]     #BrickPi.Sensor[PORT] stores the value obtained from sensor

	time.sleep(MEASUREMENT_INTERVAL-(time.time()-measurement_start))
