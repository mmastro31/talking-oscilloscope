from xml.etree.ElementTree import TreeBuilder
import oscilloscope

#INA260 Current Sensor
def currentSensorTest():
    Oscilloscope.setupCurrentSensor(i2c,0x40)
    print('Setup Complete. Continuously measuring current, voltage and power.')
    
    #measure current, voltage and power for 30 seconds
    i = 0 
    while (i<30):
        current = Oscilloscope.measureCurrent()
        voltage = Oscilloscope.measureVoltage()
        power = Oscilloscope.measurePower()
        print("Current: %.2f Voltage: %.2f Power: %.2f" %(current, voltage, power))
        time.sleep(1)
        i+=1

    #Put Oscilloscope into shutdown mode
    Oscilloscope.changeCurrentSensorMode(2)
    print('Oscilloscope shutdown.')



def main():
    Oscilloscope = oscilloscope.Oscilloscope()
    i2c = board.I2C()
    #current sensor test
    currentSensorTest()
    


if __name__ == '__main__':
    main()
