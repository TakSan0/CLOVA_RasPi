try:
    import RPi.GPIO as GPIO
except BaseException:
    from fake_rpi.RPi import GPIO

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
#           GPIO制御クラス
# ==================================


class GPIOControl:
    # コンストラクタ
    def __init__(self):
        print("Create <GPIOControl> class")

        self.init()

    # デストラクタ
    def __del__(self):
        # 現状ログ出すだけ
        print("Delete <GPIOControl> class")

    # 初期化処理
    def init():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_BACK_SW_MINUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PIN_BACK_SW_PLUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PIN_BACK_SW_BT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PIN_BACK_SW_MUTE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PIN_ILL_LED_POW, GPIO.OUT)
        GPIO.output(PIN_ILL_LED_POW, GPIO.LOW)
        GPIO.setup(PIN_ILL_LED_ENA, GPIO.OUT)
        GPIO.output(PIN_ILL_LED_ENA, GPIO.LOW)

    # 解放処理
    def release():
        GPIO.cleanup(PIN_BACK_SW_MINUS)
        GPIO.cleanup(PIN_BACK_SW_PLUS)
        GPIO.cleanup(PIN_BACK_SW_BT)
        GPIO.cleanup(PIN_BACK_SW_MUTE)
        GPIO.cleanup(PIN_ILL_LED_POW)
        GPIO.cleanup(PIN_ILL_LED_ENA)

# ==================================
#       本クラスのテスト用処理
# ==================================


def module_test():
    # 現状何もしない
    pass


# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    module_test()
