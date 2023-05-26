import sys
import threading
import time
try:
    import RPi.GPIO as GPIO
except:
    from fake_rpi.RPi import GPIO
import wave
import pyaudio as PyAudio

from clova.general.voice import VoiceController
from clova.general.queue import global_speech_queue

PIN_FRONT_SW = 4
PIN_BACK_SW_MINUS = 2
PIN_BACK_SW_PLUS = 3
PIN_BACK_SW_BT = 5
PIN_BACK_SW_MUTE = 7
PIN_POWER_SW = 22

PIN_LED_R = 13
PIN_LED_G = 12
PIN_LED_B = 6

WAV_FILENAME = "/tmp/clova_speech.wav"

# ==================================
#           テスト用クラス
# ==================================
class TestClass :

    # コンストラクタ
    def __init__(self) :
        print("Create <TestClass> class")
        self.is_active = False

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <TestClass> class")

    def task_test_playback(self) :
        voice = VoiceController()
        while(self.is_active) :
            record_data = voice.microphone_record()
            with wave.open(WAV_FILENAME, "wb") as out:
                out.setnchannels(voice.mic_num_ch)
                out.setsampwidth(2)
                out.setframerate(16000)
                out.writeframes(record_data)

            time.sleep(0.5)

            print("再生開始")
            voice.play_audio_file(WAV_FILENAME)
            print("再生終了")

            time.sleep(1.5)

    def task_test_gpio(self) :
        sw_front_before = -1
        sw_back_minus_before = -1
        sw_back_plus_before = -1
        sw_back_bt_before = -1
        sw_back_mute_before = -1
        sw_power_before = -1

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(PIN_FRONT_SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PIN_BACK_SW_MINUS, GPIO.IN)
        GPIO.setup(PIN_BACK_SW_PLUS, GPIO.IN)
        GPIO.setup(PIN_BACK_SW_BT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PIN_BACK_SW_MUTE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PIN_POWER_SW, GPIO.IN)

        GPIO.setup(PIN_LED_R, GPIO.OUT)
        GPIO.setup(PIN_LED_G, GPIO.OUT)
        GPIO.setup(PIN_LED_B, GPIO.OUT)
        GPIO.output(PIN_LED_R, GPIO.LOW)
        GPIO.output(PIN_LED_G, GPIO.LOW)
        GPIO.output(PIN_LED_B, GPIO.LOW)

        while(self.is_active) :
            sw_front = GPIO.input(PIN_FRONT_SW)
            sw_back_minus = GPIO.input(PIN_BACK_SW_MINUS)
            sw_back_plus = GPIO.input(PIN_BACK_SW_PLUS)
            sw_back_bt = GPIO.input(PIN_BACK_SW_BT)
            sw_back_mute = GPIO.input(PIN_BACK_SW_MUTE)
            sw_power = GPIO.input(PIN_POWER_SW)

            if sw_front_before != sw_front :
                if (sw_front == GPIO.HIGH) :
                    print("[FRONT] switch is OFF")
                else :
                    print("[FRONT] switch is ON")
            if sw_back_minus_before != sw_back_minus :
                if (sw_back_minus == GPIO.HIGH) :
                    print("[-] switch is OFF")
                    GPIO.output(PIN_LED_B, GPIO.LOW)
                    print("[B] LED is OFF")
                else :
                    print("[-] switch is ON")
                    GPIO.output(PIN_LED_B, GPIO.HIGH)
                    print("[B] LED is ON")
            if sw_back_plus_before != sw_back_plus :
                if (sw_back_plus == GPIO.HIGH) :
                    GPIO.output(PIN_LED_G, GPIO.LOW)
                    print("[R] LED is OFF")
                    print("[+] switch is OFF")
                else :
                    print("[+] switch is ON")
                    GPIO.output(PIN_LED_G, GPIO.HIGH)
                    print("[R] LED is ON")
            if sw_back_bt_before != sw_back_bt :
                if (sw_back_bt == GPIO.HIGH) :
                    print("[BT] switch is OFF")
                    GPIO.output(PIN_LED_R, GPIO.LOW)
                    print("[R] LED is OFF")
                else :
                    print("[BT] switch is ON")
                    GPIO.output(PIN_LED_R, GPIO.HIGH)
                    print("[R] LED is ON")
            if sw_back_mute_before != sw_back_mute :
                if (sw_back_mute == GPIO.HIGH) :
                    print("[MUTE] switch is OFF")
                else :
                    print("[MUTE] switch is ON")
            if sw_power_before != sw_power :
                if (sw_power == GPIO.HIGH) :
                    print("[POWER] switch is OFF")
                else :
                    print("[POWER] switch is ON")

            time.sleep(0.5)
            sw_front_before = sw_front
            sw_back_minus_before = sw_back_minus
            sw_back_plus_before = sw_back_plus
            sw_back_bt_before = sw_back_bt
            sw_back_mute_before = sw_back_mute
            sw_power_before = sw_power

        GPIO.cleanup(PIN_FRONT_SW)
        GPIO.cleanup(PIN_BACK_SW_MINUS)
        GPIO.cleanup(PIN_BACK_SW_PLUS)
        GPIO.cleanup(PIN_BACK_SW_BT)
        GPIO.cleanup(PIN_BACK_SW_MUTE)
        GPIO.cleanup(PIN_POWER_SW)

        GPIO.cleanup(PIN_LED_R)
        GPIO.cleanup(PIN_LED_G)
        GPIO.cleanup(PIN_LED_B)

    def scan_indexes(self):
        pyaud = PyAudio.PyAudio()

        print ("デバイスインデックス総数: {0}".format(pyaud.get_device_count()))

        found_index = -1
        for i in range(pyaud.get_device_count()):
            line_str = pyaud.get_device_info_by_index(i)
            print (line_str)
            json_data = line_str#json.loads(line_str)

            # print("{}:{},{},{}".format(json_data["index"],json_data["name"],json_data["maxInputChannels"],json_data["maxOutputChannels"])) #デバッグ用
            if ( ( json_data["name"] == "dmic_hw" ) and (json_data["maxInputChannels"] != 0) and (json_data["maxOutputChannels"] != 0) ):
                found_index = json_data["index"]

        if (found_index != -1) :
            print("入力(MIC)デバイスインデックス = {}".format(found_index))
            print("出力(SPEAKER)デバイスインデックス = {}".format(found_index))
        else :
            print("該当するものが見当たりません。設定が正しいか確認してください。")


