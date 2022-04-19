import oscilloscope
from flask import Flask
import board
import smbus
from threading import Thread, Lock
import time


#app = Flask(__name__)

global currentMode


def basicMode():
    print('basic Mode selected')

def advancedMode():
    print('advanced Mode selected')


#Monitors if Switch is moved every 1 second
def monitorSwitch(scope,i2cBus):
    while True:
        l1.acquire()
        mode = scope.readButton(i2cBus, 'B', 3)
        if mode == 1 and currentMode == 0:
            basicMode()
        elif mode == 0 and currentMode == 1:
            advancedMode()
        l1.release()
        time.sleep(1)



def onStart(scope,i2c,spi,i2cBus):
    scope.setupSound()
    scope.setupCurrentSensor(i2c)
    scope.setupMotors()
    scope.setupDisplay(spi)
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
        basicMode()  #Enter Basic Mode
    else:
        advancedMode() #Enter Advanced Mode

    #Starting Threads
    l1 = Lock()  #lock to control i2c bus
    t1 = Thread(target = monitorSwitch)
    t1.daemon = True
    t1.start()
    t1.join()


    #app.run(host='0.0.0.0', port=80, debug=True, threaded=True)