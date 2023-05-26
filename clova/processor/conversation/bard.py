import os
from bardapi import Bard
from clova.io.local.led import global_led_Ill
from clova.config.character import global_character_prov
from clova.processor.conversation.base_conversation import BaseConversationProvider

# Bard にはタイマースキル以外いらないかも
class BardConversationProvider(BaseConversationProvider) :
    OPENAI_CHARACTER_CONFIG = "あなたはサービス終了で使えなくなったクローバの後を次ぎました。"

    is_first_time = True

    # コンストラクタ
    def __init__(self) :
        self.BARD_PSID = os.environ["BARD_PSID"]
        self.bard = Bard(token=self.BARD_PSID)
        self.set_persona("")
        print("Create <OpenAIChatGPTConversationProvider> class")

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <OpenAIChatGPTConversationProvider> class")

    def set_persona(self, prompt) :
        self._char_setting_str = self.OPENAI_CHARACTER_CONFIG + prompt

    def get_answer(self, prompt, **kwargs) :
        # 底面 LED をピンクに
        global_led_Ill.set_all_pink()
        print("Bard 応答作成中")
        actual_prompt = self._char_setting_str + global_character_prov.get_character_prompt() + "\n" + prompt if self.is_first_time else prompt

        result = self.bard.get_answer(actual_prompt)

        print(result)

        self.is_first_time = False

        return result["content"]