# ==================================
#       本クラスのテスト用処理
# ==================================
def module_test() :
    # 呼び出し引数チェック
    if ((len(sys.argv) == 2) and (sys.argv[1]!="-h") and (sys.argv[1]!="--help")):
        test = TestClass()

        # ハードテスト用
        if (sys.argv[1] == "hw_test") :
            print("Ready! Press any switch to test or press [Enter] key to exit")

            test.is_active = True
            gpio_test_thread = threading.Thread(target = test.task_test_gpio, args = (), name = "GpioTestTask", daemon = True)
            pb_test_thread = threading.Thread(target = test.task_test_playback, args = (), name = "GpioTestTask", daemon = True)
            gpio_test_thread.start()
            pb_test_thread.start()

            input()

            global_speech_queue.add("終了")
            time.sleep(1)
            test.is_active = False
            print("Exit")
            time.sleep(1)
            gpio_test_thread.join()
            pb_test_thread.join()

        # インデックス値のスキャン
        elif (sys.argv[1] == "get_indecies") :
            test.scan_indexes()

        # マイクの最低音量調整
        elif (sys.argv[1] == "adjust_mic") :
            print("マイクの最低音量調整用のテストは未実装")

        # それ以外(不正)の場合
        else :
            if (len(sys.argv) != 2) :
                print("No test type specified{}".format(len(sys.argv)))
            else :
                print("Invalid test type :'{}' ".format(sys.argv[1]))

    # ヘルプ表示
    else :
        print("Usage> python CLOVA_test.py [test type]")
        print("  [test type] : hw_test / get_indecies / adjust_mic")

# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    module_test()

