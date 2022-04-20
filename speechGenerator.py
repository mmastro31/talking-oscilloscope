import oscilloscope
import time

scope = oscilloscope.Oscilloscope()
scope.setupSound()

voices = scope.engine.getProperty('voices')
for voice in voices:
   scope.engine.setProperty('voice', voice.id)
   scope.engine.say('The quick brown fox jumped over the lazy dog.')
scope.engine.runAndWait()

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

'''
for i in range(len(lines)):
    scope.createWav(lines[i], str(i+1))
    time.sleep(5)
'''