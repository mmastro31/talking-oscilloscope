from tkinter import NONE
import adafruit_ina260
import board
import busio
import digitalio
import os
import time
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735
import pygame as pg
import RPi.GPIO as GPIO
import smbus
import pyttsx3
import uuid



# Current Sensor Helper Classes

#Different Current Sensor Modes
class CurrentSensorMode:

    CONTINUOUS = adafruit_ina260.Mode.CONTINUOUS
    TRIGGERED = adafruit_ina260.Mode.TRIGGERED
    SHUTDOWN = adafruit_ina260.Mode.SHUTDOWN

#Current Sensor Number of Measurements
class AveragingCount:

    COUNT_1 =  adafruit_ina260.AveragingCount.COUNT_1
    COUNT_4 =  adafruit_ina260.AveragingCount.COUNT_4
    COUNT_16 = adafruit_ina260.AveragingCount.COUNT_16
    COUNT_64 =  adafruit_ina260.AveragingCount.COUNT_64
    COUNT_128 =  adafruit_ina260.AveragingCount.COUNT_128
    COUNT_256 =  adafruit_ina260.AveragingCount.COUNT_256
    COUNT_512 =  adafruit_ina260.AveragingCount.COUNT_512
    COUNT_1024 =  adafruit_ina260.AveragingCount.COUNT_1024

#Current Sensor Time for Conversion
class ConversionTime:

    TIME_140_us =  adafruit_ina260.ConversionTime.TIME_140_us
    TIME_204_us =  adafruit_ina260.ConversionTime.TIME_204_us
    TIME_332_us =  adafruit_ina260.ConversionTime.TIME_332_us
    TIME_588_us = adafruit_ina260.ConversionTime.TIME_588_us
    TIME_1_1_ms =  adafruit_ina260.ConversionTime.TIME_1_1_ms
    TIME_2_116_ms =  adafruit_ina260.ConversionTime.TIME_2_116_ms
    TIME_4_156_ms =  adafruit_ina260.ConversionTime.TIME_4_156_ms
    TIME_8_244_ms =  adafruit_ina260.ConversionTime.TIME_8_244_ms


