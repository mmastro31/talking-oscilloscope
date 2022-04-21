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
global bd_menu      #Button Display Menu - just to print the buttons at the bottom of the display like a mini menu
bd_menu = "Home       Play       Next"

e1 = Event()
e2 = Event()
l1 = Lock()  #lock to control i2c bus


class SSV:
    NAME = 'Single Shot Voltage'
    MOTOR = 1

class SSC:
    NAME = 'Single Shot Current'
    MOTOR = 1

class CV:
    NAME = 'Continuous Voltage'
    MOTOR = 1

class CC:
    NAME = 'Continuous Current'
    MOTOR = 1

class DIO1:
    NAME = 'Digital IO 1'
    MOTOR = 3

class DIO2:
    NAME = 'Digital IO 2'
    MOTOR = 4


measurementModes = [SSV, SSC, CV, CC, DIO1, DIO2]

def basicMode(scope,i2cBus):
    global buttonPressed
    global bd_menu

    scope.clearDisplay()
    scope.displayText("You are currently in",True,10,40,14)     #displays basic mode
    scope.displayText("Basic Mode",True,40,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    time.sleep(3)

    print('Basic Mode selected. Press play when ready.')
    playPressed = scope.readButton(i2cBus, 'B', 1)
    while playPressed != 0:
        playPressed = scope.readButton(i2cBus, 'B', 1)
    print('Play button pressed')
    playPressed = 1
    time.sleep(3)
    print('Single Shot Voltage selected. Press next to select next measurement mode or press play')
    measurementMode = measurementModes[0]
    scope.clearDisplay()
    scope.displayText(measurementMode.NAME,False,0,0,14)     #displays mm mode (mm = measruement)
    scope.displayText(bd_menu,True,8,110,12)
    time.sleep(3)
    i = 1
    while playPressed != 0:
        playPressed = scope.readButton(i2cBus, 'B', 1)
        nextPressed = scope.readButton(i2cBus, 'B', 2)
        if nextPressed == 0:
            measurementMode = measurementModes[i]
            print(measurementMode.NAME + ' selected. Press next to select next measurement mode or press play')
            scope.clearDisplay()
            scope.displayText(measurementMode.NAME,False,0,0,14)     #displays mm mode
            scope.displayText(bd_menu,True,8,110,12)
            time.sleep(2)
            i += 1
            nextPressed = 1
            if i == 6:
                i = 0
    
    print('Welcome to ' + measurementMode.NAME)
    scope.clearDisplay()
    scope.displayText(measurementMode.NAME,False,0,0,14)     #displays mm mode
    scope.displayText("Selected",True,50,70,14)
    scope.displayText(bd_menu,True,8,110,12)
    time.sleep(3)

    print('The positive port is now buzzing. Please connect your probe to the port.')
    scope.buzzMotor(measurementMode.MOTOR)
    print('Press play when you are done')
    scope.clearDisplay()
    scope.displayText("BUZZ!",True,60,40,14)     #displays instructions
    scope.displayText("Connect + Port",True,25,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    time.sleep(2)
    playPressed = 1
    while playPressed != 0:
        playPressed = scope.readButton(i2cBus, 'B', 1)
    
    print('The negative port is now buzzing. Please connect your probe to the port.')
    scope.buzzMotor(measurementMode.MOTOR)
    print('Press play when you are done')
    scope.clearDisplay()
    scope.displayText("BUZZ!",True,60,40,14)     #displays instructions
    scope.displayText("Connect + Port",True,25,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    time.sleep(2)
    playPressed = 1
    while playPressed != 0:
        playPressed = scope.readButton(i2cBus, 'B', 1)

    print('You are now ready to begin measuring. Press play when you are ready.')
    scope.clearDisplay()
    scope.displayText("READY!",False,0,0,16)     #displays "Ready!"
    #scope.displayText(bd_menu,True,8,110,12)
    time.sleep(2)
    playPressed = 1
    while playPressed != 0:
        playPressed = scope.readButton(i2cBus, 'B', 1)

    value = measuring(scope,measurementMode,i2cBus)
    print(value)
    
    scope.clearDisplay()
    if isinstance(value, int) or isinstance(value, float):
        if measurementMode.NAME == 'Single Shot Voltage' and value >= 0.01:
            value = str(value)
            value += " V"
        elif measurementMode.NAME == 'Single Shot Voltage' and value < 0.01:
            value = str(value)
            value += " mV"
        elif measurementMode.NAME == 'Single Shot Current' and value >= 0.01:
            value = str(value)
            value += " A"
        elif measurementMode.NAME == 'Single Shot Current' and value < 0.01:
            value = str(value)
            value += " mA"
        elif measurementMode.NAME == 'Digital IO 1' or measurementMode.NAME == 'Digital IO 2':
            value = str(value)    
        scope.displayText(value,False,0,0,14)     #displays values for either Single Shot or DigitalIO
        scope.displayText(bd_menu,True,8,110,12)
    else:
        for i in value:
            answer = str(i)
            scope.displayText(answer,False,0,0,14)     #displays values for Continous
            scope.displayText(bd_menu,True,8,110,12)    #Needs fixing
    time.sleep(3)




def advancedMode(scope,i2cBus):
    global currentMeasurementMode
    if currentMeasurementMode == None:
        #First Time running program
        print('Welcome to Advanced Mode. Please select a measurement')
        e1.set()
    else:
        print('Advanced Mode selected')
        e1.set()


def measuring(scope, measurementMode, i2cBus):
    value = 0
    time.sleep(1)
    if measurementMode is SSV or measurementMode is SSC:
        if measurementMode is SSV:
            value = scope.measureVoltage()
            print('measuring SSV')
        elif measurementMode is SSC:
            value = scope.measureCurrent()
            print('measuring SSC')
    elif measurementMode is CV or measurementMode is CC:
        playPressed = 1
        value = []
        while playPressed != 0:
            playPressed = scope.readButton(i2cBus, 'B', 1)
            if measurementMode is CV:
                temp = scope.measureVoltage()
            elif measurementMode is CC:
                temp = scope.measureCurrent()
            value.append(temp)    
        print('Continuous Measurement Taken')
        print(value)
    elif measurementMode is DIO1 or measurementMode is DIO2:
        value = scope.readDigitalPin()
        print('measuring DIO')

    return value



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
        time.sleep(0.5)


def monitorHome(scope,i2cBus):
    global currentMode
    while True:
        l1.acquire()
        home = scope.readButton(i2cBus, 'B', 0)
        if home == 0:
            print('Going Home')
            if currentMode == 1:
                basicMode(scope,i2cBus)
            elif currentMode == 0:
                advancedMode(scope,i2cBus)
            home = 1
        l1.release()
        time.sleep(1)



def onStart(scope,i2c,spi,i2cBus):
    scope.setupSound()
    scope.setupCurrentSensor(i2c)
    scope.setupMotors()
    scope.setupDigitalPins()
    scope.setupButtons(i2cBus)
    scope.setupDisplay(spi)

    scope.displayText("Welcome to the",True,25,30,14)
    scope.displayText("Talking Oscilloscope",True,8,45,14)
    scope.displayText("Booting...",True,50,90,14)
    time.sleep(5)



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
    t2 = Thread(target = monitorHome, args=(scope,i2cBus))
    t2.daemon = True
    t2.start()
    t1.join()
    t2.join()



    #app.run(host='0.0.0.0', port=80, debug=True, threaded=True)