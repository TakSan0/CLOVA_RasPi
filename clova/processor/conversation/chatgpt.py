import os
import openai
from clova.config.character import global_character_prov
from clova.processor.conversation.base_conversation import BaseConversationProvider

# ==================================
#         OpenAI APIクラス
# ==================================


class OpenAIChatGPTConversationProvider(BaseConversationProvider):
    OPENAI_CHARACTER_CONFIG = "あなたはサービス終了で使えなくなったクローバの後を次ぎました。"

    # コンストラクタ
    def __init__(self):
        self.OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
        self.set_persona("")
        print("Create <OpenAIChatGPTConversationProvider> class")

    # デストラクタ
    def __del__(self):
        # 現状ログ出すだけ
        print("Delete <OpenAIChatGPTConversationProvider> class")

    def set_persona(self, prompt):
        self._char_setting_str = self.OPENAI_CHARACTER_CONFIG + prompt

    def get_answer(self, prompt, **kwargs):
        openai.api_key = self.OPENAI_API_KEY

        print("OpenAI 応答作成中")
        desc = global_character_prov.get_character_prompt()

        if (self.OPENAI_API_KEY != ""):
            try:

                ai_response = openai.ChatCompletion.create(
                    model=kwargs["model"],
                    messages=[
                        {"role": "system", "content": self._char_setting_str + desc},
                        {"role": "user", "content": prompt},
                    ]
                )
                # print(ai_response["choices"][0]["message"]["content"]) #返信のみを出力
                print(ai_response)

                # print(len(ai_response))
                if (len(ai_response) != 0):
                    result = ai_response["choices"][0]["message"]["content"]
                else:
                    print("AIからの応答が空でした。")
                    result = None

            except openai.error.RateLimitError:
                result = "OpenAIエラー：APIクオータ制限に達しました。しばらく待ってから再度お試しください。改善しない場合は、月間使用リミットに到達したか無料枠期限切れの可能性もあります。"
            except openai.error.AuthenticationError:
                result = "OpenAIエラー：Open AI APIキーが不正です。"
            except openai.error.APIConnectionError:
                result = "OpenAIエラー：Open AI APIに接続できませんでした。"
            except openai.error.ServiceUnavailableError:
                result = "OpenAIエラー：Open AI サービス無効エラーです。"
            except openai.error.OpenAIError as e:
                result = "OpenAIエラー：Open AI APIエラーが発生しました： {}".format(e)
            except Exception as e:
                result = "不明なエラーが発生しました： {}".format(e)
        else:
            result = "Open AI APIキーが設定されていないため利用できません。先に APIキーを取得して設定してください。"

        print(result)
        return result

# ==================================
#       本クラスのテスト用処理
# ==================================


def module_test():
    pass


# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    module_test()
