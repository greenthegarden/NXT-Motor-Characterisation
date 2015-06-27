# config file creator

from configobj import ConfigObj
config = ConfigObj()
config.filename = 'NXT-motor-data-collection.cfg'


# MQTT config
mqtt_cfg = {
	'MQTT_BROKER_IP'           : "localhost",
	'MQTT_BROKER_PORT'         : "1883",
	'MQTT_BROKER_PORT_TIMEOUT' : "60",
	}
config['mqtt_cfg'] = mqtt_cfg

# Motor Ports
motor_ports_cfg = {
	'PORT_LH_MOTOR' : "PORT_D",
	'PORT_RH_MOTOR' : "PORT_A",
	}
config['motor_ports_cfg'] = motor_ports_cfg

# Motor Specifications
motor_spec_cfg = {
	'POWER_MAX' : 255,
	'POWER_MIN' : 70,
	}
config['motor_spec_cfg'] = motor_spec_cfg

nxt_sensor_cfg = {
	'MEASUREMENT_INTERVAL' : 1.0,
	}
config['nxt_sensor_cfg'] = nxt_sensor_cfg

# USB Mouse Specifications
usb_mouse_cfg = {
	'USE_MOUSE'  : 'False',
	'ID_VENDOR'  : 1118,
	'ID_PRODUCT' : 57,
	}
config['usb_mouse_cfg'] = usb_mouse_cfg

# IMU Configuration
imu_cfg = {
	'USE_IMU'              : 'False',
	'MEASUREMENT_INTERVAL' : 1.0,
	'IMU_ORIENTATION'      : 'down',
	'G_GAIN'               : 0.070,
	'LP'                   : 0.1,  # Loop period = 41ms.   This needs to match the time it takes each loop to run
        'AA'                   : 0.90,
	}
config['imu_cfg'] = imu_cfg

# Test Conditions
test_defaults_cfg = {
	'SAMPLE_RATE'     : 0.1,
	'DURATION'        : 10,
	'LHM_POWER_LEVEL' : 150,
	'RHM_POWER_LEVEL' : 200,
	}
config['test_defaults_cfg'] = test_defaults_cfg

# file configuration
file_cfg = {
	'LOG_FILE'       : "NXT-motor-data-collection.log",
	'SAMPLE_FILE'    : "signal.mat",
	'WRITE_OUT_FILE' : "False",
	'OUT_FILE'       : "drive_",
	'MC_OUT'         : "output_"
	}
config['file_cfg'] = file_cfg


config.write()
