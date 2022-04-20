import oscilloscope
from flask import Flask
import board
import smbus
from threading import Thread, Lock, Event
import time


#app = Flask(__name__)


#Current Mode that is selected (Basic/Advanced)
global currentMode 
#Current measurementSetting
global currentMeasurementMode
currentMeasurementMode = None
global buttonPressed
buttonPressed = None

e1 = Event()
e2 = Event()
l1 = Lock()  #lock to control i2c bus

buttonDict = {
    62: 'Single Shot Voltage',
    61: 'Single Shot Current',
    59: 'Continuous Voltage',
    55: 'Continuous Current',
    47: 'Digital IO 1',
    31: 'Digital IO 2',
    3: 'Home',
    5: 'Play',
    6: 'Next'
}

measurementModes = ['Single Shot Voltage', 'Single Shot Current', 'Continuous Voltage', 'Continuous Current', 'Digital IO 1', 'Digital IO 2']

def basicMode(scope,i2cBus):
    global buttonPressed
    print('Basic Mode selected. Press play when ready.')
    playPressed = scope.readButton(i2cBus, 'B', 1)
    while playPressed != 0:
        playPressed = scope.readButton(i2cBus, 'B', 1)
    print('Play button pressed')
    playPressed = 1
    print('Single Shot Voltage. Press next to select next measurement mode or press play')
    measurementMode = measurementModes[0]
    while playPressed != 0:
        playPressed = scope.readButton(i2cBus, 'B', 1)
        nextPressed = scope.readButton(i2cBus, 'B', 2)
        i = 1
        if nextPressed == 0:
            measurementMode = measurementModes[i]
            print(measurementMode + '. Press next to select next measurement mode or press play')
            i += 1
            nextPressed = 1
    
    print('Welcome to ' + measurementMode)
    



    


def advancedMode(scope,i2cBus):
    global currentMeasurementMode
    if currentMeasurementMode == None:
        #First Time running program
        print('Welcome to Advanced Mode. Please select a measurement')
        e1.set()
    else:
        print('Advanced Mode selected')
        e1.set()



#Monitors if Switch is moved every 1 second
def monitorSwitch(scope,i2cBus):
    global currentMode
    while True:
        l1.acquire()
        mode = scope.readButton(i2cBus, 'B', 3)
        if mode == 1 and currentMode == 0:
            currentMode = 1
            basicMode(scope,i2cBus)
        elif mode == 0 and currentMode == 1:
            currentMode = 0
            advancedMode(scope,i2cBus)
        l1.release()
        time.sleep(1)


def monitorButtons(scope,i2cBus):
    global buttonPressed
    while e1.isSet():
        l1.acquire()
        A,B = scope.readAllButtons(i2cBus)
        print(A, B)
        try:
            buttonPressed = buttonDict[A]
            e1.clear()
        except:
            pass

        try:
            buttonPressed = buttonDict[B]
            e1.clear()
        except:
            pass
        l1.release()
        time.sleep(1)



def onStart(scope,i2c,spi,i2cBus):
    scope.setupSound()
    #scope.setupCurrentSensor(i2c)
    scope.setupMotors()
    #scope.setupDisplay(spi)
    scope.setupDigitalPins()
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
        basicMode(scope,i2cBus)  #Enter Basic Mode
    else:
        advancedMode(scope,i2cBus) #Enter Advanced Mode

    #Starting Threads
    t1 = Thread(target = monitorSwitch, args=(scope,i2cBus))
    t1.daemon = True
    t1.start()
    t2 = Thread(target = monitorButtons, args=(scope,i2cBus))
    t2.daemon = True
    t2.start()
    t1.join()
    t2.join()



    #app.run(host='0.0.0.0', port=80, debug=True, threaded=True)