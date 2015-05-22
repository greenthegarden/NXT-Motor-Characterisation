## source:
# https://stackoverflow.com/questions/3089832/sine-wave-glissando-from-one-pitch-to-another-in-numpy

# source:
# https://stackoverflow.com/questions/3089832/sine-wave-glissando-from-one-pitch-to-another-in-numpy
#

from pylab import *

#sample_rate = .1
#f0, f1 = .1, 1
#t_change = 5

sample_rate = .1
f0, f1 = 0.05, 0.5
t_change = 60

times = arange(0, t_change, sample_rate)

ramp = times / float(t_change)
#ramp = 1./(1+exp(-6.*(times-t_change)))

freq = f0*(1-ramp)+f1*ramp
phase_correction = add.accumulate(times*concatenate((zeros(1), 2*pi*(freq[:-1]-freq[1:]))))

power_level = 255*sin(2*pi*freq*times+phase_correction)


#---------------------------------------------------------------------------------------
# Generate Plots
#
#---------------------------------------------------------------------------------------

figure()
subplot(211)
plot(times, freq)
subplot(212)
plot(times, power_level)

show()


#---------------------------------------------------------------------------------------
# Export data to mat file
#
#---------------------------------------------------------------------------------------

import scipy.io as io
# export data to mat file
io.savemat("signal.mat", {"sample_rate": sample_rate,
                          "times"      : times,
                          "power"      : power_level
                          })
