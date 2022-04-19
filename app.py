import oscilloscope
from flask import Flask
import board
import smbus
from threading import Thread, Lock
import time


#app = Flask(__name__)

#Current Mode that is selected (Basic/Advanced)
global currentMode 
#Current measurementSetting
global currentMeasurementMode
currentMeasurementMode = None

def basicMode():
    global currentMeasurementMode
    if currentMeasurementMode == None:
        #First time running program
        print('Welcome to basic mode. Please select a measurement')
    else:
        print('Basic Mode selected.')


def advancedMode():
    print('advanced Mode selected')


#Monitors if Switch is moved every 1 second
def monitorSwitch(scope,i2cBus):
    global currentMode
    while True:
        l1.acquire()
        mode = scope.readButton(i2cBus, 'B', 3)
        if mode == 1 and currentMode == 0:
            currentMode = 1
            basicMode()
        elif mode == 0 and currentMode == 1:
            currentMode = 0
            advancedMode()
        l1.release()
        time.sleep(1)


def monitorButtons(scope,i2cBus):
    while True:
        l1.acquire()
        A,B = scope.readAllButtons(i2cBus)
        if A != 256:
            print('Button Pressed')
            print(A, B)
        elif B != 15:
            print('Button Pressed')
            print(A, B)
        l1.release()
        time.sleep(1)



def onStart(scope,i2c,spi,i2cBus):
    scope.setupSound()
    #scope.setupCurrentSensor(i2c)
    #scope.setupMotors()
    #scope.setupDisplay(spi)
    #scope.setupDigitalPins()
    scope.setupButtons(i2cBus)



if __name__ == "__main__":
    #Set up all sensors and buttons on Pi
    i2c = board.I2C()
    spi = board.SPI()
    i2cBus = smbus.SMBus(1)
    scope = oscilloscope.Oscilloscope()
    onStart(scope,i2c,spi,i2cBus)

    #Determine if Oscilloscope is in Basic or Advanced Mode based on switch placement
    currentMode = scope.readButton(i2cBus, 'B', 3)
    if currentMode:
        basicMode()  #Enter Basic Mode
    else:
        advancedMode() #Enter Advanced Mode

    #Starting Threads
    l1 = Lock()  #lock to control i2c bus
    t1 = Thread(target = monitorSwitch(scope,i2cBus))
    t1.daemon = True
    t1.start()
    t2 = Thread(target = monitorButtons(scope,i2cBus))
    t2.daemon = True
    t2.start()
    t1.join()
    t2.join()



    #app.run(host='0.0.0.0', port=80, debug=True, threaded=True)