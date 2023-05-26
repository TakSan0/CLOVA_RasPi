from clova.config.config import global_config_prov
# from CLOVA_config import HttpReqSettingHandler
from clova.io.local.led import global_led_Ill
from clova.processor.skill.timer import TimerSkillProvider
from clova.io.local.switch import SwitchInput
from clova.io.local.volume import global_vol
from clova.config.character import global_character_prov
from clova.general.conversation import ConversationController
from clova.general.voice import VoiceController
from clova.io.http.http_server import HttpServer
from clova.processor.skill.line import LineSkillProvider, HttpReqLineHandler

def main() :
    # 会話モジュールのインスタンス作成
    conv = ConversationController()

    # HTTPサーバー系のインスタンス作成
    line_svr = HttpServer(8080, HttpReqLineHandler)
    # config_svr = HttpServer(8000, HttpReqSettingHandler)

    # LINE送信モジュールのインスタンス
    line_sender = LineSkillProvider()

    # 底面 LED を黄色に
    global_led_Ill.set_all_yellow()

    # LEDを使うモジュールにインスタンスをコピー
    voice = VoiceController()

    # キー準備
    char_swich = SwitchInput(SwitchInput.PIN_BACK_SW_BT, global_character_prov.select_next_character)
    plus_swich = SwitchInput(SwitchInput.PIN_BACK_SW_PLUS, global_vol.vol_up_cb)
    minus_swich = SwitchInput(SwitchInput.PIN_BACK_SW_MINUS, global_vol.vol_down_cb)

    # タイマ準備
    tmr = TimerSkillProvider()
    conv.tmr = tmr
    #tmr.Start()

    # メインループ
    while True :

        int_exists, stt_result = conv.check_for_interrupted_voice()

        # 割り込み音声ありの時
        if ( int_exists == True) :
            if stt_result != "" :
                filename = voice.text_2_speech(stt_result)
                if (filename != "") :
                    voice.play_audio_file(filename)
                else :
                    print("音声ファイルを取得できませんでした。")

        # 割り込み音声無の時
        else :
            answered_text = ""

            # 録音
            record_data = voice.microphone_record()

            # テキストに返還
            stt_result = voice.speech_2_text(record_data)

            if stt_result is None:
                print("発話なし")
                continue

            print("発話メッセージ:{}".format(stt_result))

            # 終了ワードチェック
            if (stt_result == "終了") or (stt_result == "終了。") :
                answered_text = "わかりました。終了します。さようなら。"
                is_exit = True

            else :
                # 会話モジュールから、問いかけに対する応答を取得
                answered_text =  conv.get_answer(stt_result)
                is_exit = False

            # 応答が空でなかったら再生する。
            if ( ( answered_text != None) and (answered_text != "" ) ) :
                print("応答メッセージ:{}".format(answered_text) )

                answered_text_list = answered_text.split("\n")
                for text_to_speech in answered_text_list :
                    if text_to_speech != "" :
                        filename = voice.text_2_speech(text_to_speech)
                        if (len(filename) != 0) :
                            voice.play_audio_file(filename)

            # 終了ワードでループから抜ける
            if (is_exit == True ) :
                tmr.stop()
                print("Exit!!!")
                break


    # 底面 LED をオフに
    global_led_Ill.set_all_off()

if __name__ == "__main__":
    main()

