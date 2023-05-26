import json
from CLOVA_queue import global_speech_queue
from CLOVA_config import global_config_prov
from typing import Tuple

# ==================================
#       キャラクタ管理クラス
# ==================================
class CharacterProvider :

    # コンストラクタ
    def __init__(self) :
        print("Create <CharacterProvider> class")

        # キャラクタ設定ファイルの読み込み
        self.read_character_config_file()


    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <CharacterProvider> class")

    # キャラクタ設定
    def set_character(self, id) :
        self.character = self.systems["characters"][id]
        self.current_character_num = self.character_index.index(id)
        select_speech = "キャラクタ {} さんが選択されました。".format(self.character["persona"]["name"])
        print(select_speech)
        global_speech_queue.add(select_speech)

    def get_character_settings(self):
        return self.character

    # キャラクタの特徴を取得。
    def get_character_prompt(self) :
        # OpenAI に指示するキャラクタの特徴をひとつの文字列化する。
        description = ""
        if (self.character["persona"]["name"] != "") :
            description += "あなたの名前は {}です。\n".format(self.character["persona"]["name"])

        if (self.character["persona"]["gender"] != "") :
            description += "あなたの性別は {}です。\n".format(self.character["persona"]["gender"])

        if (self.character["persona"]["myself"] != "") :
            description += "あなたは一人称として {}を使います。\n".format(self.character["persona"]["myself"])

        if (self.character["persona"]["type"] != "") :
            description += "あなたの性格は {}\n".format(self.character["persona"]["type"])

        if (self.character["persona"]["talk_style"] != "") :
            description += "あなたの話し方は {}\n".format(self.character["persona"]["talk_style"])

        if (self.character["persona"]["detail"] != "") :
            description += "あなたは {}\n".format(self.character["persona"]["detail"])

        print("character Description={}".format(description))
        return description

    # キャラクタに必要なクレデンシャル名を取得
    def get_requirements(self, id) -> Tuple[Tuple[str]]:
        return global_config_prov.get_requirements_config()["tts"] \
            [self.systems['characters'][id]["tts"]["system"]] \
            ["requires"]

    # 次のキャラクターを選択
    def select_next_character(self) :
        num = self.current_character_num
        while True :
            # 次を選択
            if ( (num + 1) < self.characters_len) :
                num = num + 1
            else :
                num = 0

            # 選択可のキャラクタまで行くか、一周したら抜ける
            if (
                global_config_prov.is_requirements_met(self.get_requirements(self.character_index[num])) or
                num == self.current_character_num
            ):
                break

        self.set_character(num)

    # キャラクタ設定ファイルを読み出す
    def read_character_config_file(self) :
        with open("./CLOVA_systems.json", "r", encoding="utf-8") as cfg_file:
            file_text = cfg_file.read()
        self.systems = json.loads(file_text)
        self.character_index = list(self.systems["characters"].keys())
        self.characters_len = len(self.character_index)

# ==================================
#      外部参照用のインスタンス
# ==================================
global_character_prov = CharacterProvider()

# ==================================
#       本クラスのテスト用処理
# ==================================
def module_test() :
    # 現状何もしない
    print( "characters_len = {}".format(str(global_character_prov.systems["characters"].keys())))

# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    module_test()

