from clova.processor.tts.base_tts import BaseTTSProvider
import os
import requests


class VoiceTextTTSProvider(BaseTTSProvider):
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

        try:
            # APIにリクエストを送信してデータを取得
            response = requests.post(url, auth=auth, data=params)

            # HTTPエラーがあれば例外を発生させる
            response.raise_for_status()

            return response.content

        except requests.exceptions.RequestException as e:
            print("リクエストエラー:{}".format(e))

        except IOError as e:
            print("ファイルの保存エラー:{}".format(e))

        return None
