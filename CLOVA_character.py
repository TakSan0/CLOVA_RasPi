import os
import time
import json
from CLOVA_queue import global_speech_queue

# ==================================
#       キャラクタ管理クラス
# ==================================
class characterSelection :

    # コンストラクタ
    def __init__(self) :
        print("Create <characterSelection> class")

        # キャラクタ設定ファイルの読み込み
        self.read_character_config_file()


    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <characterSelection> class")

    # キャラクタ設定
    def set_character(self, num) :
        self.sel_num = num
        select_speech = "キャラクタ {} さんが選択されました。".format(self.setting_json["characters"][self.sel_num]["Name"])
        print(select_speech)
        global_speech_queue.add(select_speech)

    # キャラクタの特徴を取得。
    def get_character_description(self) :
        # OpenAI に指示するキャラクタの特徴をひとつの文字列化する。
        description = ""
        if (self.setting_json["characters"][self.sel_num]["Personality"]["name"] != "") :
            description += "あなたの名前は {}です。\n".format(self.setting_json["characters"][self.sel_num]["Personality"]["name"])

        if (self.setting_json["characters"][self.sel_num]["Personality"]["gender"] != "") :
            description += "あなたの性別は {}です。\n".format(self.setting_json["characters"][self.sel_num]["Personality"]["gender"])

        if (self.setting_json["characters"][self.sel_num]["Personality"]["myself"] != "") :
            description += "あなたは一人称として {}を使います。\n".format(self.setting_json["characters"][self.sel_num]["Personality"]["myself"])

        if (self.setting_json["characters"][self.sel_num]["Personality"]["type"] != "") :
            description += "あなたの性格は {}\n".format(self.setting_json["characters"][self.sel_num]["Personality"]["type"])

        if (self.setting_json["characters"][self.sel_num]["Personality"]["talkstyle"] != "") :
            description += "あなたの話し方は {}\n".format(self.setting_json["characters"][self.sel_num]["Personality"]["talkstyle"])

        if (self.setting_json["characters"][self.sel_num]["Personality"]["detail"] != "") :
            description += "あなたは {}\n".format(self.setting_json["characters"][self.sel_num]["Personality"]["detail"])

        print("character Description={}".format(description))
        return description

    # キャラクタ選択可否のチェック
    def check_character_selectable(self, num) :
        ret = True

        # Web版Voice Text 用のキャラクタの場合
        if (self.setting_json["characters"][num]["Speaker"]["system"] == "VoiceText" ) :
            # 空白なら無効化
            if (os.environ["VOICE_TEXT_API_KEY"] == "") :
                ret = False
        # |WEB版VOICEVOX API 用のキャラクタの場合
        if (self.setting_json["characters"][num]["Speaker"]["system"] == "VoiceVox" ) :
            # 空白なら無効化
            if (os.environ["WEB_VOICEVOX_API_KEY"] == "") :
                ret = False
        # AITalk WebAPI 用のキャラクタの場合
        if (self.setting_json["characters"][num]["Speaker"]["system"] == "AITalk") :
            # 空白なら無効化
            if (os.environ["AITALK_USER"] == "") or (os.environ["AITALK_PASSWORD"] == "") :
                ret = False

        return ret

    # 次のキャラクターを選択
    def select_next_character(self, arg) :
        num = self.sel_num
        while True :
            # 次を選択
            if ( (num + 1) < self.num_of_char) :
                num = num + 1
            else :
                num = 0
            # 選択可のキャラクタまで行くか、一周したら抜ける
            if ( (self.check_character_selectable(num) == True ) or (num == self.sel_num ) ):
                break

        self.set_character(num)

    # キャラクタ設定ファイルを読み出す
    def read_character_config_file(self) :
        with open("~/CLOVA_RasPi/CLOVA_character.json", "r", encoding="utf-8") as cfg_file:
            file_text = cfg_file.read()
        self.setting_json = json.loads(file_text)
        self.num_of_char = len(self.setting_json["characters"])

# ==================================
#      外部参照用のインスタンス
# ==================================
global_character = characterSelection()

# ==================================
#       本クラスのテスト用処理
# ==================================
def module_test() :
    # 現状何もしない
    print( "CharCount = {}".format(str(len(global_character.setting_json["characters"]))))
    print( global_character.setting_json["characters"][0]["Name"] )
    print( global_character.setting_json["characters"][1]["Name"] )

# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    module_test()

