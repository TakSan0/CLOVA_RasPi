import time
import re
from CLOVA_openai import OpenaiApiControl
from CLOVA_datetime import DateTime
from CLOVA_timer import TimerControl
from CLOVA_news import NewsReader
from CLOVA_weather import WeatherGetter
from CLOVA_line import LineSender

from CLOVA_queue import global_speech_queue
from CLOVA_charactor import global_charactor

# ==================================
#          会話制御クラス
# ==================================
class Conversation :
    # コンストラクタ
    def __init__(self) :
        print("Create <Conversation> class")

        self.datetime = DateTime()
        self.tmr = TimerControl()
        self.news = NewsReader();
        self.weather = WeatherGetter()
        self.openai = OpenaiApiControl()
        self.line = LineSender()


    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <Conversation> class")

    # 音声以外での待ち処理
    def CheckIfInterruptedVoiceExists(self) :
        ret = False
        speech_text = ""

        if (len(global_speech_queue) != 0 ) :
            speech_text = global_speech_queue.GetFromQueue()
            print(speech_text)
            ret = True

        return ret, speech_text

    # 問いかけに答える
    def GetAnswer(self, request_string) :
        answer_text = ""
        answer_selected = False

        # 無言なら無応答
        if (request_string == "") :
            answer_text = ""
            answer_selected = True

        # タイマーの設定
        if (answer_selected == False) :
            answer_text = self.tmr.GetAnswerIfTextIsRequestTimerSet(request_string)
            if ( answer_text != "" ) :
                answer_selected = True

        # 名前に応答
        if (answer_selected == False) :
            if ( (request_string == "ねえクローバー") or (request_string == "ねえクローバ") ) :
                answer_text = "はい。何でしょう。"
                answer_selected = True

        # 日時応答
        if (answer_selected == False) :
            answer_text = self.datetime.GetAnswerIfTextIsRequestDateTime(request_string)
            if ( answer_text != "" ) :
                answer_selected = True

        # ニュース応答
        if (answer_selected == False) :
            answer_text = self.news.GetAnswerIfTextIsRequestingNews(request_string)
            if ( answer_text != "" ) :
                answer_selected = True

        # 天気応答
        if (answer_selected == False) :
            answer_text = self.weather.GetAnswerIfTextIsRequestingWeather(request_string)
            if ( answer_text != "" ) :
                answer_selected = True

        # LINE送信応答
        if (answer_selected == False) :
            answer_text = self.line.GetAnswerIfTextIsLineMessage(request_string)
            if ( answer_text != "" ) :
                answer_selected = True

        # どれにも該当しないときには AI に任せる。
        if (answer_selected == False ) :

            # OpenAI 系の場合(最初の3文字が 'gpt' の場合)
            if ( global_charactor.setting_json["charactors"][global_charactor.sel_num]["Personality"]["aisystem"][:3] == "gpt" ) :
                answer_text = self.openai.GetAnswerFromAi(global_charactor.setting_json["charactors"][global_charactor.sel_num]["Personality"]["aisystem"], request_string)
                answer_selected = True

            # Bard 等の 他のAPI が利用可能になっていったら ここに入れていく...
            #elif () :

            # AI が利用不可の場合は
            else :
                # 謝るしかない…
                answer_text = "すみません。質問が理解できませんでした。"
                answer_selected = True

        return answer_text

# ==================================
#       本クラスのテスト用処理
# ==================================
def ModuleTest() :
    # 現状何もしない
    pass

# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    ModuleTest()

