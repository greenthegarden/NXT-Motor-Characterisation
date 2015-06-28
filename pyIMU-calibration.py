#!/usr/bin/env python

from pyberryimu.client import BerryIMUClient
from pyberryimu.calibration.standard import StandardCalibration

sc = StandardCalibration(verbose=True)
c  = BerryIMUClient(bus=1)
sc.calibrate_accelerometer(c)
c.calibration_object = sc
sc.save(save_path='/home/pi/.pyberryimu')
