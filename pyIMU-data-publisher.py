#!/usr/bin/env python

from pyberryimu.client import BerryIMUClient

with BerryIMUClient(bus=1) as c :
	acc  = c.read_accelerometer()
	gyro = c.read_gyroscope()
	mag  = c.read_magnetometer()
	pr   = c.read_pressure()
	temp = c.read_temperature()

	print(temp)
