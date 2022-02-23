
#Parts Setup


class Oscilloscope:

    def __init__(self):
        self.CurrentSensor = None



    #INA260 Current Sensor

    def setupCurrentSensor(self, bus, address=0x40):
        self.CurrentSensor = adafruit_ina260.INA260(bus)


    def measureCurrent(self):
        current = self.CurrentSensor.current
        return current 

    def measureVoltage(self):
        voltage = self.CurrentSensor.voltage
        return voltage

    def measurePower(self):
        power = self.CurrentSensor.power
        return power

    def changeCurrentSensorMode(self,num):
        pass
    
    def changeCurrentSensorAverage(self,count):
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
