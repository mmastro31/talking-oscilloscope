from xml.etree.ElementTree import TreeBuilder
import oscilloscope
import board
import smbus
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

def ToBePastedintoApp(Oscilloscope):
    #There is a Max of 14 spaces for characters across the x-axis for the display
    #  (w/ font-size at 32, but any lower and its too small to read) 
    #  21 spaces w/ 14 fontsize (not bad actually) 
    #  25 spaces w/ 12 fontsize
    #  10 fontsize too small

    #110 is the max for comfort in terms of the y-axis (14 fontsize)

    scope = Oscilloscope
    count_spaces = "1234567891123456789"
    welcome = "Welcome to the Talking"
    welcome2 = "Oscilloscope."
    welcome3 = "Oscilloscope."
    Basic_mode = "You are currently in" 
    Basic_mode2 = "Basic Mode."
    Advanced_mode = "You are currently in Advanced Mode."
    press_play = "Press Play to continue."
    mode_cycle = "___________"      #useless, will just be the mode depending on the button
    mode_selected = "_______ has been selected."
    mode_selection = "Press Play to select the mode or Next to cycle through the modes."
    prob = "The ____ port is now buzzing, please connect your prob to the port."
    measurement = "_______ Amps/Volts"  #depends on the measurement, this is kinda useless
    after_m = "Press Play to repeat the value, Next to read a new value, or Home to go back to the main menu."

    scope.displayText(count_spaces,True,0,0,14)
    scope.displayText(welcome,True,5,15,14)
    scope.displayText(welcome2,True,5,30,14)
    #scope.displayText(welcome3,True,10,60)

    scope.displayText(Basic_mode,True,5,100,14)
    scope.displayText(Basic_mode2,True,5,115,14)
    time.sleep(60)
    '''
    scope.displayText(Basic_mode,True,50,50)
    scope.displayText(press_play,True,100,100)
    time.sleep(10)
    scope.clearDisplay()
    scope.displayText(mode_cycle)
    time.sleep(5)
    scope.clearDisplay()
    scope.displayText(mode_selected)
    scope.displayText(mode_selection)
    scope.displayText(prob)
    scope.displayText(measurement)
    scope.displayText(after_m)
    '''
    

    return

def tftDisplayMenuSelection(Oscilloscope):
    print("The following display options are available:\n")
    print("   0 - CLEAR\n")
    print("   1 - IMAGE\n")
    print("   2 - TEXT\n")
    print("   3 - GRAPH [not yet ready]\n")
    print("   4 - OFF\n")
    print("   5 - ON [not necessary if already on]\n")  # Dont know if i need this given if it was turned off prior
    print("   6 - Test for app.py")
    print("   7 - EXIT")
    option = input("Please select one:")
    option.strip()

    if (option == "0"):
        print("================================\n")
        print("        CLEARING DISPLAY\n")
        print("================================\n")
        Oscilloscope.clearDisplay()
    elif (option == "1"):
        print("================================\n")
        print("        DISPLAYING IMAGE\n")
        print("================================\n")
        imageFile = input("Please type out the name of the image file:")
        value = Oscilloscope.displayImage(imageFile)
        if(value == 1):
            print("Please ensure the file name is valid.\n")
            tftDisplayMenuSelection(Oscilloscope)
        else:
            pass
    elif (option == "2"):
        print("================================\n")
        print("        DISPLAYING TEXT\n")
        print("================================\n")
        text = input("Please type out your text: ")
        Oscilloscope.displayText(text)
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
        Oscilloscope.displayOff()
    elif (option == "5"):
        print("================================\n")
        print("        TURING DISPLAY ON\n")
        print("================================\n")
        Oscilloscope.displayOn()
    elif (option == "6"):
        print("================================\n")
        print("            TEST APP.py\n")
        print("================================\n")
        ToBePastedintoApp(Oscilloscope)
    elif (option == "7"):
        print("================================\n")
        print("            EXITING\n")
        print("================================\n")
        return
    else:
        print("---ERROR: Not a valid option. Please select a number from the list---\n")
        tftDisplayMenuSelection(Oscilloscope)

def tftDisplayTest(Oscilloscope,spi):
    Oscilloscope.setupDisplay(spi)
    print("Setup Complete.\n")
    value = True
    while (value == True):
        tftDisplayMenuSelection(Oscilloscope)
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
    time.sleep(5)
    d = Oscilloscope.readButton(i2cBus, 'A', 0)
    print(d)
    b = Oscilloscope.readButton(i2cBus, 'A', 1)
    print(b)
    while True:
        a,c = Oscilloscope.readAllButtons(i2cBus)
        print(a,c)
        time.sleep(3)

def mainMenu(Oscilloscope,i2c,spi,i2cBus):
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
            buttonTest(Oscilloscope,i2cBus)
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
        mainMenu(Oscilloscope,i2c,spi,i2cBus)
    else:
        return

def main():
    Oscilloscope = oscilloscope.Oscilloscope()
    i2c = board.I2C()
    i2cBus = smbus.SMBus(1)
    spi = board.SPI()
    print("Running demo.py...\n")
    print("Welcome!\n")
    mainMenu(Oscilloscope,i2c,spi,i2cBus)



if __name__ == '__main__':
    main()
