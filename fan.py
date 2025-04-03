#!/path/to/new/virtual/environment  ####/path/to/new/virtual/environment
# virtual inviroment needed for rpi_hardware_pwm pip install.

# Created by: Thomas Kunchick 
# Inspired by Michael Klements - https://www.the-diy-life.com/connecting-a-pwm-fan-to-a-raspberry-pi/
# For 120mm 12V PWM Fan Control On A Raspberry Pi5 with POE-NVME Hat
# Sets fan speed proportional to CPU temperature - best for good quality fans

from rpi_hardware_pwm import HardwarePWM
import time                                # Calling time to allow delays to be used
import subprocess                          # Calling subprocess to get the CPU temperatures


pwm = HardwarePWM(2, 1500, chip=2)         # channel 0 1 2 3 for GPIO12 13 18 19 respectively?? Working on channel 2 for some reason (RaspPi5)
                                           # 1500 = hz
                                           # chip=2 This indicates that the PWM channel is mapped to the PWM chip 2
                                           # which controls GPIO 12 and 13. For Rpi 1,2,3,4, use chip=0; For Rpi 5, use chip=2
pwm.start(50)                              # Start PWM with a 50% duty cycle

## other commands for Hardware PWM
##
## pwm.change_duty_cycle(75)               # Change duty cycle to 75% 
## pwm.change_frequency(500)               # Change frequency to 500 Hz
## pwm.stop()                              # Stop PWM

minTemp = 40                               # Temperature and speed range variables, edit these to adjust max and min temperatures and speeds
maxTemp = 55
minSpeed = 0
maxSpeed = 100

pi_list = ["pi1", "pi2", "pi3"]            # Pi list to check - must have SSH keys installed. Edit as needed.
u = "user@"                                # User id to log into with. Edit as needed.
temp=0

def get_temp():                            # Function to read in the CPU temperature and return it as a float in degrees celcius

    temp=0
    for pi in pi_list:
        ssh_now="{}{}".format (u, pi)
        pi_temp = subprocess.run(['ssh', ssh_now, 'vcgencmd', 'measure_temp'], capture_output=True)  # Celsius
        temp_str = pi_temp.stdout.decode()
        try: 
            if temp <= float(temp_str.split('=')[1].split('\'')[0]):
                   temp = float(temp_str.split('=')[1].split('\'')[0])
        except (IndexError, ValueError):
                raise RuntimeError('Could not get temperature')
    return (temp)

def renormalize(n, range1, range2):         # Function to scale the read temperature to the fan speed range
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (n - range1[0]) / delta1) + range2[0]

while 1:                                    # Execute loop forever
    temp = get_temp()                       # Get the current CPU temperatures
    if temp < minTemp:                      # Constrain temperature to set range limits
        temp = minTemp
    elif temp > maxTemp:
        temp = maxTemp
    temp = int(renormalize(temp, [minTemp, maxTemp], [minSpeed, maxSpeed]))
    pwm.change_duty_cycle(temp)             # Set fan duty based on temperature, from minSpeed to maxSpeed
    time.sleep(5)                           # Sleep for 5 seconds
