import speech_recognition
from clova.processor.stt.base_stt import BaseSTTProvider

GOOGLE_SPEECH_RATE = 16000

class GoogleCloudSpeechSTTProvider(BaseSTTProvider):
    def __init__(self):
        pass
    
    def stt(self, audio, **kwargs):
        print("音声からテキストに変換中(Speech Recognition)")

        # 録音した音声データをGoogle Speech Recognitionでテキストに変換する
        recognizer = speech_recognition.Recognizer()
        audio_data = speech_recognition.AudioData(audio, sample_rate=GOOGLE_SPEECH_RATE, sample_width=2)

        try:
            result = recognizer.recognize_google(audio_data, language=kwargs["language"])
        except Exception:
            return None

        return result
