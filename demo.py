from xml.etree.ElementTree import TreeBuilder
import oscilloscope
import board
import time
#Not sure if these below are required bc of the way i coded everything
import digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7735

#INA260 Current Sensor
def currentSensorTest(Oscilloscope,i2c):
    Oscilloscope.setupCurrentSensor(i2c,0x40)
    print('Setup Complete. Continuously measuring current, voltage and power.')

    #measure current, voltage and power for 30 seconds
    i = 0
    while (i<30):
        current = Oscilloscope.measureCurrent()
        voltage = Oscilloscope.measureVoltage()
        power = Oscilloscope.measurePower()
        print("Current: %.2f Voltage: %.2f Power: %.2f" %(current, voltage, power))
        time.sleep(1)
        i+=1

    #Put Oscilloscope into shutdown mode
    Oscilloscope.CurrentSensor.mode = oscilloscope.CurrentSensorMode.SHUTDOWN
    print('Oscilloscope shutdown.')

def tftDisplayMenuSelection(Oscilloscope,spi,image,draw,disp,backlight,width,height):
    print("The following display options are available:\n")
    print("   0 - CLEAR\n")
    print("   1 - IMAGE\n")
    print("   2 - TEXT\n")
    print("   3 - GRAPH [not yet ready]\n")
    print("   4 - OFF\n")
    print("   5 - ON [not necessary if already on]\n")  # Dont know if i need this given if it was turned off prior
    print("   6 - EXIT\n")
    option = input("Please select one:")
    option.strip()

    if (option == "0"):
        print("================================\n")
        print("        CLEARING DISPLAY\n")
        print("================================\n")
        Oscilloscope.clearDisplay(image,draw,disp,width,height)
    elif (option == "1"):
        print("================================\n")
        print("        DISPLAYING IMAGE\n")
        print("================================\n")
        imageFile = input("Please type out the name of the image file:")
        value = Oscilloscope.displayImage(imageFile,image,draw,disp,width,height)
        if(value == 1):
            print("Please ensure the file name is valid.\n")
            tftDisplayMenuSelection(Oscilloscope,spi,image,draw,disp,backlight,width,height)
        else:
            pass
    elif (option == "2"):
        print("================================\n")
        print("        DISPLAYING TEXT\n")
        print("================================\n")
        text = input("Please type out your text: ")
        Oscilloscope.displayText(text,image,draw,disp,width,height)
    elif (option == "3"):
        print("================================\n")
        print("        DISPLAYING GRAPH\n")
        print("================================\n")
        print("  [CURRENTLY NOT IMPLEMENTED]\n")
        pass
    elif (option == "4"):
        print("================================\n")
        print("       TURING DISPLAY OFF\n")
        print("================================\n")
        Oscilloscope.displayOff(backlight)
    elif (option == "5"):
        print("================================\n")
        print("        TURING DISPLAY ON\n")
        print("================================\n")
        Oscilloscope.displayOn(backlight)
    elif (option == "6"):
        print("================================\n")
        print("            EXITING\n")
        print("================================\n")
        return
    else:
        print("---ERROR: Not a valid option. Please select a number from the list---\n")
        tftDisplayMenuSelection(Oscilloscope,spi,image,draw,disp,backlight,width,height)

def tftDisplayTest(Oscilloscope, spi):
    image, draw, disp, backlight, width, height = Oscilloscope.setupDisplay(spi)
    print("Setup Complete.\n")
    value = True
    while (value == True):
        tftDisplayMenuSelection(Oscilloscope,spi,image,draw,disp,backlight,width,height)
        repeat = input("Would you like quit TFT Display(y/n)?")
        repeat.strip()
        repeat.lower()
        if (repeat == "y"):
            value = False
    pass


def audioTest(Oscilloscope):
    Oscilloscope.setupSound()

    text = "Hello World"
    Oscilloscope.createWav(text)
    time.sleep(5)
    Oscilloscope.playSound('test.wav')



def motorTest(Oscilloscope):
    Oscilloscope.setupMotors()
    Oscilloscope.buzzMotor(1)
    Oscilloscope.buzzMotor(2)
    Oscilloscope.buzzMotor(3)
    Oscilloscope.motorOn(2)
    Oscilloscope.motorOn(1)
    Oscilloscope.buzzMotor(4)
    Oscilloscope.stopMotors()

def digitalInputTest(Oscilloscope):
    pass

def buttonTest(Oscilloscope,i2cBus):
    Oscilloscope.setupButtons(i2cBus)
    print('Buttons Set Up')
    d = Oscilloscope.readButton(i2cBus, 'A', 0)
    print(d)
    b = Oscilloscope.readButton(i2cBus, 'A', 1)
    print(b)
    while True:
        a,c = Oscilloscope.readAllButtons(i2cBus)
        print(a,c)
        time.sleep(3)

def mainMenu(Oscilloscope,i2c,spi):
    print("The following options are available:\n")
    print("   0 - Current Sensor\n")
    print("   1 - TFT Display\n")
    print("   2 - Stereo Decoder\n")
    print("   3 - Motors\n")
    print("   4 - Digital Inputs\n")
    print("   5 - Buttons / Physical UI\n")

    option = input("Please select one:")
    option.strip()
    if (option == "0"):  # current sensor test
        try:
            currentSensorTest(Oscilloscope, i2c)
        except:
            print("---ERROR: No current sensor detected---\n")
    elif (option == "1"):  # tft display test
        try:
            tftDisplayTest(Oscilloscope, spi)
        except:
            print("---ERROR: No tft display detected---\n")
    elif (option == "2"):  # Stereo Decoder
        try:
            audioTest(Oscilloscope)
        except:
            print("---ERROR: No Stereo Decoder detected ---\n")
    elif (option == "3"):  # Motors 
        try:
            motorTest(Oscilloscope)
        except:
            print("---ERROR: No Motor detected---\n")
    elif (option == "4"):  # Digital Inputs
        try:
            digitalInputTest(Oscilloscope)
        except:
            print("---ERROR: No Digital Inputs Detected---\n")
    elif (option == "5"):  # Buttons / Physical UI
        try:
            buttonTest(Oscilloscope)
        except:
            print("---ERROR: No Buttons detected---\n")
    else:
        print("---ERROR: Not a valid option. Please select a number from the list---\n")
        mainMenu(Oscilloscope,i2c,spi)

    print("------\n")
    print("Welcome back to the Main Menu.\n")
    stayORleave = input("Would you like to quit demo.py(y/n)?\n")
    stayORleave.strip()
    stayORleave.lower()
    if (stayORleave == "n"):
        mainMenu(Oscilloscope,i2c,spi)
    else:
        return

def main():
    Oscilloscope = oscilloscope.Oscilloscope()
    i2c = board.I2C()
    i2cBus = smbus.SMBus(1)
    spi = board.SPI()
    print("Running demo.py...\n")
    print("Welcome!\n")
    mainMenu(Oscilloscope,i2c,spi)



if __name__ == '__main__':
    main()
