import threading as th
import time
import RPi.GPIO as GPIO

# ==================================
#           キー入力クラス
# ==================================
class KeyInput :
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
    def __init__(self, pin, cb_func) :
        print("Create <KeyInput> class / Pin={}".format(pin))

        self._pin = pin
        print("GPIO.setup({}, {}, {})".format(self._pin, GPIO.IN, GPIO.PUD_UP))
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self._pin, GPIO.FALLING, callback=cb_func, bouncetime = 200)

    # デストラクタ
    def __del__(self) :
        print("Delete <KeyInput> class / Pin={}".format(self._pin))
        self.Release()

    # 解放処理
    def Release(self) :
        print("Relase key({})".format(self._pin))
        GPIO.remove_event_detect(self._pin)
        GPIO.cleanup(self._pin)

# ==================================
#       本クラスのテスト用処理
# ==================================
def ModuleTest() :
    # 現状何もしない
    pass

# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    ModuleTest()

