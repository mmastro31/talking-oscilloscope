import oscilloscope
from flask import Flask


app = Flask(__name__)



def onStart(scope,i2c,spi,i2cBus):
    scope.setupSound()
    scope.setupCurrentSensor(i2c)
    scope.setupMotors()
    scope.setupDisplay(spi)
    scope.setupDigitalPins()
    scope.setupButtons(i2cBus)




if __name__ == "__main__":
    i2c = board.I2C()
    spi = board.SPI()
    i2cBus = smbus.SMBus(1)
    scope = oscilloscope.Oscilloscope()
    onStart(scope,i2c,spi,i2cBus)

    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)