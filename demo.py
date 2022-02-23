from xml.etree.ElementTree import TreeBuilder
import oscilloscope


Oscilloscope = oscilloscope.Oscilloscope()


#INA260 Current Sensor

i2c = board.I2C()

Oscilloscope.setupCurrentSensor(i2c,0x40)
Oscilloscope.measureCurrent()