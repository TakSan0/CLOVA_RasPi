import threading as th
import time
import datetime
import re

from CLOVA_queue import global_speech_queue

# ==================================
#         タイマー管理クラス
# ==================================
# タイマー管理クラス
class TimerControl :
    # コンストラクタ
    def __init__(self) :
        # 現状ログ出すだけ
        print("Create <TimerControl> class")

        self._active = False
        self._is_timer_set = False
        self._is_alarm_on = False
        self._timer_thread = th.Thread(target = self.TimerMain, args = (), name = 'TimerMain', daemon = True)
        self._timer_thread.start()
        self._duration = ""

    # デストラクタ
    def __del__(self) :
        print("Delete <TimerControl> class")

        self.Stop()
        self._active = False
        time.sleep(1)
        self._timer_thread.join()
        print("_timer_thread Joined!")

    # タイマの監視を開始
    def Start(self) :
        if (self._is_timer_set == False) :
            print("Timer started!")
            self._is_timer_set = True


    # タイマの監視を停止
    def Stop(self) :
        if (self._is_timer_set == True) :
            print("Timer stopped!")
            self._is_timer_set = False

    # タイマのスレッド関数
    def TimerMain(self) :
        self._active = True

        while (self._active == True) :
            self.TimerWatch()
            time.sleep(1)


    # タイマの監視処理
    def TimerWatch(self) :
        if (self._is_timer_set == True) :
            print ("Waiting Timer!")
            if (datetime.datetime.now() >= self.target_time) :
                #self._is_timer_set = False
                self._is_alarm_on = True
                print("Time UP!!!!")
                answer_text = "{} 経ちました。".format(self._duration)
                global_speech_queue.AddToQueue(answer_text)
                print(answer_text)
                self.target_time += datetime.timedelta(seconds=10)
                #self.Stop()

    # タイマーの 要求に答える。タイマーの要求ではなければ 空 の文字列を返す
    def GetAnswerIfTextIsRequestTimerSet(self, request_text) :
        if (self._is_alarm_on == False) :
            if ( ( re.match(".*後に.*知らせて", request_text) != None ) or ( re.match(".*後に.*タイマ.*セット", request_text) != None ) ):
                print("Match1")
                pos =  request_text.find("後")
                duration = request_text[:pos]
                self._duration = duration
                print(duration)
                if (duration != "" ) :
                    answer_text = '{}後にタイマーをセットします。'.format(duration)
                    self.SetTargetDateTimeForTheDuration(duration)
                    print(answer_text)
                    #self._is_timer_set = True #??
                    return answer_text
                else :
                    return ""
            else :
                return ""
        else :
            if ('わかりました' in request_text ) or ('了解' in request_text ) or ('止めて' in request_text ) :
                answer_text = "タイマ通知を終了します。"
                self._is_alarm_on = False
                self._is_timer_set = False
                self.Stop()
                print(answer_text)
                return answer_text
            else :
                #answer_text = "{} 経ちました。".format(self._duration)
                #global_speech_queue.AddToQueue(answer_text)

                answer_text = "終了待ちです。";
                print(answer_text)
                return answer_text

    # 満了までの期間から、満了日時分秒を割り出す
    def SetTargetDateTimeForTheDuration(self, duration) :
        if ( ( "時間" in duration ) or ( "分" in duration ) or ( "秒" in duration ) ) :
            secs = self.ParseTime(duration)
            self.target_time = datetime.datetime.now() + datetime.timedelta(seconds=secs)
            print("{} = {} sec @ {}".format(duration, secs, self.target_time))
            self._is_timer_set = True
            self.Start()
            #is_timer_set = True

    # 文字列の時分秒の部分を字句解析して秒に変換
    def ParseTime(self, time_string) :
        print("time_string={}".format(time_string))
        time_pattern = r'(?:(\d+)時間)?(?:(\d+)分)?(?:(\d+)秒)?'
        hours, minutes, seconds = map(int, re.match(time_pattern, time_string).groups(default=0))
        print("{}時間 {}分 {}秒 = {}sec".format(hours, minutes, seconds, ( (hours * 3600) + (minutes * 60) + seconds)))
        return ( (hours * 3600) + (minutes * 60) + seconds)

# ==================================
#       本クラスのテスト用処理
# ==================================
def ModuleTest2() :
    tmr = TimerControl()
    #seconds = tmr.ParseTime("3時間40分59秒後")
    seconds = tmr.ParseTime("1分10秒後")
    print(seconds)

def ModuleTest() :
    tmr = TimerControl()
    tmr.GetAnswerIfTextIsRequestTimerSet("1分10秒後に知らせて")

    test_event = th.Event()
    test_thread = th.Thread(target=WaitForTestOrEnterKey, args=(test_event,))
    test_thread.start()

    while not test_event.is_set():
        # 他のスレッドが動ける処理をここに記述
        if (tmr._is_timer_set == False) :
            break
        time.sleep(0.5)

    print("Finished Test!")


def WaitForTestOrEnterKey(event):
    input("Press Enter to FINISH...")
    event.set()


# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    ModuleTest()

