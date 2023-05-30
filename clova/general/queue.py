from collections import deque
import regex as re
from clova.general.logger import BaseLogger

# ==================================
#          発話キュークラス
# ==================================


class SpeechQueue(BaseLogger):
    REGEX_ASSUME_EMPTY = re.compile("^[\\p{P}|\\p{S}|\\p{Z}|\n]*$")

    # コンストラクタ
    def __init__(self):
        super().__init__()

        self._queue = deque()

    # デストラクタ
    def __del__(self):
        super().__del__()

    # 文字列をキューに格納する
    def add(self, string):
        if string.strip() == "" or self.REGEX_ASSUME_EMPTY.match(string) is not None:
            self.log("add", "SpeechQueue却下: \'{}\'".format(string))
            return
        self.log("add", "SpeechQueue += \'{}\'".format(string))
        self._queue.append(string)

    # キューから文字列を取得する
    def get(self):
        return self._queue.popleft()

    def clear(self):
        self._queue.clear()

    def __len__(self):
        return len(self._queue)


# ==================================
#      外部参照用のインスタンス
# ==================================
global_speech_queue = SpeechQueue()

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
