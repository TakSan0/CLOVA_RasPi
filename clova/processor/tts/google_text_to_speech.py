from clova.processor.tts.base_tts import BaseTTSProvider
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech as tts

class GoogleTextToSpeechTTSProvider(BaseTTSProvider):
    GOOGLE_SPEECH_RATE = 16000
    WAV_PLAY_FILENAME = "/tmp/clova_speech.wav"

    GENDER_MAP = {
        "MALE": tts.SsmlVoiceGender.MALE,
        "FEMALE": tts.SsmlVoiceGender.FEMALE,
        "NEUTRAL": tts.SsmlVoiceGender.NEUTRAL
    }

    def __init__(self):
        self._client_tts = tts.TextToSpeechClient()
    
    def tts(self, text, **kwargs):
        print("音声合成中(Google TTS)")

        # テキスト入力
        synthesis_input = tts.SynthesisInput(text=text)

        # パラメータを読み込み
        gender = self.GENDER_MAP[kwargs["gender"]] or tts.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED
        pitch_cfg = float(kwargs["pitch"])
        rate_cfg = float(kwargs["rate"])


        # 音声合成設定
        voice_config = tts.VoiceSelectionParams(
            language_code=kwargs["language"],
            ssml_gender=gender,
            name=kwargs["name"]
        )

        # 音声ファイル形式設定
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.LINEAR16, speaking_rate=rate_cfg, pitch = pitch_cfg, sample_rate_hertz = self.GOOGLE_SPEECH_RATE
        )

        # 音声合成メイン処理実行
        response = self._client_tts.synthesize_speech(
            input=synthesis_input, voice=voice_config, audio_config=audio_config
        )

        # 音声をファイルに保存
        with open(self.WAV_PLAY_FILENAME, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print("ファイル保存完了 ;{}".format(self.WAV_PLAY_FILENAME))
        
        return self.WAV_PLAY_FILENAME