import time
import os

import RPi.GPIO as GPIO
from CLOVA_config import global_config_sys
from CLOVA_config import HttpReqSettingHandler
from CLOVA_led import global_led_Ill
from CLOVA_timer import TimerControl
from CLOVA_switch import SwitchInput
from CLOVA_volume import global_vol
from CLOVA_charactor import global_charactor
from CLOVA_conversation import Conversation
from CLOVA_voice import VoiceControl
from CLOVA_http_server import HttpServer
from CLOVA_line import LineSender, HttpReqLineHandler

def main() :
    # 会話モジュールのインスタンス作成
    conv = Conversation()

    # HTTPサーバー系のインスタンス作成
    line_svr = HttpServer(8080, HttpReqLineHandler)
    config_svr = HttpServer(8000, HttpReqSettingHandler)

    # LINE送信モジュールのインスタンス
    line_sender = LineSender()

    # 底面 LED を黄色に
    global_led_Ill.AllYellow()

    # LEDを使うモジュールにインスタンスをコピー
    voice = VoiceControl()

    # キー準備
    char_swich = SwitchInput(SwitchInput.PIN_BACK_SW_BT, global_charactor.SelNextChar)
    plus_swich = SwitchInput(SwitchInput.PIN_BACK_SW_PLUS, global_vol.VolUpCallback)
    minus_swich = SwitchInput(SwitchInput.PIN_BACK_SW_MINUS, global_vol.VolDownCallback)

    # タイマ準備
    tmr = TimerControl()
    conv.tmr = tmr
    #tmr.Start()

    # キャラクタ設定
    global_charactor.SetCharactor(global_config_sys.settings["charactor"]["default_sel"])

    # メインループ
    while True :

        int_exists, speeched_text = conv.CheckIfInterruptedVoiceExists()

        # 割り込み音声ありの時
        if ( int_exists == True) :
            if speeched_text != "" :
                filename = voice.TextToSpeech(speeched_text)
                if (filename != "") :
                    voice.PlayAudioFile(filename)
                else :
                    print("音声ファイルを取得できませんでした。")

        # 割り込み音声無の時
        else :
            answered_text = ""

            # 録音
            record_data = voice.RecordFromMic()

            # テキストに返還
            speeched_text = voice.SpeechToText(record_data)
            #speeched_text = speech_to_text_by_google_speech_recognition(record_data)
            print("発話メッセージ:{}".format(speeched_text))

            # 終了ワードチェック
            if (speeched_text == "終了") or (speeched_text == "終了。") :
                answered_text = "わかりました。終了します。さようなら。"
                is_exit = True

            else :
                # 会話モジュールから、問いかけに対する応答を取得
                answered_text =  conv.GetAnswer(speeched_text)
                is_exit = False

            # 応答が空でなかったら再生する。
            if ( ( answered_text != None) and (answered_text != "" ) ) :
                print("応答メッセージ:{}".format(answered_text) )

                answered_text_list = answered_text.split('\n')
                for text_to_speech in answered_text_list :
                    if text_to_speech != "" :
                        filename = voice.TextToSpeech(text_to_speech)
                        if (len(filename) != 0) :
                            voice.PlayAudioFile(filename)

            # 終了ワードでループから抜ける
            if (is_exit == True ) :
                tmr.Stop()
                print("Exit!!!")
                break


    # 底面 LED をオフに
    global_led_Ill.AllOff()

if __name__ == "__main__":
    main()

