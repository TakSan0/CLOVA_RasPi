from clova.general.datetime import DateTime
from clova.processor.skill.timer import TimerControl
from clova.processor.skill.news import NewsReader
from clova.processor.skill.weather import WeatherGetter
from clova.processor.skill.line import LineSender

from clova.general.queue import global_speech_queue
from clova.config.config import global_config_prov

from clova.processor.conversation.base_conversation import BaseConversationProvider
from clova.processor.conversation.chatgpt import OpenAIChatGPTConversationProvider

from typing import Dict

# ==================================
#          会話制御クラス
# ==================================
class ConversationController :
    CONVERSATION_MODULES: Dict[str, BaseConversationProvider] = {
        "OpenAI-ChatGPT": OpenAIChatGPTConversationProvider()
    }

    # コンストラクタ
    def __init__(self) :
        print("Create <ConversationController> class")

        self.datetime = DateTime()
        self.tmr = TimerControl()
        self.news = NewsReader()
        self.weather = WeatherGetter()
        self.line = LineSender()


    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <ConversationController> class")

    # 音声以外での待ち処理
    def check_for_interrupted_voice(self) :
        ret = False
        speech_text = ""

        if (len(global_speech_queue) != 0 ) :
            speech_text = global_speech_queue.get()
            print(speech_text)
            ret = True

        return ret, speech_text

    # 問いかけに答える
    def get_answer(self, prompt) :
        answer_text = ""
        answer_selected = False

        # 無言なら無応答
        if (prompt == "") :
            answer_text = ""
            answer_selected = True

        # タイマーの設定
        if (answer_selected == False) :
            answer_text = self.tmr.try_get_answer(prompt)
            if ( answer_text != "" ) :
                answer_selected = True

        # 名前に応答
        if (answer_selected == False) :
            if ( (prompt == "ねえクローバー") or (prompt == "ねえクローバ") ) :
                answer_text = "はい。何でしょう。"
                answer_selected = True

        # 日時応答
        if (answer_selected == False) :
            answer_text = self.datetime.try_get_answer(prompt)
            if ( answer_text != "" ) :
                answer_selected = True

        # ニュース応答
        if (answer_selected == False) :
            answer_text = self.news.try_get_answer(prompt)
            if ( answer_text != "" ) :
                answer_selected = True

        # 天気応答
        if (answer_selected == False) :
            answer_text = self.weather.try_get_answer(prompt)
            if ( answer_text != "" ) :
                answer_selected = True

        # LINE送信応答
        if (answer_selected == False) :
            answer_text = self.line.try_get_answer(prompt)
            if ( answer_text != "" ) :
                answer_selected = True

        # どれにも該当しないときには AI に任せる。
        if (answer_selected == False ) :
            system = global_config_prov.get_general_config()["apis"]["conversation"]["system"]
            kwargs = global_config_prov.get_general_config()["apis"]["conversation"]["params"]
            answer_text = self.CONVERSATION_MODULES[system].get_answer(prompt, **kwargs)

            # AI が利用不可の場合は
            if answer_text is None :
                # 謝るしかない…
                answer_text = "すみません。質問が理解できませんでした。"
                answer_selected = True

        return answer_text

# ==================================
#       本クラスのテスト用処理
# ==================================
def module_test() :
    # 現状何もしない
    pass

# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    module_test()

