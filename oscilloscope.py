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


    def __init__(self):
        #Current Sensor
        self.CurrentSensor = None
        #I2S Stereo Decoder
        self.mixer = None
        GPIO.setmode(GPIO.BCM)


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
        return voltage

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
        self.mixer.music.set_volume(0.2)

        engine = pyttsx3.init()


    # queues up and starts audio
    def playSound(self, filename):

        try:
            self.mixer.music.load(filename)
        except pg.error:
            print("File {} not found! {}".format(filename, pg.get_error()))
            return
            
        self.mixer.music.play(-1)

    # pauses any playing audio
    def pauseSound(self):
        if self.mixer.music.get_busy():
            self.mixer.pause()
            
    # unpauses any paused audio
    def unpauseSound(self):
        self.mixer.unpause()


    def checkVolume(self):
        return


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
        backlight = digitalio.DigitalInOut(board.D25)
        backlight.switch_to_output()
        backlight.value = True

        # Configuration for CS and DC pins (these are PiTFT defaults):
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D24)

        # Config for display baudrate (default max is 24mhz):
        BAUDRATE = 24000000

        # Create the display:
        disp = st7735.ST7735R(spi, rotation=270, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE, )


        # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for full color.
        if disp.rotation % 180 == 90:
            height = disp.width  # we swap height/width to rotate it to landscape!
            width = disp.height
        else:
            width = disp.width  # we swap height/width to rotate it to landscape!
            height = disp.height

        image = Image.new("RGB", (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        return image,draw,disp,backlight,width,height

    def clearDisplay(self,image,draw,disp,width,height):
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
        disp.image(image)

    def displayOff(self,backlight):
        # Turn off Backlight
        backlight.value = False

    def displayOn(self,backlight):
        # Turn on Backlight
        backlight.value = True

    def displayImage(self,imageFile,image,draw,disp,width,height):
        self.clearDisplay(image,draw,disp,width,height)

        #Try to load in image but if filename doesnt exist, return
        try:
            image = Image.open(imageFile)
        except:
            print("---ERROR: ",imageFile," does not exist---")
            return 1

        # Scale the image to the smaller screen dimension
        image_ratio = image.width / image.height
        screen_ratio = width / height
        if screen_ratio < image_ratio:
            scaled_width = image.width * height // image.height
            scaled_height = height
        else:
            scaled_width = width
            scaled_height = image.height * width // image.width
        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

        # Crop and center the image
        x = scaled_width // 2 - width // 2
        y = scaled_height // 2 - height // 2
        image = image.crop((x, y, x + width, y + height))

        # Display image.
        disp.image(image)
        return 0

    def displayText(self,text,image,draw,disp,width,height):
        self.clearDisplay(image, draw, disp, width, height)

        # First define some constants to allow easy resizing of shapes.
        BORDER = 32
        FONTSIZE = 18

        # Draw a black filled box as the background
        # technically redundant as clearDisplay does the same thing
        draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
        disp.image(image)

        # Load a TTF Font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

        # Draw Some Text
        (font_width, font_height) = font.getsize(text)
        draw.text((width // 2 - font_width // 2, height // 2 - font_height // 2),text,font=font,fill=(255, 255, 0),)

        # Display image.
        disp.image(image)


    #-----------------Buttons/Multiplexer---------------------

    def setupButtons(self):
        pass

    def getButtonState(self,buttonIndex):
        pass



    #----------------Digital Input--------------------------


    def setupDigitalPins(self):
        GPIO.setup(self.DIO1, GPIO.IN)
        GPIO.setup(self.DIO2, GPIO.IN)

    def readDigitalPin(self):
        x = GPIO.input(self.DIO1)
        y = GPIO.input(self.DIO2)
        return (x,y)