#Oscilloscope Class - Controls all Main Components 
class Oscilloscope:


    MOTOR_1_OUT = 22
    MOTOR_2_OUT = 23
    MOTOR_3_OUT = 24
    MOTOR_4_OUT = 25
    MOTOR_1and2_EN = 5
    MOTOR_3and4_EN = 6
    motorList = {
        1: MOTOR_1_OUT,
        2: MOTOR_2_OUT,
        3: MOTOR_3_OUT,
        4: MOTOR_4_OUT
        }
    DIO1 = 26
    DIO2 = 16

    MCP23017_ADDR  = 0x20  # Address of peripheral on I2C bus
    MCP23017_IODIR_A = 0x00  # IO direction configuration register address A
    MCP23017_IODIR_B = 0x10  # IO direction configuration register address B
    MCP23017_GPPU_A  = 0x06  # Pull-up configuration register address A
    MCP23017_GPPU_B  = 0x16  # Pull-up configuration register address B
    MCP23017_GPIO_A  = 0x09  # GPIO register address A
    MCP23017_GPIO_B  = 0x19  # GPIO register address B

    def __init__(self):
        #Current Sensor
        self.CurrentSensor = None
        #I2S Stereo Decoder
        self.mixer = None
        GPIO.setmode(GPIO.BCM)   
        self.engine = pyttsx3.init()

        #TFT Display Global Variables
        image = None    #The image to be printed (everything included)
        draw = None     #Tool to print onto the display
        disp = None     #Setting up the specific model of the tft display
        backlight = None
        width = None
        height = None



    #------------INA260 Current Sensor----------------
    def setupCurrentSensor(self, bus, address=0x40):
        self.CurrentSensor = adafruit_ina260.INA260(bus)
        self.CurrentSensor.reset_bit = 1
        self.CurrentSensor.mode = CurrentSensorMode.CONTINUOUS
        self.CurrentSensor.averaging_count = AveragingCount.COUNT_4
        self.CurrentSensor.voltage_conversion_time = ConversionTime.TIME_588_us
        self.CurrentSensor.current_conversion_time = ConversionTime.TIME_588_us


    def measureCurrent(self):
        #measure current with sensor
        current = self.CurrentSensor.current
        #print("Current: %.2f " %(current) + "mA")
        return current

    def measureVoltage(self):
        #measure voltage with sensor
        voltage = self.CurrentSensor.voltage
        #print("Voltage: %.2f " %(voltage) + "V")
        return round(voltage, 3)

    def measurePower(self):
        #measure power with sensor
        power = self.CurrentSensor.power
        #print("Power: %.2f " %(power) + "mW")
        return power


    #------------I2S Stereo Decoder---------------
    # initializes StereoDecoder
    def setupSound(self):
        freq=44100
        bitsize=-16
        channels=2
        buffer=2048
        self.mixer = pg.mixer
        self.mixer.init(freq, bitsize, channels, buffer)
        # default starting volume will be 20%
        self.engine.setProperty('rate', 175)
        self.engine.setProperty('voice', 'english+f4')
        soundLevel = self.checkVolume()
        self.mixer.music.set_volume(0.2)


    # queues up and starts audio
    def playSound(self, filename):

        sound = self.mixer.Sound(filename)

        try:
            channela = sound.play()
            time.sleep(sound.get_length())
        except pg.error:
            print("File {} not found! {}".format(filename, pg.get_error()))
            return
            
        #self.mixer.music.play(loops = 0)

    # pauses any playing audio
    def pauseSound(self):
        if self.mixer.music.get_busy():
            self.mixer.pause()
            
    # unpauses any paused audio
    def unpauseSound(self):
        self.mixer.unpause()


    def checkVolume(self):
        currentVolume = None
        return currentVolume


    # increments volume, volume is a float between 0.0 and 1.0
    def increaseVolume(self):
        if self.mixer.music.get_volume() <= 0.9:
            self.mixer.music.set_volume(self.mixer.music.get_volume() + 0.1)

    # decrements volume, volume is a float between 0.0 and 1.0
    def decreaseVolume(self):
        if self.mixer.music.get_volume() >= 0.1:
            self.mixer.music.set_volume(self.mixer.music.get_volume() - 0.1)
        
    # stops all audio
    def stopSound(self):
        self.mixer.stop()

    def createWav(self, text, save_to):

        os.system('festival  -b \'(voice_cmu_us_slt_arctic_hts)\' \'(SayText "' + text + '")\'') 
        
        '''

        temp_file = '/{}.txt'.format(uuid.uuid4())
        if not save_to:
            save_to = '/{}.wav'.format(uuid.uuid4())
        with open(temp_file, 'w') as f:
            f.write(text)
        os.system('text2wave -o {out_fn} {in_fn}'.format(
            out_fn=save_to, in_fn=temp_file))

        '''

        return 

    #------------Motors-------------------
    #Setup 4 Haptic Motors
    #1 and 2 controlled on pin 5
    #3 and 4 controlled on pin 6
    def setupMotors(self):
        #Turn every motor output off just in case, and setup pin
        #Motor 1
        GPIO.setup(self.MOTOR_1_OUT,GPIO.OUT)
        GPIO.output(self.MOTOR_1_OUT,GPIO.LOW)
        #Motor 2
        GPIO.setup(self.MOTOR_2_OUT,GPIO.OUT)
        GPIO.output(self.MOTOR_2_OUT,GPIO.LOW)
        #Motor 3
        GPIO.setup(self.MOTOR_3_OUT,GPIO.OUT)
        GPIO.output(self.MOTOR_3_OUT,GPIO.LOW)
        #Motor 4
        GPIO.setup(self.MOTOR_4_OUT,GPIO.OUT)
        GPIO.output(self.MOTOR_4_OUT,GPIO.LOW)
        #setup enables
        GPIO.setup(self.MOTOR_1and2_EN,GPIO.OUT)
        GPIO.setup(self.MOTOR_3and4_EN,GPIO.OUT)
        GPIO.output(self.MOTOR_1and2_EN,GPIO.HIGH)
        GPIO.output(self.MOTOR_3and4_EN,GPIO.HIGH)


    #Buzzes the selected motor for 3 seconds
    def buzzMotor(self,motorIndex):
        try:
            currentMotor = self.motorList[motorIndex]
        except IndexError:
            print('invalid index')
        GPIO.output(currentMotor,GPIO.HIGH)
        time.sleep(3)  #arbitrary, can be changed later
        GPIO.output(currentMotor,GPIO.LOW)

    #turn motor on indefinitely
    def motorOn(self,motorIndex):
        try:
            currentMotor = self.motorList[motorIndex]
        except IndexError:
            print('invalid index')
        GPIO.output(currentMotor,GPIO.HIGH)

    #Force stop one motor
    def stopMotor(self,motorIndex):
        try:
            currentMotor = self.motorList[motorIndex]
        except IndexError:
            print('invalid index')
        GPIO.output(currentMotor,GPIO.LOW)

    #Force stop all motors
    def stopMotors(self):
        GPIO.output(self.MOTOR_1and2_EN,GPIO.LOW)
        GPIO.output(self.MOTOR_3and4_EN,GPIO.LOW)
        GPIO.output(self.MOTOR_4_OUT,GPIO.LOW)
        GPIO.output(self.MOTOR_1_OUT,GPIO.LOW)
        GPIO.output(self.MOTOR_2_OUT,GPIO.LOW)
        GPIO.output(self.MOTOR_3_OUT,GPIO.LOW)

    #-------------TFT LCD Display------------------

    def setupDisplay(self,spi):
        # Turn on the Backlight
        self.backlight = digitalio.DigitalInOut(board.D25)
        self.backlight.switch_to_output()
        self.backlight.value = True

        # Configuration for CS and DC pins (these are PiTFT defaults):
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D16)

        # Config for display baudrate (default max is 24mhz):
        BAUDRATE = 24000000

        # Create the display:
        self.disp = st7735.ST7735R(spi, rotation=270, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE, )


        # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for full color.
        if self.disp.rotation % 180 == 90:
            self.height = self.disp.width  # we swap height/width to rotate it to landscape!
            self.width = self.disp.height
        else:
            self.width = self.disp.width  # we swap height/width to rotate it to landscape!
            self.height = self.disp.height

        self.image = Image.new("RGB", (self.width, self.height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

    def clearDisplay(self):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 0, 0))
        self.disp.image(self.image)

    def displayOff(self):
        # Turn off Backlight
        self.backlight.value = False #NEEDS FIXING <================================================================================

    def displayOn(self):
        # Turn on Backlight
        self.backlight.value = True

    def displayImage(self,imageFile):
        self.clearDisplay()

        #Try to load in image but if filename doesnt exist, return
        try:
            self.image = Image.open(imageFile)
        except:
            print("---ERROR: ",imageFile," does not exist---")
            return 1

        # Scale the image to the smaller screen dimension
        image_ratio = self.image.width / self.image.height
        screen_ratio = self.width / self.height
        if screen_ratio < image_ratio:
            scaled_width = self.image.width * self.height // self.image.height
            scaled_height = self.height
        else:
            scaled_width = self.width
            scaled_height = self.image.height * self.width // self.image.width
        self.image = self.image.resize((scaled_width, scaled_height), Image.BICUBIC)

        # Crop and center the image
        x = scaled_width // 2 - self.width // 2
        y = scaled_height // 2 - self.height // 2
        self.image = self.image.crop((x, y, x + self.width, y + self.height))

        # Display image.
        self.disp.image(self.image)

    def displayText(self,text,custom=False,x=0,y=0,font_size=18):
        #self.clearDisplay()

        # First define some constants to allow easy resizing of shapes.
        BORDER = 32
        FONTSIZE = font_size

        # Draw a black filled box as the background
        # technically redundant as clearDisplay does the same thing
        #self.draw.rectangle((0, 0, self.width, self.height), fill=(0, 0, 0))
        #self.disp.image(self.image)

        # Load a TTF Font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

        # Draw Some Text
        (font_width, font_height) = font.getsize(text)
        if custom == True:
            self.draw.text((x,y),text,font=font,fill=(255, 255, 0),)
        else:
            self.draw.text((self.width // 2 - font_width // 2, self.height // 2 - font_height // 2),text,font=font,fill=(255, 255, 0),)
        
        # Display image.
        self.disp.image(self.image)

    '''
    -----------------Buttons/Multiplexer---------------------

    GPIOA0-5 = Advanced Buttons 
    GPIOA0 = Single Shot Voltage = 62
    GPIOA1 = Single Shot Current = 61
    GPIOA2 = Continuous Voltage = 59
    GPIOA3 = Continuous Current = 55
    GPIOA4 = DIO1 = 47
    GPIOA5 = DIO2 = 31

    GPIOB0-4 = Switch and Basic Buttons
    GPIOB0 = Home = 14
    GPIOB1 = Play = 13
    GPIOB2 = Next = 11
    GPIOB3 = Switch Basic Side 
    GPIOB4 = Switch Advanced Side 


    '''

    def setPinDir(self,i2cBus, AorB, pin, isInput, pullup = False):

        if AorB == 'A':
            IODIR = self.MCP23017_IODIR_A
            GPPU = self.MCP23017_GPPU_A
        elif AorB == 'B':
            IODIR = self.MCP23017_IODIR_B
            GPPU = self.MCP23017_GPPU_B
        else:
            print('neither A or B given')

        directionReg = i2cBus.read_byte_data(self.MCP23017_ADDR, IODIR)

        if isInput:
            directionReg |= (1 << pin)
        else:
            directionReg = directionReg & ~(1<<pin)

        i2cBus.write_byte_data(self.MCP23017_ADDR, IODIR, directionReg)

        if isInput:
            puReg = i2cBus.read_byte_data(self.MCP23017_ADDR, GPPU)
            if pullup:
                puReg = puReg | (1<<pin)
            else:
                puReg = puReg & ~(1<<pin)
            i2cBus.write_byte_data(self.MCP23017_ADDR, GPPU, puReg)


    def setupButtons(self, i2cBus):

        IOCON = i2cBus.read_byte_data(self.MCP23017_ADDR, 0x0A)

        if IOCON == 0:
            IOCON = IOCON | (1<<7)
            i2cBus.write_byte_data(self.MCP23017_ADDR, 0x0A, IOCON)     

        #Set up all pins as input
        i2cBus.write_byte_data(self.MCP23017_ADDR, self.MCP23017_IODIR_A, 0xFF)
        i2cBus.write_byte_data(self.MCP23017_ADDR, self.MCP23017_IODIR_B, 0xFF)

        self.setPinDir(i2cBus,'A', 0, 1, pullup=True)
        self.setPinDir(i2cBus,'A', 1, 1, pullup=True)
        self.setPinDir(i2cBus,'A', 2, 1, pullup=True)
        self.setPinDir(i2cBus,'A', 3, 1, pullup=True)
        self.setPinDir(i2cBus,'A', 4, 1, pullup=True)
        self.setPinDir(i2cBus,'A', 5, 1, pullup=True)
        self.setPinDir(i2cBus,'B', 0, 1, pullup=True)
        self.setPinDir(i2cBus,'B', 1, 1, pullup=True)
        self.setPinDir(i2cBus,'B', 2, 1, pullup=True)
        self.setPinDir(i2cBus,'B', 3, 1, pullup=True)
        self.setPinDir(i2cBus,'B', 4, 1, pullup=True)

    def readButton(self,i2cBus, AorB, pin):

        if AorB == 'A':
            GPIO = self.MCP23017_GPIO_A
        elif AorB == 'B':
            GPIO = self.MCP23017_GPIO_B
        else:
            print('neither A or B given')

        gpioReg = i2cBus.read_byte_data(self.MCP23017_ADDR, GPIO)

        return (gpioReg >> pin) & 0x01

    def readAllButtons(self,i2cBus):
        A = i2cBus.read_byte_data(self.MCP23017_ADDR, self.MCP23017_GPIO_A)
        B = i2cBus.read_byte_data(self.MCP23017_ADDR, self.MCP23017_GPIO_B)
        return A,B

    #----------------Digital Input--------------------------


    def setupDigitalPins(self):
        GPIO.setup(self.DIO1, GPIO.IN)
        GPIO.setup(self.DIO2, GPIO.IN)

    def readDigitalPin(self):
        x = GPIO.input(self.DIO1)
        y = GPIO.input(self.DIO2)
        return (x,y)



