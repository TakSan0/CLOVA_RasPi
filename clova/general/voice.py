import time
import pyaudio
import threading
import numpy as np
import audioop
import ffmpeg

from typing import Dict, Type

from clova.io.local.led import global_led_Ill
from clova.config.config import global_config_prov
from clova.config.character import global_character_prov
from clova.io.local.volume import global_vol
from clova.general.queue import global_speech_queue

from clova.general.logger import BaseLogger

from clova.processor.stt.base_stt import BaseSTTProvider
from clova.processor.stt.google_cloud_speech import GoogleCloudSpeechSTTProvider
from clova.processor.stt.speech_recognition_google import SpeechRecognitionGoogleSTTProvider

from clova.processor.tts.base_tts import BaseTTSProvider
from clova.processor.tts.google_text_to_speech import GoogleTextToSpeechTTSProvider
from clova.processor.tts.voice_text import VoiceTextTTSProvider
from clova.processor.tts.voice_vox import VoiceVoxTTSProvider
from clova.processor.tts.ai_talk import AITalkTTSProvider

# 音声ファイル設定
SPEECH_FORMAT = pyaudio.paInt16

# 再生設定
PCM_PLAY_SIZEOF_CHUNK = 512

# 録音設定
GOOGLE_SPEECH_RATE = 16000
GOOGLE_SPEECH_SIZEOF_CHUNK = int(GOOGLE_SPEECH_RATE / 10)

# ==================================
#        音声取得・再生クラス
# ==================================


