import os
import time
import json
from CLOVA_queue import global_speech_queue

# ==================================
#       キャラクタ管理クラス
# ==================================
class CharactorSelection :

    # コンストラクタ
    def __init__(self) :
        print("Create <CharactorSelection> class")

        # キャラクタ設定ファイルの読み込み
        self.ReadCharactorConfigFile()


    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <CharactorSelection> class")

    # キャラクタ設定
    def SetCharactor(self, num) :
        self.sel_num = num
        select_speech = "キャラクタ {} さんが選択されました。".format(self.setting_json["charactors"][self.sel_num]["Name"])
        print(select_speech)
        global_speech_queue.AddToQueue(select_speech)

    # キャラクタの特徴を取得。
    def GetCharactorDescription(self) :
        # OpenAI に指示するキャラクタの特徴をひとつの文字列化する。
        description = ""
        if (self.setting_json["charactors"][self.sel_num]["Personality"]["name"] != "") :
            description += "あなたの名前は {}です。\n".format(self.setting_json["charactors"][self.sel_num]["Personality"]["name"])

        if (self.setting_json["charactors"][self.sel_num]["Personality"]["gender"] != "") :
            description += "あなたの性別は {}です。\n".format(self.setting_json["charactors"][self.sel_num]["Personality"]["gender"])

        if (self.setting_json["charactors"][self.sel_num]["Personality"]["myself"] != "") :
            description += "あなたは一人称として {}を使います。\n".format(self.setting_json["charactors"][self.sel_num]["Personality"]["myself"])

        if (self.setting_json["charactors"][self.sel_num]["Personality"]["type"] != "") :
            description += "あなたの性格は {}\n".format(self.setting_json["charactors"][self.sel_num]["Personality"]["type"])

        if (self.setting_json["charactors"][self.sel_num]["Personality"]["talkstyle"] != "") :
            description += "あなたの話し方は {}\n".format(self.setting_json["charactors"][self.sel_num]["Personality"]["talkstyle"])

        if (self.setting_json["charactors"][self.sel_num]["Personality"]["detail"] != "") :
            description += "あなたは {}\n".format(self.setting_json["charactors"][self.sel_num]["Personality"]["detail"])

        print("Charactor Description={}".format(description))
        return description

    # キャラクタ選択可否のチェック
    def CheckIfCharactorSelectable(self, num) :
        ret = True

        # Web版Voice Text 用のキャラクタの場合
        if (self.setting_json["charactors"][num]["Speaker"]["system"] == "VoiceText" ) :
            # 空白なら無効化
            if (os.environ['VOICE_TEXT_API_KEY'] == "") :
                ret = False
        # |WEB版VOICEVOX API 用のキャラクタの場合
        if (self.setting_json["charactors"][num]["Speaker"]["system"] == "VoiceVox" ) :
            # 空白なら無効化
            if (os.environ['WEB_VOICEVOX_API_KEY'] == "") :
                ret = False
        # AITalk WebAPI 用のキャラクタの場合
        if (self.setting_json["charactors"][num]["Speaker"]["system"] == "AITalk") :
            # 空白なら無効化
            if (os.environ['AITALK_USER'] == "") or (os.environ['AITALK_PASSWORD'] == "") :
                ret = False

        return ret

    # 次のキャラクターを選択
    def SelNextChar(self, arg) :
        num = self.sel_num
        while True :
            # 次を選択
            if ( (num + 1) < self.num_of_char) :
                num = num + 1
            else :
                num = 0
            # 選択可のキャラクタまで行くか、一周したら抜ける
            if ( (self.CheckIfCharactorSelectable(num) == True ) or (num == self.sel_num ) ):
                break

        self.SetCharactor(num)

    # キャラクタ設定ファイルを読み出す
    def ReadCharactorConfigFile(self) :
        file_path = os.path.expanduser("~/CLOVA_RasPi/CLOVA_charactor.json")
        with open(file_path, 'r', encoding='utf-8') as cfg_file:
            file_text = cfg_file.read()
        self.setting_json = json.loads(file_text)
        self.num_of_char = len(self.setting_json["charactors"])

# ==================================
#      外部参照用のインスタンス
# ==================================
global_charactor = CharactorSelection()

# ==================================
#       本クラスのテスト用処理
# ==================================
def ModuleTest() :
    # 現状何もしない
    print( "CharCount = {}".format(str(len(global_charactor.setting_json["charactors"]))))
    print( global_charactor.setting_json["charactors"][0]["Name"] )
    print( global_charactor.setting_json["charactors"][1]["Name"] )

# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    ModuleTest()

