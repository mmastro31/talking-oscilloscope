
import matplotlib.pyplot as plt
import random



lines = [
    'Single Shot Voltage', #1
    'Single Shot Current', #2
    'Continuous Voltage', #3
    'Continuous Current', #4
    'Digital IO 1', #5
    'Digital IO 2', #6
    'Basic Mode selected. Press play when ready.', #7
    'Play button pressed', #8
    'Single Shot Voltage selected. Press next to select next measurement mode or press play', #9
    ' selected. Press next to select next measurement mode or press play', #10
    'Welcome to ', #11
    'The positive port is now buzzing. Please connect your probe to the port.', #12
    'Press play when you are done', #13
    'The negative port is now buzzing. Please connect your probe to the port.', #14
    'You are now ready to begin measuring. Press play when you are ready.', #15
    'Welcome to Advanced Mode. Please select a measurement', #16
    'Single Shot Current selected. Press next to select next measurement mode or press play', #17
    'Continuous Voltage selected. Press next to select next measurement mode or press play', #18
    'Continuous Current selected. Press next to select next measurement mode or press play', #19
    'Digital IO 1 selected. Press next to select next measurement mode or press play', #20
    'Digital IO 2 selected. Press next to select next measurement mode or press play', #21
    'Welcome to Single Shot Voltage', #22
    'Welcome to Single Shot Current', #23
    'Welcome to Continuous Voltage', #24
    'Welcome to Continuous Current', #25
    'Welcome to Digital IO 1', #26
    'Welcome to Digital IO 2', #27
]


#################### generate default graph ###########################


   
x = []
y = []
for i in range(150):
    time = 0.1 + (i * 0.1)
    x.append(time)
    y.append(0)

  
plt.plot(x, y, color='red', marker='o')
plt.title('Oscilloscope', fontsize=14)
plt.xlabel('time', fontsize=14)
plt.ylabel('Volts', fontsize=14)
plt.grid(True)
plt.savefig('defaultGraph.png')