import os
import openai
from CLOVA_led import global_led_Ill
from CLOVA_character import global_character_prov

# ==================================
#         OpenAI APIクラス
# ==================================
class OpenAiApiControl :
    OPENAI_character_CFG = "あなたはサービス終了で使えなくなったクローバの後を次ぎました。"

    # コンストラクタ
    def __init__(self) :
        self.OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
        self.ser_character_setting("")
        print("Create <OpenaiApiControl> class")

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <OpenaiApiControl> class")

    def ser_character_setting(self, setting_str) :
        self._char_setting_str = self.OPENAI_character_CFG + setting_str

    def get_answer(self, model_name, prompt) :
        openai.api_key = self.OPENAI_API_KEY

        # 底面 LED をピンクに
        global_led_Ill.set_all_pink()
        print("OpenAI 応答作成中")
        desc = global_character_prov.get_character_prompt()

        if (self.OPENAI_API_KEY != "") :
            try:

                ai_response = openai.ChatCompletion.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content":  self._char_setting_str + desc },
                        {"role": "user", "content": prompt},
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
def module_test() :
    pass


# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    module_test()

