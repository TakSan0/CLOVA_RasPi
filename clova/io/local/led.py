import time
try:
    import RPi.GPIO as GPIO
    import smbus
except:
    from fake_rpi.RPi import GPIO
    from fake_rpi import smbus

PIN_FRONT_SW = 4
PIN_BACK_SW_MINUS = 2
PIN_BACK_SW_PLUS = 3
PIN_BACK_SW_BT = 5
PIN_BACK_SW_MUTE = 7
PIN_POWER_SW = 22

PIN_IND_LED_R = 13
PIN_IND_LED_G = 12
PIN_IND_LED_B = 6

PIN_ILL_LED_POW = 23
PIN_ILL_LED_ENA = 24

# ==================================
#    LEDインジケータ制御クラス
# ==================================
class IndicatorLed :
    LED_OFF = False
    LED_ON = True

    # コンストラクタ
    def __init__(self) :
        print("Create <IndicatorLed> class")

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_IND_LED_G, GPIO.OUT)

    # デストラクタ
    def __del__(self) :
        print("Delete <IndicatorLed class")

        GPIO.cleanup(PIN_IND_LED_G)

    # LEDインディケーター On/Off
    def set_led(self, onoff, pin = PIN_IND_LED_G) :
        GPIO.output(pin, onoff)

# ==================================
#   イルミネーションLED制御クラス
# ==================================
class IllminationLed :
    I2C_SEL_CH = 0
    SLAVE_ADDR = 0x50
    REG_ADDRESS_TABLE = [
        [0x02, 0x22, 0x42], [0x12, 0x32, 0x52],
        [0x01, 0x21, 0x41], [0x11, 0x31, 0x51],
        [0x00, 0x20, 0x40], [0x10, 0x30, 0x50],
        [0x60, 0x80, 0xA0], [0x70, 0x90, 0xB0],
        [0x61, 0x81, 0xA1], [0x71, 0x91, 0xB1],
        [0x62, 0x82, 0xA2], [0x72, 0x92, 0xB2],
        [0x63, 0x83, 0xA3], [0x73, 0x93, 0xB3],
        [0x64, 0x84, 0xA4], [0x74, 0x94, 0xB4],
        [0x65, 0x85, 0xA5], [0x75, 0x95, 0xB5],
        [0x05, 0x25, 0x45], [0x15, 0x35, 0x55],
        [0x04, 0x24, 0x44], [0x14, 0x34, 0x54],
        [0x03, 0x23, 0x43], [0x13, 0x33, 0x53]
    ]
    RGB_OFF        = [0x00, 0x00, 0x00]
    RGB_BLACK      = [0x00, 0x00, 0x00]
    RGB_RED        = [0xFF, 0x00, 0x00]
    RGB_DARKGREEN  = [0x00, 0x1F, 0x00]
    RGB_GREEN      = [0x00, 0xFF, 0x00]
    RGB_BLUE       = [0x00, 0x00, 0xFF]
    RGB_ORANGE     = [0xFF, 0x7F, 0x00]
    RGB_YELLOW     = [0xFF, 0xFF, 0x00]
    RGB_PINK       = [0xFF, 0x00, 0xFF]
    RGB_CYAN       = [0x00, 0xFF, 0xFF]
    RGB_LIST = [RGB_OFF, RGB_BLACK, RGB_RED, RGB_DARKGREEN, RGB_GREEN, RGB_BLUE, RGB_ORANGE, RGB_YELLOW, RGB_PINK, RGB_CYAN]

    ALL_BITS = 0xFFFFFFF

    # コンストラクタ
    def __init__(self) :
        self.is_available = False
        print("Create <IllminationLed> class")
        self.init()

    # デストラクタ
    def __del__(self) :
        print("Delete <IllminationLed> class")

        try:
            self.set_all(global_led_Ill.RGB_RED)
            self.finalize()
        except Exception:
            print("Delete <IllminationLed> fail; seems to be already finalized?")

    # 初期化処理
    def init(self) :
        # Initialize Lib
        GPIO.setmode(GPIO.BCM)
        try :
            self.is_available = True
            self._i2c = smbus.SMBus(self.I2C_SEL_CH)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x00, 0x01)

            print("LED control device found at addr:{}".format(self.I2C_SEL_CH))
        except IOError:
            self.is_available = False
            print("IOError : LED control device not found!")

        except Exception as e:
            self.is_available = False
            print("Error : LED control device : {}".format(str(e)))

        print("Ill LED Initialized")

        # Initialize GPIO
        GPIO.setup(PIN_ILL_LED_POW, GPIO.OUT)
        GPIO.output(PIN_ILL_LED_POW, GPIO.LOW)
        GPIO.setup(PIN_ILL_LED_ENA, GPIO.OUT)
        GPIO.output(PIN_ILL_LED_ENA, GPIO.LOW)
        time.sleep(3.0)

        # Power ON
        GPIO.output(PIN_ILL_LED_POW, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(PIN_ILL_LED_ENA, GPIO.HIGH)

        if (self.is_available == True) :
            # Send Initialize Command
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0xFE, 0xC5)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0xFD, 0x03)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x00, 0x01)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x01, 0xFF)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x0F, 0x07)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x10, 0x07)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0xFE, 0xC5)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0xFD, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x00, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x01, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x02, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x03, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x04, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x05, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x06, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x07, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x08, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x09, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x0A, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x0B, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x0C, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x0D, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x0E, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x0F, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x10, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x11, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x12, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x13, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x14, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x15, 0x00)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x16, 0x3F)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0x17, 0x00)

    # コマンドヘッダーの送信
    def send_command_header(self) :
        if (self.is_available == True) :
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0xFE, 0xC5)
            self._i2c.write_byte_data(self.SLAVE_ADDR, 0xFD, 0x01)
        else :
            print("LED Device unavailable!")

    # ビット指定でRGB食を指定設定
    def set_leds_with_bit_mask(self, bits, rgb_color) :
        if (self.is_available == True) :
            self.send_command_header()
            for num in range(len(self.REG_ADDRESS_TABLE)):
                for rgb in range(len(self.REG_ADDRESS_TABLE[num])):
                    bits_mask = (1 << num)
                    if ( ( bits_mask & bits) != 0 ) :
                        self._i2c.write_byte_data(self.SLAVE_ADDR, self.REG_ADDRESS_TABLE[num][rgb], rgb_color[rgb] )
                    else :
                        self._i2c.write_byte_data(self.SLAVE_ADDR, self.REG_ADDRESS_TABLE[num][rgb], self.RGB_OFF[rgb] )
            time.sleep(0.05)
        else :
            print("LED Device unavailable!")

    # 配列指定ですべての LED を設定する
    def set_all_led_with_array(self, rgb_data) :
        if (self.is_available == True) :
            self.send_command_header()
            for num in range(len(rgb_data)):
                for rgb in range(len(rgb_data[num])):
                    self._i2c.write_byte_data(self.SLAVE_ADDR, self.REG_ADDRESS_TABLE[num][rgb], rgb_data[num][rgb] )
        else :
            print("LED Device unavailable!")

    def set_all(self, rgb):
        self.set_leds_with_bit_mask(self.ALL_BITS, rgb)

    # 終了処理
    def finalize(self) :
        GPIO.cleanup(PIN_ILL_LED_POW)
        GPIO.cleanup(PIN_ILL_LED_ENA)
        print("Finalize")

