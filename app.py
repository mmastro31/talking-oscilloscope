import oscilloscope


scope = oscilloscope.Oscilloscope()
scope.setupSound()

text = "Hello World"
scope.createWav(text)
scope.playSound('test.wav')
