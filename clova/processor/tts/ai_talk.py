from clova.processor.tts.base_tts import BaseTTSProvider
import os
import requests
from clova.general.logger import BaseLogger


class AITalkTTSProvider(BaseTTSProvider, BaseLogger):
    def __init__(self):
        super().__init__()

        self.aitalk_user = os.environ["AITALK_USER"]
        self.aitalk_password = os.environ["AITALK_PASSWORD"]

    def __del__(self):
        super().__del__()

    def tts(self, text, **kwargs):
        self.log("tts", "音声合成中(AITalk)")

        # 音声合成設定
        url = "https://webapi.aitalk.jp/webapi/v5/ttsget.php"
        params = {
            "username": self.aitalk_user,
            "password": self.aitalk_password,
            "speaker_name": kwargs["name"],
            "ext": "wav",
            "speed": kwargs["speed"],
            "pitch": kwargs["pitch"],
            "text": text
        }

        try:
            # APIにリクエストを送信してデータを取得
            response = requests.get(url, data=params)

            self.log("tts", "URL:{} params:{}".format(url, params))

            # HTTPエラーがあれば例外を発生させる
            response.raise_for_status()

            return response.content

        except requests.exceptions.RequestException as e:
            self.log("tts", "リクエストエラー:{}".format(e))

        except IOError as e:
            self.log("tts", "ファイルの保存エラー:{}".format(e))

        return None
