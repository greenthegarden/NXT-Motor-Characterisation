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

# Test Conditions
test_conditions_cfg = {
	'SAMPLE_RATE'     : 0.1,
	'LHM_POWER_LEVEL' : 150,
	'RHM_POWER_LEVEL' : 200,
	}
config['test_conditions_cfg'] = test_conditions_cfg

# file configuration
file_cfg = {
	'LOG_FILE' : "NXT-motor-data-collection.log",
	'OUT_FILE' : "drive_",
	}
config['file_cfg'] = file_cfg


config.write()
