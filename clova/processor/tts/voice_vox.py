from clova.processor.tts.base_tts import BaseTTSProvider
import os
import requests
import json
import time

class VoiceVoxTTSProvider(BaseTTSProvider):
    def __init__(self):
        self.web_voicevox_api_key = os.environ["WEB_VOICEVOX_API_KEY"]
        self.voicevox_custom_api_endpoint = os.environ["VOICEVOX_CUSTOM_API_ENDPOINT"]
    
    def tts(self, text, **kwargs):
        print("音声合成中(VoiceVox)")

        if self.voicevox_custom_api_endpoint != "":
            return self._tts_engine(text, **kwargs)

        # 音声合成設定
        url = "https://api.tts.quest/v3/voicevox/synthesis"
        params = {
            "key": self.web_voicevox_api_key,
            "speaker": kwargs["name"],
            "text": text,
        }
        ret = None

        try:
            # APIにリクエストを送信してデータを取得
            res = requests.post(url, data=params)

            # HTTPエラーがあれば例外を発生させる
            res.raise_for_status()
            res_json = json.loads(res.text)

            # print("status = '{}'".format(response.status_code))
            # print("content = '{}'".format(response.content))
            # print("text = '{}'".format(response.text))
            if (res_json["success"] == True) :

                while True:
                    # print("webDownloadUrl = '{}'".format(res_json["wavDownloadUrl"]))
                    response = requests.get(res_json["wavDownloadUrl"])

                    if (response.status_code == 200) :
                        break

                    # 404エラーの場合はもう一度やり直す。
                    elif (response.status_code != 404) :
                        # 404 以外のHTTPエラーがあれば例外を発生させる
                        response.raise_for_status()
                        break
                    # 少しだけ待ってリトライ
                    time.sleep(0.5)

                return response.content
            else :
                print("NOT success (VoiceVox")

        except requests.exceptions.RequestException as e:
            print(res.text)
            print("リクエストエラー:{}".format(e))

        except IOError as e:
            print(res.text)
            print("ファイルの保存エラー:{}".format(e))

        print("ファイル保存完了:{}".format(self.WAV_PLAY_FILENAME))

        return ret

    def _tts_engine(self, text, **kwargs):
        # impl of https://github.com/VOICEVOX/voicevox_engine/blob/master/README.md
        try:
            phrase = requests.post(self.voicevox_custom_api_endpoint + "/audio_query", params={
                "speaker": kwargs["x_voice_vox_id"],
                "text": text
            })
            phrase.raise_for_status()

            res = requests.post(self.voicevox_custom_api_endpoint + "/synthesis", params={ "speaker": kwargs["x_voice_vox_id"] }, data=phrase.content)
            res.raise_for_status()

            return res.content
        except Exception as e:
            print(e)
            return None
