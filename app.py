import oscilloscope



Oscilloscope = oscilloscope.Oscilloscope
Oscilloscope.setupSound()

text = "Hello World"
Oscilloscope.createWav(text)
Oscilloscope.playSound('test.wav')
