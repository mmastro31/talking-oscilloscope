import adafruit_ina260
import board
import busio
import time

class Oscilloscope:

    def __init__(self):
        self.CurrentSensor = None

    #INA260 Current Sensor

    count_dict = {0: adafruit_ina260.AveragingCount.COUNT_1,
                1: adafruit_ina260.AveragingCount.COUNT_4, 
                2: adafruit_ina260.AveragingCount.COUNT_16,
                3: adafruit_ina260.AveragingCount.COUNT_64,
                4: adafruit_ina260.AveragingCount.COUNT_128,
                5: adafruit_ina260.AveragingCount.COUNT_256,
                6: adafruit_ina260.AveragingCount.COUNT_512,
                7: adafruit_ina260.AveragingCount.COUNT_1024}
    conv_dict = {0: adafruit_ina260.ConversionTime.TIME_140_us,
            1: adafruit_ina260.ConversionTime.TIME_204_us,
            2: adafruit_ina260.ConversionTime.TIME_332_us,
            3: adafruit_ina260.ConversionTime.TIME_588_us,
            4: adafruit_ina260.ConversionTime.TIME_1_1_ms,
            5: adafruit_ina260.ConversionTime.TIME_2_116_ms,
            6: adafruit_ina260.ConversionTime.TIME_4_156_ms,
            7: adafruit_ina260.ConversionTime.TIME_8_244_ms,
        }

    def setupCurrentSensor(self, bus, address=0x40):
        self.CurrentSensor = adafruit_ina260.INA260(bus)
        self.CurrentSensor.reset_bit = 1
        self.CurrentSensor.mode = adafruit_ina260.Mode.CONTINUOUS
        self.CurrentSensor.averaging_count = adafruit_ina260.AveragingCount.COUNT_4
        self.CurrentSensor.voltage_conversion_time = adafruit_ina260.ConversionTime.TIME_588_us
        self.CurrentSensor.current_conversion_time = adafruit_ina260.ConversionTime.TIME_588_us


    def measureCurrent(self):
        #measure current with sensor
        current = self.CurrentSensor.current
        #print("Current: %.2f " %(current) + "mA")
        return current 

    def measureVoltage(self):
        #measure voltage with sensor
        voltage = self.CurrentSensor.voltage
        #print("Voltage: %.2f " %(voltage) + "V")
        return voltage

    def measurePower(self):
        #measure power with sensor
        power = self.CurrentSensor.power
        #print("Power: %.2f " %(power) + "mW")
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
    
    def currentSensorCount(self,num):
        #Dictionary is above.
        #0-7 correspond to count
        #invalid if other number
        if num < 0 or num > 7:
            print('invalid index. Please select 0-7')
        else:
            newCount = self.count_dict[num]
            self.CurrentSensor.averaging_count = newCount
        
    def currentSensorTiming(self,num):
        #Dictionary is above. (conv_dict)
        #0-7 corresponds to conversion time
        #invalid if other number
        if num < 0 or num > 7:
            print('invalid index number. Please select 0-7')
        else:
            newTime = self.conv_dict[num]
            self.CurrentSensor.voltage_conversion_time = newTime
            self.CurrentSensor.current_conversion_time = newTime

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
