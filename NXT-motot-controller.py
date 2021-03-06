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
# Modules and methods to support MQTT
#
#---------------------------------------------------------------------------------------

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc) :

	print("Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if the connection is lost
	# the subscriptions will be renewed when reconnecting.

	print("Subscribing to topics ...")
	for topic in config['mqtt_topics']['TOPICS'] :
		client.subscribe(topic)
		print("{0}".format(topic))

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
# Definition of experiments
#
#---------------------------------------------------------------------------------------

def run_nxt_motor_contoller(sample_interval = float(config['test_defaults_cfg']['SAMPLE_RATE'])) :
	while True:
		measurement_start = time.time()
		result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors
		if not result :
			client.publish("pibot/sensor/ultrasonic", '{0:.1f}'.format(BrickPi.Sensor[PORT_1]))
			print BrickPi.Sensor[PORT_1]     #BrickPi.Sensor[PORT] stores the value obtained from sensor
		time.sleep(sample_interval-(time.time()-measurement_start))


#---------------------------------------------------------------------------------------
# Run experiments
#
#---------------------------------------------------------------------------------------

import sys, getopt, os

def print_help() :
	print("{0}".format(os.path.basename(__file__)))
	print("-s <sample_interval> to set the sample interval. Default is {0} secs".format(config['test_defaults_cfg']['SAMPLE_RATE']))

def main(argv) :
	sample_rate = float(config['test_defaults_cfg']['SAMPLE_RATE'])
	try :
		opts, args = getopt.getopt(argv,"hs:",["sample_interval="])
	except getopt.GetoptError:
		print_help()
		sys.exit(2)
	for opt, arg in opts :
		if opt == '-h' :
			 print_help()
			 sys.exit()
		elif opt in ("-s", "--sample_interval") :
			 sample_interval = float(arg)
	print("Sample rate is {0}".format(sample_interval))

	run_nxt_motor_contoller(sample_interval)


if __name__ == "__main__":
   main(sys.argv[1:])
