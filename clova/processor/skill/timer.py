import threading as th
import time
import datetime
import re

from clova.general.queue import global_speech_queue

from clova.processor.skill.base_skill import BaseSkillProvider
from clova.general.logger import BaseLogger

# ==================================
#         タイマー管理クラス
# ==================================
# タイマー管理クラス


class TimerSkillProvider(BaseSkillProvider, BaseLogger):
    # コンストラクタ
    def __init__(self):
        super().__init__()

        self._active = False
        self._is_timer_set = False
        self._is_alarm_on = False
        self._timer_thread = th.Thread(target=self._thread_timer, args=(), name="TimerMain", daemon=True)
        self._timer_thread.start()
        self._duration = ""

    # デストラクタ
    def __del__(self):
        super().__del__()

        self.stop()
        self._active = False
        time.sleep(1)
        self._timer_thread.join()
        self.log("DTOR", "_timer_thread Joined!")

    # タイマの監視を開始
    def start(self):
        if (not self._is_timer_set):
            self.log("start", "Timer started!")
            self._is_timer_set = True

    # タイマの監視を停止

    def stop(self):
        if (self._is_timer_set):
            self.log("stop", "Timer stopped!")
            self._is_timer_set = False

    # タイマのスレッド関数
    def _thread_timer(self):
        self._active = True

        while (self._active):
            self._timer_update()
            time.sleep(1)

    # タイマの監視処理

    def _timer_update(self):
        if (self._is_timer_set):
            self.log("_timer_update", "Waiting Timer!")
            if (datetime.datetime.now() >= self.target_time):
                # self._is_timer_set = False
                self._is_alarm_on = True
                self.log("_timer_update", "Time UP!!!!")
                answer_text = "{} 経ちました。".format(self._duration)
                global_speech_queue.add(answer_text)
                self.log("_timer_update", answer_text)
                self.target_time += datetime.timedelta(seconds=10)
                # self.Stop()

    # タイマーの 要求に答える。タイマーの要求ではなければ None を返す
    def try_get_answer(self, request_text):
        if (not self._is_alarm_on):
            if ((re.match(".*後に.*知らせて", request_text) is not None) or (re.match(".*後に.*タイマ.*セット", request_text) is not None)):
                self.log("DTOR", "Match1")
                pos = request_text.find("後")
                duration = request_text[:pos]
                self._duration = duration
                self.log("DTOR", duration)
                if (duration != ""):
                    answer_text = "{}後にタイマーをセットします。".format(duration)
                    self.set_duration(duration)
                    self.log("DTOR", answer_text)
                    # self._is_timer_set = True #??
                    return answer_text
                else:
                    return None
            else:
                return None
        else:
            if ("わかりました" in request_text) or ("了解" in request_text) or ("止めて" in request_text):
                answer_text = "タイマ通知を終了します。"
                self._is_alarm_on = False
                self._is_timer_set = False
                self.stop()
                self.log("try_get_answer", answer_text)
                return answer_text
            else:
                # answer_text = "{} 経ちました。".format(self._duration)
                # global_speech_queue.AddToQueue(answer_text)

                answer_text = "終了待ちです。"
                self.log("try_get_answer", answer_text)
                return answer_text

    # 満了までの期間から、満了日時分秒を割り出す
    def set_duration(self, duration):
        if (("時間" in duration) or ("分" in duration) or ("秒" in duration)):
            secs = self.parse_time(duration)
            self.target_time = datetime.datetime.now() + datetime.timedelta(seconds=secs)
            self.log("set_duration", "{} = {} sec @ {}".format(duration, secs, self.target_time))
            self._is_timer_set = True
            self.start()
            # is_timer_set = True

    # 文字列の時分秒の部分を字句解析して秒に変換
    def parse_time(self, time_string):
        self.log("parse_time", "time_string={}".format(time_string))
        time_pattern = r"(?:(\d+)時間)?(?:(\d+)分)?(?:(\d+)秒)?"
        hours, minutes, seconds = map(int, re.match(time_pattern, time_string).groups(default=0))
        self.log("parse_time", "{}時間 {}分 {}秒 = {}sec".format(hours, minutes, seconds, ((hours * 3600) + (minutes * 60) + seconds)))
        return ((hours * 3600) + (minutes * 60) + seconds)

# ==================================
#       本クラスのテスト用処理
# ==================================


def module_test2():
    tmr = TimerSkillProvider()
    # seconds = tmr.ParseTime("3時間40分59秒後")
    seconds = tmr.parse_time("1分10秒後")
    print(seconds)


def module_test():
    tmr = TimerSkillProvider()
    tmr.try_get_answer("1分10秒後に知らせて")

    test_event = th.Event()
    test_thread = th.Thread(target=WaitForTestOrEnterKey, args=(test_event,))
    test_thread.start()

    while not test_event.is_set():
        # 他のスレッドが動ける処理をここに記述
        if (not tmr._is_timer_set):
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
    module_test()
