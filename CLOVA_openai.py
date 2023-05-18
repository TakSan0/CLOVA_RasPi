import time
import os
import openai
from CLOVA_led import global_led_Ill
from CLOVA_charactor import global_charactor

# ==================================
#         OpenAI APIクラス
# ==================================
class OpenaiApiControl :
    OPENAI_CHARACTOR_CFG = "あなたはサービス終了で使えなくなったクローバの後を次ぎました。"

    # コンストラクタ
    def __init__(self) :
        self.OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
        self.SetCharctorSetting("")
        print("Create <OpenaiApiControl> class")

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <OpenaiApiControl> class")

    def SetCharctorSetting(self, setting_str) :
        self._char_setting_str = self.OPENAI_CHARACTOR_CFG + setting_str

    def GetAnswerFromAi(self, aimodel, speeched_text) :
        openai.api_key = self.OPENAI_API_KEY

        # 底面 LED をピンクに
        global_led_Ill.AllPink()
        print("OpenAI 応答作成中")
        desc = global_charactor.GetCharactorDescription()

        if (self.OPENAI_API_KEY != "") :
            try:

                ai_response = openai.ChatCompletion.create(
                    model=aimodel,
                    messages=[
                        {"role": "system", "content":  self._char_setting_str + desc },
                        {"role": "user", "content": speeched_text},
                    ]
                )
                #print(ai_response["choices"][0]["message"]["content"]) #返信のみを出力
                print(ai_response)

                #print(len(ai_response))
                if (len(ai_response) != 0) :
                    answer_text = ai_response["choices"][0]["message"]["content"]
                else :
                    print("AIからの応答が空でした。")
                    answer_text = ""

            except openai.error.RateLimitError:
                answer_text = "OpenAIエラー：APIクオータ制限に達しました。しばらく待ってから再度お試しください。改善しない場合は、月間使用リミットに到達したか無料枠期限切れの可能性もあります。"
            except openai.error.AuthenticationError:
                answer_text = "OpenAIエラー：Open AI APIキーが不正です。"
            except openai.error.APIConnectionError:
                answer_text = "OpenAIエラー：Open AI APIに接続できませんでした。"
            except openai.error.ServiceUnavailableError:
                answer_text = "OpenAIエラー：Open AI サービス無効エラーです。"
            except openai.error.OpenAIError as e:
                answer_text = "OpenAIエラー：Open AI APIエラーが発生しました： {}".format(e)
            except Exception as e:
                answer_text = "不明なエラーが発生しました： {}".format(e)
        else :
            answer_text = "Open AI APIキーが設定されていないため利用できません。先に APIキーを取得して設定してください。"

        print(answer_text)
        return answer_text

# ==================================
#       本クラスのテスト用処理
# ==================================
def ModuleTest() :
    pass


# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    ModuleTest()

