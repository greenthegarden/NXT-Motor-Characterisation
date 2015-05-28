## source:
# https://stackoverflow.com/questions/3089832/sine-wave-glissando-from-one-pitch-to-another-in-numpy

# source:
# https://stackoverflow.com/questions/3089832/sine-wave-glissando-from-one-pitch-to-another-in-numpy
#

from pylab import *

def generate_sinusoidal_signal(sample_rate=0.1, amplitude=255) :
	#sample_rate = .1
	#f0, f1 = .1, 1
	#t_change = 5

	#sample_rate = .1
	f0, f1 = 0.05, 0.5
	t_change = 60

	global times
	times = arange(0, t_change, sample_rate)

	ramp = times / float(t_change)
	#ramp = 1./(1+exp(-6.*(times-t_change)))

	freq = f0*(1-ramp)+f1*ramp
	phase_correction = add.accumulate(times*concatenate((zeros(1), 2*pi*(freq[:-1]-freq[1:]))))

	power_level = float(amplitude)*sin(2*pi*freq*times+phase_correction)

def generate_stepped_signal(sample_rate=0.1, amplitude=255) :

	sample_period = 60

	global power_leve

	times = arange(0, sample_period, sample_rate)

	power_level = []

	for time in times :
		if time < 12 :
			power_level.append(50)
		elif time < 24 :
			power_level.append(100)
		elif time < 36 :
			power_level.append(150)
		elif time < 48 :
			power_level.append(200)
		else :
			power_level.append(250)

	print(len(times))
	print(len(power_level))

	figure()
	plot(times, power_level)

	show()

	import scipy.io as io
	# export data to mat file
	io.savemat("step.mat", {"sample_rate": sample_rate,
													"times"      : times,
													"power"      : power_level
													})


#---------------------------------------------------------------------------------------
# Generate Plots
#
#---------------------------------------------------------------------------------------

def plot_signal() :

	figure()
#	subplot(211)
#	plot(times, freq)
#	subplot(212)
	plot(times, power_level)

	show()


#---------------------------------------------------------------------------------------
# Export data to mat file
#
#---------------------------------------------------------------------------------------

def export_signal() :
	import scipy.io as io
	# export data to mat file
	io.savemat("signal.mat", {"sample_rate": sample_rate,
														"times"      : times,
														"power"      : power_level
														})


#---------------------------------------------------------------------------------------
# Program execution starts here
#
#---------------------------------------------------------------------------------------


run_generate_sinusoidal_signal = False
run_generate_stepped_signal = True

if run_generate_sinusoidal_signal :
	generate_sinusoidal_signal()
if run_generate_stepped_signal :
	generate_stepped_signal()

