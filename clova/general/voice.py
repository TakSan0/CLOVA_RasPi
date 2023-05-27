import time
import os
import pyaudio
import wave
import numpy as np
import audioop
from pydub import AudioSegment
from clova.io.local.led import global_led_Ill
from clova.config.config import global_config_prov
from clova.config.character import global_character_prov
from clova.io.local.volume import global_vol
from clova.general.queue import global_speech_queue

from typing import Dict, Type

from clova.processor.stt.base_stt import BaseSTTProvider
from clova.processor.stt.google_cloud_speech import GoogleCloudSpeechSTTProvider
from clova.processor.stt.speech_recognition_google import GoogleCloudSpeechSTTProvider

from clova.processor.tts.base_tts import BaseTTSProvider
from clova.processor.tts.google_text_to_speech import GoogleTextToSpeechTTSProvider
from clova.processor.tts.voice_text import VoiceTextTTSProvider
from clova.processor.tts.voice_vox import VoiceVoxTTSProvider
from clova.processor.tts.ai_talk import AITalkTTSProvider

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
class VoiceController :
    STT_MODULES: Dict[str, Type[BaseSTTProvider]] = {
        "GoogleCloudSpeech": GoogleCloudSpeechSTTProvider,
        "SpeechRecognitionGoogle": GoogleCloudSpeechSTTProvider
    }
    TTS_MODULES: Dict[str, Type[BaseTTSProvider]] = {
        "GoogleTextToSpeech": GoogleTextToSpeechTTSProvider,
        "VoiceText": VoiceTextTTSProvider,
        "VoiceVox": VoiceVoxTTSProvider,
        "AITalk": AITalkTTSProvider
    }

    # コンストラクタ
    def __init__(self) :
        print("Create <VoiceControl> class")

        # 設定パラメータを読み込み
        conf = global_config_prov.get_general_config()
        self.mic_num_ch = conf["hardware"]["audio"]["microphone"]["num_ch"]
        self.mic_device_index = conf["hardware"]["audio"]["microphone"]["index"]
        self.silent_threshold = conf["hardware"]["audio"]["microphone"]["silent_thresh"]
        self.terminate_silent_duration = conf["hardware"]["audio"]["microphone"]["term_duration"]
        self.speaker_num_ch = conf["hardware"]["audio"]["speaker"]["num_ch"]
        self.speaker_device_index = conf["hardware"]["audio"]["speaker"]["index"]
        print("MiC:NumCh={}, Index={}, Threshold={}, Duration={}, SPK:NumCh={}, Index={}".format(self.mic_num_ch, self.mic_device_index,  self.silent_threshold, self.terminate_silent_duration, self.speaker_num_ch, self.speaker_device_index))#for debug

        self.tts_system = global_config_prov.get_general_config()["apis"]["tts"]["system"] or global_character_prov.get_character_settings()["tts"]["system"]
        self.stt_system = global_config_prov.get_general_config()["apis"]["stt"]["system"]

        self.tts_kwargs = global_config_prov.get_general_config()["apis"]["tts"]["params"] or global_character_prov.get_character_settings()["tts"]["params"]
        self.stt_kwargs = global_config_prov.get_general_config()["apis"]["stt"]["params"]

        self.tts = self.TTS_MODULES[self.tts_system]()
        self.stt = self.STT_MODULES[self.stt_system]()

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <VoiceControl> class")

    # マイクからの録音
    def microphone_record(self) :
        # 底面 LED を赤に
        global_led_Ill.set_all(global_led_Ill.RGB_RED)

        # PyAudioのオブジェクトを作成
        pyaud = pyaudio.PyAudio()

        # 録音開始
        print("聞き取り中：")

        # 底面 LED を暗緑に
        global_led_Ill.set_all(global_led_Ill.RGB_DARKGREEN)

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

            # 無音しきい値未満
            if maxpp_data < self.silent_threshold:
                # 無音期間 フレームカウンタをインクリメント
                silent_frames += 1

                # 開始済みの場合で、フレームカウンタが最大に達したら、会話の切れ目と認識して終了する処理
                if ( recording == True ) and ( silent_frames >= max_silent_frames ):
                    print("録音終了 / Rec level;{0}～{1}".format(maxpp_data_min, maxpp_data_max))
                    # 録音停止
                    break

            # 無音しきい値以上
            else:
                # 音の入力があったので、無音期間フレームカウンタをクリア
                silent_frames = 0

                # まだ開始できていなかったら、ここから録音開始
                if not recording:
                    # 底面 LED を緑に
                    global_led_Ill.set_all(global_led_Ill.RGB_GREEN)

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
                break

        # 録音停止
        rec_stream.stop_stream()
        rec_stream.close()

        # PyAudioオブジェクトを終了
        pyaud.terminate()

        return b"".join(rec_frames)

    # 音声からテキストに変換
    def speech_to_text(self, audio) :
        # 底面 LED をオレンジに
        global_led_Ill.set_all(global_led_Ill.RGB_ORANGE)

        return self.stt.stt(audio, **self.stt_kwargs)


    # テキストから音声に変換
    def text_to_speech(self, text) :
        # 底面 LED を青に
        global_led_Ill.set_all(global_led_Ill.RGB_BLUE)

        return self.tts.tts(text, **self.tts_kwargs)

    # 音声ファイルの再生
    # TODO: pipe stdin to prevent from damaging sd card
    def play_audio_file(self, filename) :
        # 底面 LED を水に
        global_led_Ill.set_all(global_led_Ill.RGB_CYAN)
        print("ファイル再生 :{}".format(filename))

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
            converted_wav.export(filename, format="wav")
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

# ==================================
#       本クラスのテスト用処理
# ==================================
def module_test() :
    # 現状何もしない
    pass

# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    module_test()

