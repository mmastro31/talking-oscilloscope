import oscilloscope
import time

scope = oscilloscope.Oscilloscope()
scope.setupSound()
lines = [
    'Welcome to the Talking Oscilloscope. You are in Basic mode. Click the Play button to continue or switch to Advanced mode.',  #1
    'You are in advanced mode.',  #3
    'Welcome to the Talking Oscilloscope. You are in Advanced mode. Click your desired measurement or switch to Basic mode.',    #2
    'This is the measurement menu. Click next until you reach the desired measurement function. When you select the correct measurement, press play.',
    'Please connect the positive probe to the terminal that is buzzing.',
    'PLease connect the negative probe to the terminal that is buzzing.',
    'When you are ready to measure, click Play',
    'Single Shot Voltage',
    'Single Shot Current',
    'Continuous Voltage',
    'Continuous Current',
    'Digital I O 1',
    'Digital I O 2'
]

for i in range(len(lines)):
    scope.createWav(lines[i], str(i+1))
    time.sleep(5)