class VoiceController(BaseLogger):
    STT_MODULES: Dict[str, Type[BaseSTTProvider]] = {
        "GoogleCloudSpeech": GoogleCloudSpeechSTTProvider,
        "SpeechRecognitionGoogle": SpeechRecognitionGoogleSTTProvider
    }
    TTS_MODULES: Dict[str, Type[BaseTTSProvider]] = {
        "GoogleTextToSpeech": GoogleTextToSpeechTTSProvider,
        "VoiceText": VoiceTextTTSProvider,
        "VoiceVox": VoiceVoxTTSProvider,
        "AITalk": AITalkTTSProvider
    }

    # コンストラクタ
    def __init__(self):
        super().__init__()

        # 設定パラメータを読み込み
        conf = global_config_prov.get_general_config()
        self.mic_num_ch = conf["hardware"]["audio"]["microphone"]["num_ch"]
        self.mic_device_index = conf["hardware"]["audio"]["microphone"]["index"]
        self.silent_threshold = conf["hardware"]["audio"]["microphone"]["silent_thresh"]
        self.terminate_silent_duration = conf["hardware"]["audio"]["microphone"]["term_duration"]
        self.speaker_num_ch = conf["hardware"]["audio"]["speaker"]["num_ch"]
        self.speaker_device_index = conf["hardware"]["audio"]["speaker"]["index"]
        self.log("CTOR", "MiC:NumCh={}, Index={}, Threshold={}, Duration={}, SPK:NumCh={}, Index={}".format(self.mic_num_ch, self.mic_device_index,
                 self.silent_threshold, self.terminate_silent_duration, self.speaker_num_ch, self.speaker_device_index))  # for debug

        global_character_prov.bind_for_update(self._update_system_conf)

        self._update_system_conf()

        self._wav_conversion_ffmpeg_waiting = None

    # デストラクタ
    def __del__(self):
        super().__del__()

    def _update_system_conf(self):
        self.log("_update_system_conf", "called")
        self.tts_system = global_config_prov.get_general_config()["apis"]["tts"]["system"] or global_character_prov.get_character_settings()["tts"]["system"]
        self.stt_system = global_config_prov.get_general_config()["apis"]["stt"]["system"]

        self.tts_kwargs = global_config_prov.get_general_config()["apis"]["tts"]["params"] or global_character_prov.get_character_settings()["tts"]["params"]
        self.stt_kwargs = global_config_prov.get_general_config()["apis"]["stt"]["params"]

        self.tts = self.TTS_MODULES[self.tts_system]()
        self.stt = self.STT_MODULES[self.stt_system]()

    # マイクからの録音
    def microphone_record(self):
        # 底面 LED を赤に
        global_led_Ill.set_all(global_led_Ill.RGB_RED)

        # PyAudioのオブジェクトを作成
        pyaud = pyaudio.PyAudio()

        # 録音開始
        self.log("microphone_record", "聞き取り中：")

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
        max_silent_frames = int(self.terminate_silent_duration * GOOGLE_SPEECH_RATE / 1000 / GOOGLE_SPEECH_SIZEOF_CHUNK)  # 最大無音フレームカウンタ

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
                if (recording) and (silent_frames >= max_silent_frames):
                    self.log("microphone_record", "録音終了 / Rec level: {0}～{1}".format(maxpp_data_min, maxpp_data_max))
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
                    self.log("microphone_record", "録音開始")
                    recording = True

                # 録音中のフレームを取得
                rec_frames.append(data)

            # 割り込み音声がある時はキャンセルして抜ける
            if (len(global_speech_queue) != 0):
                self.log("microphone_record", "割り込み音声により録音キャンセル")
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
    def speech_to_text(self, audio):
        # 底面 LED をオレンジに
        global_led_Ill.set_all(global_led_Ill.RGB_ORANGE)

        if len(audio) == 0:
            return None

        return self.stt.stt(audio, **self.stt_kwargs)

    # テキストから音声に変換

    def text_to_speech(self, text):
        # 底面 LED を青に
        global_led_Ill.set_all(global_led_Ill.RGB_BLUE)

        return self.tts.tts(text, **self.tts_kwargs)

    def _get_wav_info(self, wav_bytes):
        # Read the required fields from the header
        channels = int.from_bytes(wav_bytes[22:24], 'little')
        sample_rate = int.from_bytes(wav_bytes[24:28], 'little')
        width = int.from_bytes(wav_bytes[34:36], 'little')

        return channels, sample_rate, width

    def _launch_ffmpeg_cache(self):
        input_stream = ffmpeg.input("pipe:", format="wav")
        output_stream = ffmpeg.output(
            input_stream.audio,
            "pipe:",
            format="s16le",
            ar=44100,
            ac=1,
            # loglevel='error'
        )

        self._wav_conversion_ffmpeg_waiting = output_stream.run_async(pipe_stdin=True, pipe_stdout=True)
        return self._wav_conversion_ffmpeg_waiting

    def _handle_ffmpeg_output(self, pyaud, channels, stdout):
        # 再生開始
        play_stream = None

        # 再生処理
        while True:
            data = stdout.read(PCM_PLAY_SIZEOF_CHUNK)
            if not data:
                break

            if play_stream is None:  # openしたときからwriteするまで結構大きめのノイズがするためデータが取得できてからopenする
                play_stream = pyaud.open(format=SPEECH_FORMAT, channels=channels, rate=44100, output=True, output_device_index=self.speaker_device_index)
                play_stream.start_stream()

            data = np.frombuffer(data, dtype=np.int16) * global_vol.vol_value  # ボリューム倍率を更新
            data = data.astype(np.int16)
            play_stream.write(data.tobytes())

        # 再生終了処理
        play_stream.stop_stream()
        while play_stream.is_active():
            time.sleep(0.1)
        play_stream.close()
        self.log("_handle_ffmpeg_output", "Play done!")

    # 音声ファイルの再生
    def play_audio(self, audio):
        # 底面 LED を水に
        global_led_Ill.set_all(global_led_Ill.RGB_CYAN)

        # with open("./test.wav", "wb") as f:
        #     f.write(audio)

        channels, _, _ = self._get_wav_info(audio)

        self.log("play_audio", "オーディオ再生 ({}チャンネル)".format(channels))

        if channels != 1:
            # 変換
            input_stream = ffmpeg.input("pipe:", format="wav")
            output_stream = ffmpeg.output(
                input_stream.audio,
                "pipe:",
                format="s16le",
                ar=44100,
                ac=channels,
                # loglevel='error'
            )

            ffmpeg_proc = output_stream.run_async(pipe_stdin=True, pipe_stdout=True)
        else:
            ffmpeg_proc = self._wav_conversion_ffmpeg_waiting or self._launch_ffmpeg_cache()
            self._wav_conversion_ffmpeg_waiting = None

        # PyAudioのオブジェクトを作成
        pyaud = pyaudio.PyAudio()

        ffmpeg_handler = threading.Thread(target=self._handle_ffmpeg_output, args=[pyaud, channels, ffmpeg_proc.stdout])
        ffmpeg_handler.start()

        ffmpeg_proc.stdin.write(audio)
        ffmpeg_proc.stdin.close()

        ffmpeg_handler.join()
        pyaud.terminate()

        threading.Thread(target=self._launch_ffmpeg_cache).start()  # 次回から待機状態のffmpegを使用する

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
    module_test()
