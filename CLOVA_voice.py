import time
import os
import pyaudio
import wave
import numpy as np
import audioop
import speech_recognition as google_sr
import requests
import json
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech as tts
from voicetext import VoiceText
from pydub import AudioSegment
from CLOVA_led import global_led_Ill
from CLOVA_config import global_config_sys
from CLOVA_charactor import global_charactor
from CLOVA_volume import global_vol
from CLOVA_queue import global_speech_queue

# 音声ファイル設定
SPEECH_FORMAT = pyaudio.paInt16

# 再生設定
WAV_PLAY_FILENAME = "/tmp/clova_speech.wav"
WAV_PLAY_SIZEOF_CHUNK = 1024

# 録音設定
GOOGLE_SPEECH_RATE = 16000
GOOGLE_SPEECH_SIZEOF_CHUNK = int(GOOGLE_SPEECH_RATE / 10)

# ==================================
#        音声取得・再生クラス
# ==================================
class VoiceControl :
    # コンストラクタ
    def __init__(self) :
        print("Create <VoiceControl> class")

        # 設定パラメータを読み込み
        self.mic_num_ch = global_config_sys.settings["hardware"]["audio"]["microphone"]["num_ch"]
        self.mic_device_index = global_config_sys.settings["hardware"]["audio"]["microphone"]["index"]
        self.silent_threshold = global_config_sys.settings["hardware"]["audio"]["microphone"]["silent_thresh"]
        self.terminate_silent_duration = global_config_sys.settings["hardware"]["audio"]["microphone"]["term_duration"]
        self.speaker_num_ch = global_config_sys.settings["hardware"]["audio"]["speaker"]["num_ch"]
        self.speaker_device_index = global_config_sys.settings["hardware"]["audio"]["speaker"]["index"]
        print("MiC:NumCh={}, Index={}, Threshold={}, Duration={}, SPK:NumCh={}, Index={}".format(self.mic_num_ch, self.mic_device_index,  self.silent_threshold, self.terminate_silent_duration, self.speaker_num_ch, self.speaker_device_index))#for debug

        # Speech-to-Text API クライアントを作成する
        self._client_speech = speech.SpeechClient()

        # Text-to-Speech API クライアントを作成する
        self._client_tts = tts.TextToSpeechClient()

        # VoiceText のキーを取得
        self.voice_text_api_key = os.environ['VOICE_TEXT_API_KEY']
        # Web版Voice Vox API キーを取得
        self.web_voicevox_api_key = os.environ['WEB_VOICEVOX_API_KEY']
        # ALTalk ユーザー名パスワードを取得
        self.aitalk_user = os.environ['AITALK_USER']
        self.aitalk_password = os.environ['AITALK_PASSWORD']

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <VoiceControl> class")

    # マイクからの録音
    def RecordFromMic(self) :
        # 底面 LED を赤に
        global_led_Ill.AllRed()

        # PyAudioのオブジェクトを作成
        pyaud = pyaudio.PyAudio()

        # 録音開始
        print("聞き取り中：")

        # 底面 LED を暗緑に
        global_led_Ill.AllDarkGreen()

        # 録音準備
        rec_stream = pyaud.open(format=SPEECH_FORMAT,
                                channels=self.mic_num_ch,
                                rate=GOOGLE_SPEECH_RATE,
                                input=True,
                                input_device_index=self.mic_device_index,
                                frames_per_buffer=GOOGLE_SPEECH_SIZEOF_CHUNK)

        # 無音検出用パラメータ
        silent_frames = 0  # 無音期間 フレームカウンタ
        max_silent_frames = int( self.terminate_silent_duration * GOOGLE_SPEECH_RATE / 1000 / GOOGLE_SPEECH_SIZEOF_CHUNK)  # 最大無音フレームカウンタ

        # 最大最小の初期化
        maxpp_data_max = 0
        maxpp_data_min = 32767

        # 初回のボツッ音を発話開始と認識してしまうので、ダミーで最初１フレーム分読んでおく（応急処置）
        rec_stream.read(GOOGLE_SPEECH_SIZEOF_CHUNK)

        # 録音停止から始める
        recording = False

        # バッファ初期化
        rec_frames = []

        # 録音ループ
        while True:
            # データ取得
            data = rec_stream.read(GOOGLE_SPEECH_SIZEOF_CHUNK)

            # ピーク平均の算出
            maxpp_data = audioop.maxpp(data, 2)

            # 最大値、最小値の格納
            if maxpp_data < maxpp_data_min:
                maxpp_data_min = maxpp_data
            if maxpp_data > maxpp_data_max:
                maxpp_data_max = maxpp_data

            # 無音スレッショルド未満
            if maxpp_data < self.silent_threshold:
                # 無音期間 フレームカウンタをインクリメント
                silent_frames += 1

                # 開始済みの場合で、フレームカウンタが最大に達したら、会話の切れ目と認識して終了する処理
                if ( recording == True ) and ( silent_frames >= max_silent_frames ):
                    print("録音終了 / Rec level;{0}～{1}".format(maxpp_data_min, maxpp_data_max))
                    # 録音停止
                    break

            # 無音スレッショルド以上
            else:
                # 音の入力があったので、無音期間フレームカウンタをクリア
                silent_frames = 0

                # まだ開始できていなかったら、ここから録音開始
                if not recording:
                    # 底面 LED を緑に
                    global_led_Ill.AllGreen()

                    # 録音開始
                    print("録音開始")
                    recording = True

                # 録音中のフレームを取得
                rec_frames.append(data)

            # 割り込み音声がある時はキャンセルして抜ける
            if (len(global_speech_queue) != 0) :
                print("割り込み音声により録音キャンセル")
                # rec_frames = []
                rec_frames.append(data)
                break;

        # 録音停止
        rec_stream.stop_stream()
        rec_stream.close()

        # PyAudioオブジェクトを終了
        pyaud.terminate()

        return b"".join(rec_frames)

    # 音声からテキストに変換
    def SpeechToText(self, record_data) :
        # 底面 LED をオレンジに
        global_led_Ill.AllOrange()

        # 設定値により音声認識(STT)システムを選択する
        system = global_charactor.setting_json["charactors"][global_charactor.sel_num]["Listener"]["system"]
        if (system == "GoogleCloudSpeech") :
            speeched_text = self.SpeechToTextWithGoogleSpeech(record_data)
        elif (system == "GoogleSpeechRecognition") :
            speeched_text = self.SpeechToTextWithGoogleSpeechRecognition(record_data)
        else :
            print("Invalid Speech System for SpeechToText : {}".format(system))
            speeched_text = ""
        return speeched_text


    # テキストから音声に変換
    def TextToSpeech(self, text_to_speech) :
        # 底面 LED を青に
        global_led_Ill.AllBlue()

        # 設定値により音声合成(TTS)システムを選択する
        system = global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["system"]
        if (system == "GoogleTextToSpeech") :
            file_name = self.TextToSpeechWavWithGoogleSpeech(text_to_speech)
        elif (system == "VoiceText") :
            file_name = self.TextToSpeechWavWithVoiceText(text_to_speech)
        elif (system == "VoiceVox") :
            file_name = self.TextToSpeechWavWithVoiceVox(text_to_speech)
        elif (system == "AITalk") :
            file_name = self.TextToSpeechWavWithAITalk(text_to_speech)
        else :
            print("Invalid Speech System for TextToSpeech : {}".format(system))
            file_name = ""

        return file_name

    # 音声ファイルの再生
    def PlayAudioFile(self, filename) :
        # 底面 LED を水に
        global_led_Ill.AllCyan()
        print('ファイル再生 :{}'.format(filename))

        # PyAudioのオブジェクトを作成
        pyaud = pyaudio.PyAudio()

        # waveファイルの情報を取得
        wav_file = wave.open(filename, "rb")
        rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        width = wav_file.getsampwidth()

        if (rate == 24000) :
            # 一旦閉じる
            wav_file.close()
            os.rename(filename, "/tmp/temp.wav")

            # サンプリングレート変換
            rateconv_file = AudioSegment.from_wav("/tmp/temp.wav")
            converted_wav = rateconv_file.set_frame_rate(44100)
            converted_wav.export(filename, format='wav')
            os.remove("/tmp/temp.wav")

            # 再度フィアルを開いて waveファイルの情報を取得
            wav_file = wave.open(filename, "rb")
            rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            width = wav_file.getsampwidth()

        print("PlayWav: rate={}, channels={}, width = {}".format(rate,channels, width))

        # 再生開始
        play_stream = pyaud.open(format=pyaud.get_format_from_width(width), channels=channels, rate=rate, output=True, output_device_index=self.speaker_device_index)
        wav_file.rewind()
        play_stream.start_stream()

        # 再生処理
        while True:
            data = wav_file.readframes(WAV_PLAY_SIZEOF_CHUNK)
            if not data:
                break
            data = np.frombuffer(data, dtype=np.int16) * global_vol.vol_value # ボリューム倍率を更新
            data = data.astype(np.int16)
            play_stream.write(data.tobytes())

        # 再生終了処理
        play_stream.stop_stream()
        while play_stream.is_active():
            time.sleep(0.1)
        play_stream.close()
        wav_file.close()
        print("Play done!")

        # PyAudioオブジェクトを終了
        pyaud.terminate()
        time.sleep(0.1)

    # Google-Speech での音声テキスト変換
    def SpeechToTextWithGoogleSpeech(self, record_data) :
        print("音声からテキストに変換中(Google Speech)")

        # Speech-to-Text の認識設定
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=GOOGLE_SPEECH_RATE,
            language_code=global_charactor.setting_json["charactors"][global_charactor.sel_num]["Listener"]["language"],
            enable_automatic_punctuation=True,
        )

        # Speech-to-Text の音声設定
        speech_audio = speech.RecognitionAudio(content=record_data)

        # Speech-to-Text の認識処理
        speech_response = self._client_speech.recognize(config=config, audio=speech_audio)

        # 結果取得処理 (JSONから抜き出す)
        # print(len(speech_response.results)) # デバッグ用
        if (len(speech_response.results) != 0) :
            speeched_text = speech_response.results[0].alternatives[0].transcript.strip()
        else :
            print("音声取得に失敗")
            speeched_text = ""

        return speeched_text

    # Google-SpeechRecognition での音声テキスト変換
    def SpeechToTextWithGoogleSpeechRecognition(self, record_data) :
        print("音声からテキストに変換中(Google Recognition)")

        speeched_text = ""

        # 録音した音声データをGoogle Speech Recognitionでテキストに変換する
        recognizer = google_sr.Recognizer()
        audio_data = google_sr.AudioData(record_data, sample_rate=GOOGLE_SPEECH_RATE, sample_width=2)

        speeched_text = recognizer.recognize_google(audio_data, language=global_charactor.setting_json["charactors"][global_charactor.sel_num]["Listener"]["language"])

        return speeched_text

    # Google-Speech でのテキスト音声変換
    def TextToSpeechWavWithGoogleSpeech(self, speeched_text) :
        print("音声合成中(Google TTS)")

        # テキスト入力
        synthesis_input = tts.SynthesisInput(text=speeched_text)

        # パラメータを読み込み
        if ( global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["gender"] == "MALE" ) :
            gender_sel = tts.SsmlVoiceGender.MALE
        elif ( global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["gender"] == "FEMALE" ) :
            gender_sel = tts.SsmlVoiceGender.FEMALE
        elif ( global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["gender"] == "NEUTRAL" ) :
            gender_sel = tts.SsmlVoiceGender.NEUTRAL
        else :
            gender_sel = tts.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED
        pitch_cfg = float(global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["pitch"])
        rate_cfg = float(global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["rate"])


        # 音声合成設定
        voice_config = tts.VoiceSelectionParams(
            language_code=global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["language"],
            ssml_gender=gender_sel,
            name=global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["name"]
        )

        # 音声ファイル形式設定
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.LINEAR16, speaking_rate=rate_cfg, pitch = pitch_cfg, sample_rate_hertz = GOOGLE_SPEECH_RATE
        )

        # 音声合成メイン処理実行
        response = self._client_tts.synthesize_speech(
            input=synthesis_input, voice=voice_config, audio_config=audio_config
        )

        # 音声をファイルに保存
        with open(WAV_PLAY_FILENAME, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print('ファイル保存完了 ;{}'.format(WAV_PLAY_FILENAME))
        
        return WAV_PLAY_FILENAME

    # VoiceText WebAPI でのテキスト音声変換
    def TextToSpeechWavWithVoiceText(self, speeched_text) :
        print("音声合成中(VoiceText)")

        # 音声合成設定
        url = "https://api.voicetext.jp/v1/tts"
        params = {
            "text": speeched_text,
            "speaker": global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["name"],
            "emotion": global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["emotion"]
        }
        auth = (self.voice_text_api_key, '')
        ret = ""

        try:
            # APIにリクエストを送信してデータを取得
            response = requests.post(url, auth=auth, data=params)

            # HTTPエラーがあれば例外を発生させる
            response.raise_for_status()            

            # 音声をファイルに保存
            with open(WAV_PLAY_FILENAME, "wb") as out:
                out.write(response.content)

            ret = WAV_PLAY_FILENAME

        except requests.exceptions.RequestException as e:
            print("リクエストエラー:{}".format(e))

        except IOError as e:
            print("ファイルの保存エラー:{}".format(e))

        print('ファイル保存完了 ;{}'.format(WAV_PLAY_FILENAME))

        return ret

    # VoiceVox WebAPI でのテキスト音声変換
    def TextToSpeechWavWithVoiceVox(self, speeched_text) :
        print("音声合成中(VoiceVox)")

        # 音声合成設定
        url = "https://api.tts.quest/v3/voicevox/synthesis"
        params = {
            "key": self.web_voicevox_api_key,
            "speaker": global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["name"],
            "text": speeched_text,
        }
        auth = (self.voice_text_api_key, '')
        ret = ""

        try:
            # APIにリクエストを送信してデータを取得
            res = requests.post(url, data=params)

            # HTTPエラーがあれば例外を発生させる
            res.raise_for_status()
            res_json = json.loads(res.text)

            # print("status = '{}'".format(response.status_code))
            # print("content = '{}'".format(response.content))
            # print("text = '{}'".format(response.text))
            if (res_json["success"] == True) :

                while True:
                    # print("webDownloadUrl = '{}'".format(res_json["wavDownloadUrl"]))
                    response = requests.get(res_json["wavDownloadUrl"])

                    if (response.status_code == 200) :
                        break

                    # 404エラーの場合はもう一度やり直す。
                    elif (response.status_code != 404) :
                        # 404 以外のHTTPエラーがあれば例外を発生させる
                        response.raise_for_status()
                        break
                    # 少しだけ待ってリトライ
                    time.sleep(0.5)

                # 音声をファイルに保存
                with open(WAV_PLAY_FILENAME, "wb") as out:
                    out.write(response.content)

                ret = WAV_PLAY_FILENAME
            else :
                print("NOT success (VoiceVox")

        except requests.exceptions.RequestException as e:
            print(res.text)
            print("リクエストエラー:{}".format(e))

        except IOError as e:
            print(res.text)
            print("ファイルの保存エラー:{}".format(e))

        print('ファイル保存完了 ;{}'.format(WAV_PLAY_FILENAME))

        return ret

    # AITalk WebAPI でのテキスト音声変換
    def TextToSpeechWavWithAITalk(self, speeched_text) :
        print("音声合成中(AITalk)")

        # 音声合成設定
        url = "https://webapi.aitalk.jp/webapi/v5/ttsget.php"
        params = {
            "username": self.aitalk_user,
            "password": self.aitalk_password,
            "speaker_name": global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["name"],
            "ext": "wav",
            "speed": global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["speed"],
            "pitch": global_charactor.setting_json["charactors"][global_charactor.sel_num]["Speaker"]["pitch"],
            "text": speeched_text
        }
        ret = ""

        try:
            # APIにリクエストを送信してデータを取得
            response = requests.get(url, data=params)

            print("URL:{} params:{}".format(url, params))

            # HTTPエラーがあれば例外を発生させる
            response.raise_for_status()            

            # 音声をファイルに保存
            with open(WAV_PLAY_FILENAME, "wb") as out:
                out.write(response.content)

            ret = WAV_PLAY_FILENAME

        except requests.exceptions.RequestException as e:
            print("リクエストエラー:{}".format(e))

        except IOError as e:
            print("ファイルの保存エラー:{}".format(e))

        print('ファイル保存完了 ;{}'.format(WAV_PLAY_FILENAME))

        return ret

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
    ModuleTest()

