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
    FILE = '1.wav'
    MOTOR = 1
    GO_NEXT = '9.wav'
    WELCOME = '22.wav'

class SSC:
    NAME = 'Single Shot Current'
    FILE = '2.wav'
    MOTOR = 1
    GO_NEXT = '17.wav'
    WELCOME = '23.wav'

class CV:
    NAME = 'Continuous Voltage'
    FILE = '3.wav'
    MOTOR = 1
    GO_NEXT = '18.wav'
    WELCOME = '24.wav'

class CC:
    NAME = 'Continuous Current'
    FILE = '4.wav'
    MOTOR = 1
    GO_NEXT = '19.wav'
    WELCOME = '25.wav'

class DIO1:
    NAME = 'Digital IO 1'
    FILE = '5.wav'
    MOTOR = 3
    GO_NEXT = '20.wav'
    WELCOME = '26.wav'

class DIO2:
    NAME = 'Digital IO 2'
    FILE = '6.wav'
    MOTOR = 4
    GO_NEXT = '21.wav'
    WELCOME = '27.wav'

measurementModes = [SSV, SSC, CV, CC, DIO1, DIO2]

def basicButtons(scope,i2cBus):
    homePressed = 1
    playPressed = 1
    nextPressed = 1
    while playPressed != 0 and homePressed != 0 and nextPressed != 0:
        homePressed = scope.readButton(i2cBus, 'B', 0)
        playPressed = scope.readButton(i2cBus, 'B', 1)
        nextPressed = scope.readButton(i2cBus, 'B', 2)
    return (homePressed, playPressed, nextPressed)

def state0(scope,measurementMode):
    scope.clearDisplay()
    scope.displayText("You are currently in",True,10,40,14)
    scope.displayText("Basic Mode",True,40,55,14)
    scope.displayText(bd_menu,True,8,110,12),print('Basic Mode selected. Press play when ready.')
    scope.playSound('7.wav')

def state1to6(scope,measurementMode):
    print(measurementMode.NAME + ' selected. Press next to select next measurement mode or press play')
    scope.playSound(measurementMode.GO_NEXT)
    scope.clearDisplay()
    scope.displayText(measurementMode.NAME,False,0,0,14) 
    scope.displayText(bd_menu,True,8,110,12)

