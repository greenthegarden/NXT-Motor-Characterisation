# config file creator

from configobj import ConfigObj
config = ConfigObj()
config.filename = 'NXT-motor-characterisation-analysis.cfg'


# Robot specifics
robot_specifics_cfg = {
	'WHEEL_DIAMETER' : 56,	# in mm
	}
config['robot_specifics_cfg'] = robot_specifics_cfg

# recorded file field indexes
results_index_cfg = {
	'PORT_IDX'              : 0,
	'MEASUREMENT_TIMES_IDX' : 1,
	'POWER_LEVELS_IDX'      : 2,
	'ANGULAR_POSITIONS_IDX' : 3,
	}
config['results_index_cfg'] = results_index_cfg


config.write()
