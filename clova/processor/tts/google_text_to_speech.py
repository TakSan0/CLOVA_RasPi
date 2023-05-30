from google.cloud import texttospeech as tts

from clova.processor.tts.base_tts import BaseTTSProvider

from clova.general.logger import BaseLogger


class GoogleTextToSpeechTTSProvider(BaseTTSProvider, BaseLogger):
    GOOGLE_SPEECH_RATE = 16000

    GENDER_MAP = {
        "MALE": tts.SsmlVoiceGender.MALE,
        "FEMALE": tts.SsmlVoiceGender.FEMALE,
        "NEUTRAL": tts.SsmlVoiceGender.NEUTRAL
    }

    def __init__(self):
        super().__init__()

        self._client_tts = tts.TextToSpeechClient()

    def __del__(self):
        super().__del__()

    def tts(self, text, **kwargs):
        self.log("tts", "音声合成中(Google TTS)")

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
            audio_encoding=tts.AudioEncoding.LINEAR16, speaking_rate=rate_cfg, pitch=pitch_cfg, sample_rate_hertz=self.GOOGLE_SPEECH_RATE
        )

        # 音声合成メイン処理実行
        response = self._client_tts.synthesize_speech(
            input=synthesis_input, voice=voice_config, audio_config=audio_config
        )

        return response.audio_content
