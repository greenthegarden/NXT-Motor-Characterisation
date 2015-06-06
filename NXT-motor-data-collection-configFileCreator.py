# config file creator

from configobj import ConfigObj
config = ConfigObj()
config.filename = 'NXT-motor-data-collection.cfg'


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

# USB Mouse Specifications
usb_mouse_cfg = {
	'USE_MOUSE'  : 'True'
	'ID_VENDOR'  : 1118,
	'ID_PRODUCT' : 57,
	}
config['usb_mouse_cfg'] = usb_mouse_cfg

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
	'LOG_FILE'    : "NXT-motor-data-collection.log",
	'SAMPLE_FILE' : "signal.mat",
	'OUT_FILE'    : "drive_",
	'MC_OUT'      : "output_"
	}
config['file_cfg'] = file_cfg


config.write()
