try:
    import RPi.GPIO as GPIO
except BaseException:
    from fake_rpi.RPi import GPIO

from clova.general.logger import BaseLogger

# ==================================
#           キー入力クラス
# ==================================


class SwitchInput(BaseLogger):
    # PIN_FRONT_SW = 26
    # PIN_FRONT_SW = 4	# 起動に使うので、これはサポート対象外とする
    PIN_BACK_SW_MINUS = 2
    PIN_BACK_SW_PLUS = 3
    PIN_BACK_SW_BT = 5
    PIN_BACK_SW_MUTE = 7
    # PIN_POWER_SW = 22 # 電源OFFキーに使っているので、これはサポート対象外とする

    KEY_UP = False
    KEY_DOWN = True

    # コンストラクタ
    def __init__(self, pin, cb_func):
        super().__init__()

        self.log("CTOR", "Pin={}".format(pin))

        self._pin = pin
        self.log("CTOR", "GPIO.setup({}, {}, {})".format(self._pin, GPIO.IN, GPIO.PUD_UP))
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self._pin, GPIO.FALLING, callback=cb_func, bouncetime=200)

    # デストラクタ
    def __del__(self):
        super().__del__()

        self.log("DTOR", "Pin={}".format(self._pin))
        self.release()

    # 解放処理
    def release(self):
        self.log("release", "Relase key({})".format(self._pin))
        GPIO.remove_event_detect(self._pin)
        GPIO.cleanup(self._pin)

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