def state7(scope,measurementMode):
    scope.playSound(measurementMode.WELCOME)
    print('Welcome to ' + measurementMode.NAME)
    scope.clearDisplay()
    scope.displayText(measurementMode.NAME,False,0,0,14)
    scope.displayText("Selected",True,50,70,14)
    scope.displayText(bd_menu,True,8,110,12)
    scope.playSound('12.wav')
    print('The positive port is now buzzing. Please connect your probe to the port.')
    scope.buzzMotor(measurementMode.MOTOR)
    scope.clearDisplay()
    scope.displayText("BUZZ!",True,60,40,14)
    scope.displayText("Connect + Port",True,25,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    print('Press play when you are done')
    scope.playSound('13.wav')

def state8(scope,measurementMode):
    print('The negative port is now buzzing. Please connect your probe to the port.')
    scope.playSound('14.wav')
    scope.buzzMotor(measurementMode.MOTOR)
    scope.clearDisplay()
    scope.displayText("BUZZ!",True,60,40,14)
    scope.displayText("Connect + Port",True,25,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    print('Press play when you are done')
    scope.playSound('13.wav')

def state9(scope,measurementMode):
    print('You are now ready to begin measuring. Press play when you are ready.')
    scope.playSound('15.wav')
    scope.clearDisplay()
    scope.displayText("READY!",False,0,0,16)

def state10(scope,measuremntMode,value):
    scope.displayText(value,False,0,0,14)
    scope.displayText(bd_menu,True,8,110,12)
    scope.createWav(value, 'measurement')
    time.sleep(4)
    scope.playSound('measurement.wav')

          #home, play, next,  function call
basicState = { 0: [0,1,0,state0], #0 - press play when ready
               1: [0,7,2,state1to6], #1 - SSV
               2: [0,7,3,state1to6], #2 - SS
               3: [0,7,4,state1to6], #3 - CV
              4: [0,7,5,state1to6], #4 - CC
              5: [0,7,6,state1to6], #5 - DIO1
              6: [0,7,1,state1to6], #6 - DIO2
              7: [0,8,7,state7], #7 - connect probe 1
              8: [0,9,8,state8], #8 - connect probe 2
              9: [0,10,9,state9], #9 - wait to measure
              10: [0,9,10,state10]} #10 - done measuring

def basicMode(scope,i2cBus):

    '''
    1. enter basic state
    2. do tasks related to state
    3. wait for button response
    4. go to next state based on input
    5. return to 1.
    '''

    measurementMode = measurementModes[0]
    value = None

    currentState = 0
    while True:
        if currentState >= 1 and currentState <= 6:
            measurementMode = measurementModes[currentState - 1]
        
        if currentState < 10:
            state = basicState[currentState]
            state[3](scope,measurementMode)
        else:
            state = basicState[currentState]
            state[3](scope,measurementMode,value)

        if currentState == 9:
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
        nextTask = basicButtons(scope,i2cBus)
        if nextTask[0] == 0:
            nextState = basicState[currentState][0]
        elif nextTask[1] == 0:
            nextState = basicState[currentState][1]
        elif nextTask[2] == 0:
            nextState = basicState[currentState][2]
        currentState = nextState

    '''
    global buttonPressed
    global bd_menu

    scope.clearDisplay()
    scope.displayText("You are currently in",True,10,40,14)     #displays basic mode
    scope.displayText("Basic Mode",True,40,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    time.sleep(2)
    print('Basic Mode selected. Press play when ready.')
    scope.playSound('7.wav')
    playPressed = scope.readButton(i2cBus, 'B', 1)
    while playPressed != 0:
        playPressed = scope.readButton(i2cBus, 'B', 1)
    print('Play button pressed')
    playPressed = 1
    time.sleep(3)
    print('Single Shot Voltage selected. Press next to select next measurement mode or press play')
    scope.playSound('9.wav')
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
            scope.playSound(measurementMode.GO_NEXT)
            scope.clearDisplay()
            scope.displayText(measurementMode.NAME,False,0,0,14)     #displays mm mode
            scope.displayText(bd_menu,True,8,110,12)
            time.sleep(1)
            i += 1
            nextPressed = 1
            if i == 6:
                i = 0

    scope.playSound(measurementMode.WELCOME)
    print('Welcome to ' + measurementMode.NAME)
    scope.clearDisplay()
    scope.displayText(measurementMode.NAME,False,0,0,14)     #displays mm mode
    scope.displayText("Selected",True,50,70,14)
    scope.displayText(bd_menu,True,8,110,12)
    time.sleep(2)

    scope.playSound('12.wav')
    print('The positive port is now buzzing. Please connect your probe to the port.')
    scope.buzzMotor(measurementMode.MOTOR)
    print('Press play when you are done')
    scope.playSound('13.wav')
    scope.clearDisplay()
    scope.displayText("BUZZ!",True,60,40,14)     #displays instructions
    scope.displayText("Connect + Port",True,25,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    time.sleep(2)
    playPressed = 1
    while playPressed != 0:
        playPressed = scope.readButton(i2cBus, 'B', 1)
    
    print('The negative port is now buzzing. Please connect your probe to the port.')
    scope.playSound('14.wav')
    scope.buzzMotor(measurementMode.MOTOR)
    print('Press play when you are done')
    scope.playSound('13.wav')
    scope.clearDisplay()
    scope.displayText("BUZZ!",True,60,40,14)     #displays instructions
    scope.displayText("Connect + Port",True,25,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    time.sleep(2)
    playPressed = 1
    while playPressed != 0:
        playPressed = scope.readButton(i2cBus, 'B', 1)

    print('You are now ready to begin measuring. Press play when you are ready.')
    scope.playSound('15.wav')
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
        scope.createWav(value, 'measurement')
        time.sleep(4)
        scope.playSound('measurement.wav')
    else:
        for i in value:
            answer = str(i)
            scope.displayText(answer,False,0,0,14)     #displays values for Continous
            scope.displayText(bd_menu,True,8,110,12)    #Needs fixing
    time.sleep(3)
    '''



def advancedMode(scope,i2cBus):
    global currentMeasurementMode
    scope.clearDisplay()
    scope.displayText("You are currently in",True,10,40,14)     #displays basic mode
    scope.displayText("Advanced Mode",True,35,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    time.sleep(3)
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
        mode = scope.readButton(i2cBus, 'B', 3)
        if mode == 1 and currentMode == 0:
            currentMode = 1
            basicMode(scope,i2cBus)
        elif mode == 0 and currentMode == 1:
            currentMode = 0
            advancedMode(scope,i2cBus)
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

    currentMode = True  #scope.readButton(i2cBus, 'B', 3)
    #Starting Threads
    '''
    t1 = Thread(target = monitorSwitch, args=(scope,i2cBus))
    t1.daemon = True
    t1.start()
    t1.join()
    '''

    #Determine if Oscilloscope is in Basic or Advanced Mode based on switch placement
    if currentMode:
        basicMode(scope,i2cBus)  #Enter Basic Mode
    else:
        advancedMode(scope,i2cBus) #Enter Advanced Mode


    #app.run(host='0.0.0.0', port=80, debug=True, threaded=True)