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
# Modules and methods to support MQTT
#
#---------------------------------------------------------------------------------------

from pyberryimu.client import BerryIMUClient
from pyberryimu.calibration.standard import StandardCalibration

sc = StandardCalibration.load()

with BerryIMUClient(bus=1) as c :
	c.calibration_object = sc

	while True :

		acc  = c.read_accelerometer()
		gyro = c.read_gyroscope()
		mag  = c.read_magnetometer()
		pr   = c.read_pressure()
		temp = c.read_temperature()

		client.publish("pibot/imu/acc", str({'value':acc, 'time':measurement_time}))
		client.publish("pibot/imu/gyro", str({'value':gyro, 'time':measurement_time}))
		client.publish("pibot/imu/mag", str({'value':mag, 'time':measurement_time}))
		client.publish("pibot/imu/pr", str({'value':'{0:.1f}'.format(pr), 'time':measurement_time}))
		client.publish("pibot/imu/temp", str({'value':'{0:.1f}'.format(temp), 'time':measurement_time}))
