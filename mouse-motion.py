#!/usr/bin/env python

from evdev import InputDevice, categorize, ecodes, RelEvent
from select import select
import struct

dev = InputDevice('/dev/input/event0')

print(dev)

#for event in dev.read_loop() :
#	print(categorize(event))
#	if event.type == ecodes.REL_X :
#		print("Found")
#		print(RelEvent(event))
#	if event.type == ecodes.REL_Y :
#		print(RelEvent(event))
x_dir_motion = []
x_dir_times = []
y_dir_motion = []
y_dir_times = []
test = True
while True :
	if test :
#	try :
		r,w,x = select([dev], [], [])
		for event in dev.read() :
			print(event)
#			print(event.sec)
#			print(event.usec)
			event_time = event.sec + (event.usec*0.000001)
			print(event_time)
#			print("r = {0}".format(r))
#			print("w = {0}".format(w))
#			print("x = {0}".format(x))
#			print("event.type = {0}".format(event.type))
			if event.type == 2 :
				print("Moving mouse")
#				print("event.code = {0}".format(event.code))
				if event.code == 0 :
					print("Moving in y dir") 
					y_dir_times.append(event_time)
					y_dir_motion.append(event.value)
				if event.code == 1 :
					print("Moving in x dir") 
					x_dir_times.append(event_time)
					x_dir_motion.append(event.value)
				print("event.value = {0}".format(event.value))
#	except KeyboardInterrupt :
#		print("{0}".format(x_dir_motion))
#		print("{0}".format(y_dir_motion))
#		print("Bye!!")
#		break

#long int, long int, unsigned short, unsigned short, unsigned int
#FORMAT = 'llHHI'
#
#for event in dev.read_loop() :
#	print(categorize(event))
#	print(event)
#	(tv_sec, tv_usec, type, code, value) = struct.unpack(FORMAT, event)
#
#	if type != 0 or code != 0 or value != 0:
#		print("Event type %u, code %u, value: %u at %d, %d" % \
#			(type, code, value, tv_sec, tv_usec))
#	else:
#		# Events with code, type and value == 0 are "separator" events
#		print("===========================================")

