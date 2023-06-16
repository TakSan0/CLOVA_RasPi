import os
from bardapi import Bard

from clova.config.character import global_character_prov

from clova.processor.conversation.base_conversation import BaseConversationProvider

from clova.general.logger import BaseLogger

# Bard にはタイマースキル以外いらないかも


class BardConversationProvider(BaseConversationProvider, BaseLogger):
    OPENAI_CHARACTER_CONFIG = "あなたはサービス終了で使えなくなったクローバの後を次ぎました。"

    is_first_time = True

    # コンストラクタ
    def __init__(self):
        super().__init__()

        self.BARD_PSID = os.environ["BARD_PSID"]
        self.bard = Bard(token=self.BARD_PSID)
        self.set_persona("")

    # デストラクタ
    def __del__(self):
        super().__del__()

    def set_persona(self, prompt):
        self._char_setting_str = self.OPENAI_CHARACTER_CONFIG + prompt

    def get_answer(self, prompt, **kwargs):
        self.log("get_answer", "Bard 応答作成中")
        actual_prompt = self._char_setting_str + global_character_prov.get_character_prompt() + "\n" + prompt if self.is_first_time else prompt

        result = self.bard.get_answer(actual_prompt)

        self.log("get_answer", result)

        self.is_first_time = False

        return result["content"]
