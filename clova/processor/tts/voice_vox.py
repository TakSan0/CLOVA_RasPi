from clova.processor.tts.base_tts import BaseTTSProvider
import os
import requests
import json
import time
from clova.general.logger import BaseLogger
from clova.config.config import global_config_prov


class VoiceVoxTTSProvider(BaseTTSProvider, BaseLogger):
    def __init__(self):
        super().__init__()

        self.web_voicevox_api_key = os.environ["WEB_VOICEVOX_API_KEY"]
        self.voicevox_custom_api_endpoint = os.environ["VOICEVOX_CUSTOM_API_ENDPOINT"]

    def __del__(self):
        super().__del__()

    def tts(self, text, **kwargs):
        self.log("tts", "音声合成中(VoiceVox)")

        if self.voicevox_custom_api_endpoint != "":
            return self._tts_engine(text, **kwargs)

        # 音声合成設定
        url = "https://api.tts.quest/v3/voicevox/synthesis"
        params = {
            "key": self.web_voicevox_api_key,
            "speaker": kwargs["name"],
            "text": text,
        }

        try:
            # APIにリクエストを送信してデータを取得
            res = requests.post(url, data=params)

            # HTTPエラーがあれば例外を発生させる
            res.raise_for_status()
            res_json = json.loads(res.text)

            if global_config_prov.verbose():
                self.log("tts", "status = '{}'".format(res.status_code))
                self.log("tts", "content = '{}'".format(res.content))
                self.log("tts", "text = '{}'".format(res.text))

            if (res_json["success"]):

                while True:
                    if global_config_prov.verbose():
                        self.log("tts", "webDownloadUrl = '{}'".format(res_json["wavDownloadUrl"]))

                    response = requests.get(res_json["wavDownloadUrl"])

                    if (response.status_code == 200):
                        break

                    # 404エラーの場合はもう一度やり直す。
                    elif (response.status_code != 404):
                        # 404 以外のHTTPエラーがあれば例外を発生させる
                        response.raise_for_status()
                        break
                    # 少しだけ待ってリトライ
                    time.sleep(0.5)

                return response.content
            else:
                self.log("tts", "NOT success (VoiceVox")

        except requests.exceptions.RequestException as e:
            self.log("tts", res.text)
            self.log("tts", "リクエストエラー:{}".format(e))

        except IOError as e:
            # ここにはもう入ることがない？
            self.log("tts", res.text)
            self.log("tts", "ファイルの保存エラー:{}".format(e))

        return None

    def _tts_engine(self, text, **kwargs):
        self.log("_tts_engine", "_tts_engineに自動移管")

        # impl of https://github.com/VOICEVOX/voicevox_engine/blob/master/README.md
        try:
            phrase = requests.post(self.voicevox_custom_api_endpoint + "/audio_query", params={
                "speaker": kwargs["x_voice_vox_id"],
                "text": text
            })
            phrase.raise_for_status()

            res = requests.post(self.voicevox_custom_api_endpoint + "/synthesis", params={"speaker": kwargs["x_voice_vox_id"]}, data=phrase.content)
            res.raise_for_status()

            return res.content
        except Exception as e:
            self.log("_tts_engine", e)
            return None
