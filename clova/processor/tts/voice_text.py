from clova.processor.tts.base_tts import BaseTTSProvider
import os
import requests

class VoiceTextTTSProvider(BaseTTSProvider):
    WAV_PLAY_FILENAME = "/tmp/clova_speech.wav"

    def __init__(self):
        self.voice_text_api_key = os.environ["VOICE_TEXT_API_KEY"]
    
    def tts(self, text, **kwargs):
        print("音声合成中(VoiceText)")

        # 音声合成設定
        url = "https://api.voicetext.jp/v1/tts"
        params = {
            "text": text,
            "speaker": kwargs["name"],
            "emotion": kwargs["emotion"]
        }
        auth = (self.voice_text_api_key, "")
        ret = None

        try:
            # APIにリクエストを送信してデータを取得
            response = requests.post(url, auth=auth, data=params)

            # HTTPエラーがあれば例外を発生させる
            response.raise_for_status()            

            # 音声をファイルに保存
            with open(self.WAV_PLAY_FILENAME, "wb") as out:
                out.write(response.content)

            ret = self.WAV_PLAY_FILENAME

        except requests.exceptions.RequestException as e:
            print("リクエストエラー:{}".format(e))

        except IOError as e:
            print("ファイルの保存エラー:{}".format(e))

        print("ファイル保存完了 ;{}".format(self.WAV_PLAY_FILENAME))

        return ret
