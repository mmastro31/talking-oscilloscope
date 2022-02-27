import adafruit_ina260
import board
import busio
<<<<<<< Updated upstream
import time
=======
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7735
>>>>>>> Stashed changes

class Oscilloscope:

    def __init__(self):
        self.CurrentSensor = None

    #INA260 Current Sensor

    count_dict = {0: adafruit_ina260.AveragingCount.COUNT_1,
                1: adafruit_ina260.AveragingCount.COUNT_4, 
                2: adafruit_ina260.AveragingCount.COUNT_16,
                3: adafruit_ina260.AveragingCount.COUNT_64,
                4: adafruit_ina260.AveragingCount.COUNT_128,
                5: adafruit_ina260.AveragingCount.COUNT_256,
                6: adafruit_ina260.AveragingCount.COUNT_512,
                7: adafruit_ina260.AveragingCount.COUNT_1024}
    conv_dict = {0: adafruit_ina260.ConversionTime.TIME_140_us,
            1: adafruit_ina260.ConversionTime.TIME_204_us,
            2: adafruit_ina260.ConversionTime.TIME_332_us,
            3: adafruit_ina260.ConversionTime.TIME_588_us,
            4: adafruit_ina260.ConversionTime.TIME_1_1_ms,
            5: adafruit_ina260.ConversionTime.TIME_2_116_ms,
            6: adafruit_ina260.ConversionTime.TIME_4_156_ms,
            7: adafruit_ina260.ConversionTime.TIME_8_244_ms,
        }

    def setupCurrentSensor(self, bus, address=0x40):
        self.CurrentSensor = adafruit_ina260.INA260(bus)
        self.CurrentSensor.reset_bit = 1
        self.CurrentSensor.mode = adafruit_ina260.Mode.CONTINUOUS
        self.CurrentSensor.averaging_count = adafruit_ina260.AveragingCount.COUNT_4
        self.CurrentSensor.voltage_conversion_time = adafruit_ina260.ConversionTime.TIME_588_us
        self.CurrentSensor.current_conversion_time = adafruit_ina260.ConversionTime.TIME_588_us


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

    def changeCurrentSensorMode(self,num):
        #Change Mode Current Sensor is operating in
        #0 = CONTINUOUS
        #1 = TRIGGERED
        #2 = SHUTDOWN
        if num == 0:
            self.CurrentSensor.mode = adafruit_ina260.Mode.CONTINUOUS
        elif num == 1:
            self.CurrentSensor.mode = adafruit_ina260.Mode.TRIGGERED
        elif num ==2:
            self.CurrentSensor.mode = adafruit_ina260.Mode.SHUTDOWN
        else:
            print("Incorrect input. Please select 0, 1, or 2")
    
    def currentSensorCount(self,num):
        #Dictionary is above.
        #0-7 correspond to count
        #invalid if other number
        if num < 0 or num > 7:
            print('invalid index. Please select 0-7')
        else:
            newCount = self.count_dict[num]
            self.CurrentSensor.averaging_count = newCount
        
    def currentSensorTiming(self,num):
        #Dictionary is above. (conv_dict)
        #0-7 corresponds to conversion time
        #invalid if other number
        if num < 0 or num > 7:
            print('invalid index number. Please select 0-7')
        else:
            newTime = self.conv_dict[num]
            self.CurrentSensor.voltage_conversion_time = newTime
            self.CurrentSensor.current_conversion_time = newTime

    #I2S Stereo Decoder

    def soundOut():
        pass

    def setupSound():
        pass

    #Motors / H-Bridge

    def buzzMotor():
        pass

    def setupMotor():
        pass

    def getMotorState():
        pass

    def stopMotor():
        pass

    #TFT LCD Display

    def setupDisplay():
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

        # Setup SPI bus using hardware SPI:
        spi = board.SPI()

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

    def displayOff():
        # Turn on the Backlight
        backlight = digitalio.DigitalInOut(board.D25)
        backlight.switch_to_output()
        backlight.value = False

    def displayImage():
        image = Image.new("RGB", (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
        disp.image(image)

        image = Image.open("blinka.JPG")

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

    def displayText():
        # First define some constants to allow easy resizing of shapes.
        BORDER = 20
        FONTSIZE = 24

        image = Image.new("RGB", (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a green filled box as the background
        draw.rectangle((0, 0, width, height), fill=(0, 255, 0))
        disp.image(image)

        # Draw a smaller inner purple rectangle
        draw.rectangle(
            (BORDER, BORDER, width - BORDER - 1, height - BORDER - 1), fill=(170, 0, 136)
        )

        # Load a TTF Font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

        # Draw Some Text
        text = "Hello World!"
        (font_width, font_height) = font.getsize(text)
        draw.text(
            (width // 2 - font_width // 2, height // 2 - font_height // 2),
            text,
            font=font,
            fill=(255, 255, 0),
        )

        # Display image.
        disp.image(image)

    def clearDisplay():
        pass

    #Buttons

    def getButtonState():
        pass

    def setupButton():
        pass
