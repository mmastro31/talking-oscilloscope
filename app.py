
import oscilloscope
from flask import Flask
import board
import smbus
from threading import Thread, Lock, Event
import time
import numpy as np
from scipy.io.wavfile import write

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
        homePressed = scope.readButton(i2cBus, 'B', 4)
        time.sleep(0.01)
        playPressed = scope.readButton(i2cBus, 'B', 1)
        time.sleep(0.01)
        nextPressed = scope.readButton(i2cBus, 'B', 2)
        time.sleep(0.01)
    return (homePressed, playPressed, nextPressed)

def state0(scope,measurementMode):
    scope.clearDisplay()
    scope.displayText("You are currently in",True,10,40,14)
    scope.displayText("Basic Mode",True,40,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    text = 'Basic Mode selected. Press play when ready.'
    print(text)
    scope.playSound(text)

def state1to6(scope,measurementMode):
    text = measurementMode.NAME + ' selected. Press next to select next measurement mode or press play'
    print(text)
    scope.playSound(text)
    scope.clearDisplay()
    scope.displayText(measurementMode.NAME,False,0,0,14) 
    scope.displayText(bd_menu,True,8,110,12)

def state7(scope,measurementMode):
    text = 'Welcome to ' + measurementMode.NAME
    print(text)
    scope.playSound(text)
    scope.clearDisplay()
    scope.displayText(measurementMode.NAME,False,0,0,14)
    scope.displayText("Selected",True,50,70,14)
    scope.displayText(bd_menu,True,8,110,12)
    text = 'The positive port is now buzzing. Please connect your probe to the port.'
    scope.playSound(text)
    print(text)
    scope.buzzMotor(measurementMode.MOTOR)
    scope.clearDisplay()
    scope.displayText("BUZZ!",True,60,40,14)
    scope.displayText("Connect + Port",True,25,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    text = 'Press play when you are done'
    scope.playSound(text)

def state8(scope,measurementMode):
    text = 'The negative port is now buzzing. Please connect your probe to the port.'
    print(text)
    scope.playSound(text)
    scope.buzzMotor(measurementMode.MOTOR)
    scope.clearDisplay()
    scope.displayText("BUZZ!",True,60,40,14)
    scope.displayText("Connect + Port",True,25,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    text = 'Press play when you are done'
    print(text)
    scope.playSound(text)

def state9(scope,measurementMode):
    text = 'You are now ready to begin measuring. Press play when you are ready.'
    print(text)
    scope.playSound(text)
    scope.clearDisplay()
    scope.displayText("READY!",False,0,0,16)

def state10(scope,measurementMode,value,measure_flag):
    scope.displayText(value,False,0,0,14)
    scope.displayText(bd_menu,True,8,110,12)
    if isinstance(value, int) or isinstance(value, float):
        scope.playSound(value)
    elif isinstance(value,np.array):
        scope.playWav('example.wav')
    time.sleep(1)
    #scope.playSound('/tmp/measurement.wav')
    text = 'Press Home to go home. Press Play to take another measurement. Press next to replay measurement'
    print(text)
    scope.playSound(text)

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

def writeWave(input_array):
    samplerate = 44100; fs = 100
    t = np.linspace(0., 1., samplerate)
    amplitude = np.iinfo(np.int16).max
    data = amplitude * input_array
    write("example.wav", samplerate, data.astype(np.int16))


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
    measure_flag = False

    currentState = 0
    while True:
        if currentState >= 1 and currentState <= 6:
            measurementMode = measurementModes[currentState - 1]
        
        if currentState < 10:
            measure_flag = False
            state = basicState[currentState]
            state[3](scope,measurementMode)
        else:
            state = basicState[currentState]
            state[3](scope,measurementMode,value,measure_flag)
 
        nextTask = basicButtons(scope,i2cBus)
        if nextTask[0] == 0:
            nextState = basicState[currentState][0]
        elif nextTask[1] == 0:
            nextState = basicState[currentState][1]
        elif nextTask[2] == 0:
            nextState = basicState[currentState][2]
        currentState = nextState

        if currentState == 10 and measure_flag == False:
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
            elif isinstance(value,np.array):
                writeWave(value)
            measure_flag = True



def advancedButtons(scope,i2cBus):
    singleVoltage = 1
    singleCurrent = 1
    continuousVoltage = 1
    continuousCurrent = 1
    digital1 = 1
    digital2 = 1
    while singleVoltage != 0 and singleCurrent != 0 and continuousVoltage != 0 and continuousCurrent != 0 and digital1 != 0 and digital2 != 0:
        singleVoltage = scope.readButton(i2cBus, 'A', 0)
        time.sleep(0.01)
        singleCurrent = scope.readButton(i2cBus, 'A', 1)
        time.sleep(0.01)
        continuousVoltage = scope.readButton(i2cBus, 'A', 2)
        time.sleep(0.01)
        continuousCurrent = scope.readButton(i2cBus, 'A', 3)
        time.sleep(0.01)
        digital1 = scope.readButton(i2cBus, 'A', 4)
        time.sleep(0.01)
        digital2 = scope.readButton(i2cBus, 'A', 5)
        time.sleep(0.01)

    if singleVoltage == 0:
        return SSV
    elif singleCurrent == 0:
        return SSC 
    elif continuousVoltage == 0:
        return CV
    elif continuousCurrent == 0:
        return CC
    elif digital1 == 0:
        return DIO1
    elif digital2 == 0:
        return DIO2
    

def advancedMode(scope,i2cBus):
    global currentMeasurementMode
    scope.clearDisplay()
    scope.displayText("You are currently in",True,10,40,14)     #displays basic mode
    scope.displayText("Advanced Mode",True,35,55,14)
    scope.displayText(bd_menu,True,8,110,12)
    text = 'Please select measurement mode.'
    print(text)
    scope.playSound(text)
    measurementMode = advancedButtons(scope,i2cBus)
    text = measurementMode.NAME + ' selected.'
    print(text)
    scope.playSound(text)




    


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
        value = np.array([])
        text = 'Press play when you are done measuring'
        scope.playSound(text)
        print(text)
        while playPressed != 0:
            playPressed = scope.readButton(i2cBus, 'B', 1)
            if measurementMode is CV:
                temp = scope.measureVoltage()
            elif measurementMode is CC:
                temp = scope.measureCurrent()
            value.append(temp)
            time.sleep(0.01)
        print('Continuous Measurement Taken')
        print(value)
        writeWave(value)

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