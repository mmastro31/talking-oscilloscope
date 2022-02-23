#Parts Setup
import adafruit_ina260
import board

class Oscilloscope:

    def __init__(self):
        self.CurrentSensor = None

    #INA260 Current Sensor

    def setupCurrentSensor(self, bus, address=0x40):
        self.CurrentSensor = adafruit_ina260.INA260(bus)
        self.CurentSensor.reset_bit = 1
        self.CurrentSensor.mode = adafruit_ina260.Mode.CONTINUOUS


    def measureCurrent(self):
        current = self.CurrentSensor.current
        print(current)
        return current 

    def measureVoltage(self):
        voltage = self.CurrentSensor.voltage
        print(voltage)
        return voltage

    def measurePower(self):
        power = self.CurrentSensor.power
        print(power)
        return power


    def changeCurrentSensorMode(self,num):
        #Change Mode Current Sensor is operating in
        #0 = CONTINUOUS
        #1 = TRIGGERED
        #2 = SHUTDOWN
        if num == 0:
            self.CurrentSensor.mode = adafruit_ina260.Mode.CONTINUOUS
        elif num == 1:
            self.CurrentSensor.mode = adafruit_ina260.Mode.TRIGGERED
        elif num ==2:
            self.CurrentSensor.mode = adafruit_ina260.Mode.SHUTDOWN
        else:
            print("Incorrect input. Please select 0, 1, or 2")
    
    def changeCurrentSensorAverage(self,count):
        #Possible average counts: 1,4,16,64,128,256,512,1024
        pass

    #I2S Stereo Decoder

    def soundOut():
        pass

    def setupSound():
        pass

    #Motors / H-Bridge

    def buzzMotor():
        pass

    def setupMotor():
        pass

    def getMotorState():
        pass

    def stopMotor():
        pass

    #TFT LCD Display

    def setupDisplay():
        pass

    def displayOff():
        pass

    def printDisplay():
        pass


    #Buttons

    def getButtonState():
        pass

    def setupButton():
        pass
