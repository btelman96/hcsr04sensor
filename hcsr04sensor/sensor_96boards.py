'''Measure the distance or depth with an HCSR04 Ultrasonic sound 
sensor and a 96Boards compatible device.  Imperial and Metric measurements are available'''

# Al Audet
# MIT License
# Modified by Brendon Telman for 96Boards support. Tested on Dragonboard 410C

import time
import math
from gpio_96boards import GPIO


class Measurement(object):
    '''Create a measurement using a HC-SR04 Ultrasonic Sensor connected to 
    the GPIO pins of a 96Boards compatible device
    trig_pin and echo_pin calls MUST be the id of the GPIO ex. 36, which is pin 23 on the Dragonboard 410c
    Metric values are used by default. For imperial values use
    unit='imperial'
    temperature=<Desired temperature in Fahrenheit>
    '''

    def __init__(self,
                 trig_pin,
                 echo_pin,
                 temperature=20,
                 unit='metric',
                 round_to=1
                 ):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.temperature = temperature
        self.unit = unit
        self.round_to = round_to
        self.pins = (
            (self.trig_pin, 'out'),
            (self.echo_pin, 'in')
        )

    def raw_distance(self, sample_size=11, sample_wait=0.1):
        '''Return an error corrected unrounded distance, in cm, of an object 
        adjusted for temperature in Celcius.  The distance calculated
        is the median value of a sample of `sample_size` readings.

        
        Speed of readings is a result of two variables.  The sample_size
        per reading and the sample_wait (interval between individual samples).

        Example: To use a sample size of 5 instead of 11 will increase the 
        speed of your reading but could increase variance in readings;

        value = sensor.Measurement(trig_pin, echo_pin)
        r = value.raw_distance(sample_size=5)
        
        Adjusting the interval between individual samples can also
        increase the speed of the reading.  Increasing the speed will also
        increase CPU usage.  Setting it too low will cause errors.  A default
        of sample_wait=0.1 is a good balance between speed and minimizing 
        CPU usage.  It is also a safe setting that should not cause errors.
        
        e.g.

        r = value.raw_distance(sample_wait=0.03)
        '''
        
        ''' 
                            96Boards logic
                  We have to put all pins we are accesing in a list,
                  So we can use the 'with' call
        '''
        
        
        if self.unit == 'imperial':
            self.temperature = (self.temperature - 32) * 0.5556
        elif self.unit == 'metric':
            pass
        else:
            raise ValueError(
                'Wrong Unit Type. Unit Must be imperial or metric')

        speed_of_sound = 331.3 * math.sqrt(1+(self.temperature / 273.15))
        sample = []
        # setup input/output pins
        with GPIO(self.pins) as GPIO
            for distance_reading in range(sample_size):
                GPIO.digital_write(self.trig_pin, GPIO.LOW)
                time.sleep(sample_wait)
                GPIO.digital_write(self.trig_pin, GPIO.HIGH)
                time.sleep(0.00001)
                GPIO.digital_write(self.trig_pin, GPIO.LOW)
                echo_status_counter = 1
                while GPIO.digital_read(self.echo_pin) == 0:
                    if echo_status_counter < 1000:
                        sonar_signal_off = time.time()
                        echo_status_counter += 1
                    else:
                        raise SystemError('Echo pulse was not received')
                while GPIO.digital_read(self.echo_pin) == 1:
                    sonar_signal_on = time.time()
                time_passed = sonar_signal_on - sonar_signal_off
                distance_cm = time_passed * ((speed_of_sound * 100) / 2)
                sample.append(distance_cm)
            sorted_sample = sorted(sample)
            # Only cleanup the pins used to prevent clobbering
            # any others in use by the program
            # TODO is there a cleanup for this library, if so, now may be a good time to use it
            return sorted_sample[sample_size // 2]

    def depth_metric(self, median_reading, hole_depth):
        '''Calculate the rounded metric depth of a liquid. hole_depth is the
        distance, in cm's, from the sensor to the bottom of the hole.'''
        return round(hole_depth - median_reading, self.round_to)

    def depth_imperial(self, median_reading, hole_depth):
        '''Calculate the rounded imperial depth of a liquid. hole_depth is the
        distance, in inches, from the sensor to the bottom of the hole.'''
        return round(hole_depth - (median_reading * 0.394), self.round_to)

    def distance_metric(self, median_reading):
        '''Calculate the rounded metric distance, in cm's, from the sensor
        to an object'''
        return round(median_reading, self.round_to)

    def distance_imperial(self, median_reading):
        '''Calculate the rounded imperial distance, in inches, from the sensor
        to an oject.'''
        return round(median_reading * 0.394, self.round_to)
