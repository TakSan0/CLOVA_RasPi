import time
from CLOVA_queue import global_speech_queue

# ==================================
#       ボリューム制御クラス
# ==================================
class VolumeControl :
    vol_value = 1.0
    _vol_step  = 7
    VOL_MIN_STEP = 0
    VOL_MAX_STEP = 12
    
    # ボリュームテーブル（後でちゃんと計算しないとバランス悪い）
    VOL_TABLE = [ 0.001, 0.01, 0.1, 0.15, 0.2, 0.3, 0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0 ]  

    # コンストラクタ
    def __init__(self) :
        print("Create <VolumeControl> class")

        self._vol_step = 7

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <VolumeControl> class")

    # ボリューム [+] 押下時処理
    def VolUpCallback(self, arg) :
        if (self._vol_step < self.VOL_MAX_STEP) :
            self._vol_step += 1
            self.vol_value = self.VOL_TABLE[self._vol_step]
            print("Vol + [={}({})]".format(self._vol_step, self.vol_value))
            vol_speech = "ボリュームを {} に設定しました。".format(str(self._vol_step))
            print(vol_speech)
            global_speech_queue.AddToQueue(vol_speech)

    # ボリューム [-] 押下時処理
    def VolDownCallback(self, arg) :
        if (self._vol_step > self.VOL_MIN_STEP) :
            self._vol_step -= 1
            self.vol_value = self.VOL_TABLE[self._vol_step]
            print("Vol - [={}({})]".format(self._vol_step, self.vol_value))
            vol_speech = "ボリュームを {} に設定しました。".format(str(self._vol_step))
            print(vol_speech)
            global_speech_queue.AddToQueue(vol_speech)

# ==================================
#      外部参照用のインスタンス
# ==================================
global_vol = VolumeControl()

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
    ModuleTest()

