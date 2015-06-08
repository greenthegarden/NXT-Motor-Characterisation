#!/usr/bin/env python

from evdev import InputDevice, categorize, ecodes, RelEvent

dev = InputDevice('/dev/input/event0')

print(dev)

for event in dev.read_loop() :
	if event.type == ecodes.REL_X :
		print(categorize(event))
		print(RelEvent(event))
	if event.type == ecodes.REL_Y :
		print(categorize(event))
		print(RelEvent(event))
