import oscilloscope
import time
import pyttsx3



lines = [
    'Single Shot Voltage',
    'Single Shot Current',
    'Continuous Voltage',
    'Continuous Current',
    'Digital IO 1',
    'Digital IO 2',
    'Basic Mode selected. Press play when ready.',
    'Play button pressed',
    'Single Shot Voltage selected. Press next to select next measurement mode or press play',
    ' selected. Press next to select next measurement mode or press play',
    'Welcome to ',
    'The positive port is now buzzing. Please connect your probe to the port.',
    'Press play when you are done',
    'The negative port is now buzzing. Please connect your probe to the port.',
    'You are now ready to begin measuring. Press play when you are ready.',
    'Welcome to Advanced Mode. Please select a measurement',
]

scope = oscilloscope.Oscilloscope()
scope.setupSound()

scope.engine.setProperty('rate', 175)
scope.engine.setProperty('voice', 'english+f1')
scope.engine.say('Hello World')
scope.engine.runAndWait()
scope.engine.setProperty('voice', 'english+f2')
scope.engine.say('Hello World')
scope.engine.runAndWait()
scope.engine.setProperty('voice', 'english+f3')
scope.engine.say('Hello World')
scope.engine.runAndWait()
scope.engine.setProperty('voice', 'english+f4')
scope.engine.say('Hello World')
scope.engine.runAndWait()
scope.engine.setProperty('voice', 'english_rp+f3') #my preference
scope.engine.say('Hello World')
scope.engine.runAndWait()
scope.engine.setProperty('voice', 'english_rp+f4')
scope.engine.say('Hello World')
scope.engine.runAndWait()

'''
scope.createWav(lines[0], '1')
scope.engine.runAndWait()

time.sleep(10)

'''