from google.cloud import speech_v1p1beta1 as speech
from clova.processor.stt.base_stt import BaseSTTProvider


class GoogleCloudSpeechSTTProvider(BaseSTTProvider):
    GOOGLE_SPEECH_RATE = 16000

    def __init__(self):
        self._client_speech = speech.SpeechClient()
    
    def stt(self, audio, **kwargs):
        print("音声からテキストに変換中(Google Cloud Speech)")

        # Speech-to-Text の認識設定
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.GOOGLE_SPEECH_RATE,
            language_code=kwargs["language"],
            enable_automatic_punctuation=True,
        )

        # Speech-to-Text の音声設定
        speech_audio = speech.RecognitionAudio(content=audio)

        # Speech-to-Text の認識処理
        speech_response = self._client_speech.recognize(config=config, audio=speech_audio)

        # 結果取得処理 (JSONから抜き出す)
        # print(len(speech_response.results)) # デバッグ用
        if (len(speech_response.results) != 0) :
            result = speech_response.results[0].alternatives[0].transcript.strip()
        else :
            print("音声取得に失敗")
            result = None

        return result
