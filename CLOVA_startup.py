import os
import time
import subprocess
import RPi.GPIO as GPIO
from CLOVA_led import IndicatorLed as ind_led

# スイッチが接続されているGPIO番号
PIN_FRONT_SW = 4
PIN_BACK_SW_MUTE = 7

# LEDが接続されているGPIO番号
#PIN_LED_G = 12

# 別のPythonスクリプトが実行中かどうかを確認する関数
def is_process_running(process_name):
    try:
        subprocess.check_output(["pidof", process_name])
        return True
    except subprocess.CalledProcessError:
        return False

# まだ起動していなければ CLOVA_RasPi.py を起動する関数
def start_main():
    if not is_process_running("CLOVA_RasPi.py"):
        program_path = os.path.expanduser("~/CLOVA_RasPi/CLOVA_RasPi.py")
        print("Starting : {}".format(program_path))
        subprocess.Popen(["/usr/bin/python3", program_path])
        time.sleep(1)

# GPIOの初期化
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_BACK_SW_MUTE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
led = ind_led()

# スイッチの状態を監視し、押された場合にMyAppli.pyを起動する
while True:
    if not GPIO.input(PIN_BACK_SW_MUTE):
        print("Sw ON!")
        led.set_led(led.LED_ON)
        #GPIO.output(PIN_LED_G, True)
        start_main()
    else:
        led.set_led(led.LED_OFF)
        #GPIO.output(PIN_LED_G, False)
    time.sleep(0.1)
