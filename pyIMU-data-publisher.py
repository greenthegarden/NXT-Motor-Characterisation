#!/usr/bin/env python

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

#		print(acc)
		print(gyro)
#		print(mag)
#		print(pr)
#		print(temp)
