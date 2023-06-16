from typing import Dict, Tuple, Type

from clova.processor.conversation.base_conversation import BaseConversationProvider
from clova.processor.conversation.chatgpt import OpenAIChatGPTConversationProvider
from clova.processor.conversation.bard import BardConversationProvider

from clova.processor.skill.base_skill import BaseSkillProvider
from clova.processor.skill.timer import TimerSkillProvider
from clova.processor.skill.news import NewsSkillProvider
from clova.processor.skill.weather import WeatherSkillProvider
from clova.processor.skill.line import LineSkillProvider
from clova.processor.skill.datetime import DateTimeSkillProvider

from clova.general.queue import global_speech_queue
from clova.config.config import global_config_prov
from clova.io.local.led import global_led_Ill

from clova.general.logger import BaseLogger

# ==================================
#          会話制御クラス
# ==================================


class ConversationController(BaseLogger):
    CONVERSATION_MODULES: Dict[str, Type[BaseConversationProvider]] = {
        "OpenAI-ChatGPT": OpenAIChatGPTConversationProvider,
        "Bard": BardConversationProvider
    }
    SKILL_MODULES: Tuple[BaseSkillProvider] = [
        TimerSkillProvider(), NewsSkillProvider(), WeatherSkillProvider(), LineSkillProvider(), DateTimeSkillProvider()
    ]

    # コンストラクタ
    def __init__(self):
        super().__init__()

        self.system = global_config_prov.get_general_config()["apis"]["conversation"]["system"]
        self.provider = self.CONVERSATION_MODULES[self.system]()

    # デストラクタ
    def __del__(self):
        super().__del__()

    # 音声以外での待ち処理
    def check_for_interrupted_voice(self):
        ret = False
        speech_text = ""

        if (len(global_speech_queue) != 0):
            speech_text = global_speech_queue.get()
            print(speech_text)
            ret = True

        return ret, speech_text

    # 問いかけに答える
    def get_answer(self, prompt):
        # 無言なら無応答
        if (prompt == ""):
            return ""

        # 名前に応答
        if ((prompt == "ねえクローバー") or (prompt == "ねえクローバ")):
            return "はい。何でしょう。"

        # スキル
        for skill in self.SKILL_MODULES:
            result = skill.try_get_answer(prompt)
            if result:
                return result

        # どれにも該当しないときには AI に任せる。
        kwargs = global_config_prov.get_general_config()["apis"]["conversation"]["params"]

        # 底面 LED をピンクに
        global_led_Ill.set_all(global_led_Ill.RGB_PINK)

        result = self.provider.get_answer(prompt, **kwargs)
        if result:
            return result

        # AI が利用不可の場合は謝るしかない…
        return "すみません。質問が理解できませんでした。"

# ==================================
#       本クラスのテスト用処理
# ==================================


def module_test():
    # 現状何もしない
    pass


# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    module_test()
