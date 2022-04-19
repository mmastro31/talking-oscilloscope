import oscilloscope
from flask import Flask
import board
import smbus


#app = Flask(__name__)



def onStart(scope,i2c,spi,i2cBus):
    scope.setupSound()
    scope.setupCurrentSensor(i2c)
    scope.setupMotors()
    scope.setupDisplay(spi)
    scope.setupDigitalPins()
    scope.setupButtons(i2cBus)


def menu(scope,i2c,spi,i2cBus):
    mode = scope.readButton(i2cBus,'B',3)
    if mode == 1:
        #Basic Mode
        scope.playSound('1.wav')
    elif mode == 0:
        #Advanced Mode
        scope.playSound('2.wav')




if __name__ == "__main__":
    i2c = board.I2C()
    spi = board.SPI()
    i2cBus = smbus.SMBus(1)
    scope = oscilloscope.Oscilloscope()
    onStart(scope,i2c,spi,i2cBus)

    menu(scope,i2c,spi,i2cBus)



    #app.run(host='0.0.0.0', port=80, debug=True, threaded=True)