# ==================================
#      外部参照用のインスタンス
# ==================================
global_led_Ill = IllminationLed()

# ==================================
#       本クラスのテスト用処理
# ==================================

def load_illumi_data(data_bytes, child_length, grandchild_length):
    result = []
    current_index = 0

    while current_index < len(data_bytes):
        child = []
        for _ in range(child_length):
            grandchild = []
            for _ in range(grandchild_length):
                grandchild.append(data_bytes[current_index])
                current_index += 1
            child.append(grandchild)
        result.append(child)

    return result

# # For making illumi_data to a file:
# def illumi_data_to_bytes(illumi_data):
#     flattened = [byte for sublist in illumi_data for subsublist in sublist for byte in subsublist]
#     return bytes(flattened)

def module_test() :
    with open('./assets/illumi_test.bin', 'rb') as file:
        data_bytes = file.read()
    illumi_data = load_illumi_data(data_bytes, 22, 3)

    ill_led = IllminationLed()
    for color in ill_led.RGB_LIST:
        ill_led.set_all(color)
        time.sleep(0.5)

    ill_led.set_all(ill_led.RGB_BLACK)

    for step in range(len(illumi_data)):
        ill_led.set_all_led_with_array(illumi_data[step])
        time.sleep(0.05)

# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    module_test()

