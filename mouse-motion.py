#!/usr/bin/env python

from evdev import InputDevice, categorize, ecodes, RelEvent
from select import select
import struct

dev = InputDevice('/dev/input/event0')

print(dev)

#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'

#for event in dev.read_loop() :
#	print(categorize(event))
#	if event.type == ecodes.REL_X :
#		print("Found")
#		print(RelEvent(event))
#	if event.type == ecodes.REL_Y :
#		print(RelEvent(event))

while True :
	r,w,x = select([dev], [], [])
	for event in dev.read() :
		print(event)
		print("r = {0}".format(r))
		print("w = {0}".format(w))
		print("x = {0}".format(x))
		print("event.type = {0}".format(event.type))
		print("event.code = {0}".format(event.code))
		print("event.value = {0}".format(event.value))

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

