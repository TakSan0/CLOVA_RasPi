from collections import deque

# ==================================
#          発話キュークラス
# ==================================
class SpeechQueue :
    # コンストラクタ
    def __init__(self) :
        print("Create <SpeechQueue> class")

        self._queue = deque()

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <SpeechQueue> class")

    # 文字列をキューに格納する
    def AddToQueue(self, string):
        self._queue.append(string)

    # キューから文字列を取得する
    def GetFromQueue(self):
        return self._queue.popleft()

    def __len__(self):
        return len(self._queue)

# ==================================
#      外部参照用のインスタンス
# ==================================
global_speech_queue = SpeechQueue()

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

