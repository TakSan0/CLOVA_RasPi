import os
import http.server
from urllib.parse import parse_qs
import json
import dotenv
from typing import Tuple

dotenv.load_dotenv()

# ==================================
#       設定パラメータ管理クラス
# ==================================


class ConfigurationProvider:
    general_config = None
    GENERAL_CONFIG_FILENAME = "./CLOVA_RasPi.json"
    requirements_config = None
    REQUIREMENTS_CONFIG_FILENAME = "./assets/CLOVA_requirements.json"

    # コンストラクタ
    def __init__(self):
        print("Create <ConfigurationProvider> class")
        print("GENERAL_CONFIG_FILENAME={}".format(self.GENERAL_CONFIG_FILENAME))
        print("REQUIREMENTS_CONFIG_FILENAME={}".format(self.REQUIREMENTS_CONFIG_FILENAME))

        self.load_config_file()
        self.assert_current_config_requirements()

    # デストラクタ
    def __del__(self):
        # 現状ログ出すだけ
        print("Delete <ConfigurationProvider> class")

    def get_general_config(self):
        return self.general_config

    def get_requirements_config(self):
        return self.requirements_config

    # 全設定パラメータを読み取る
    def load_config_file(self):
        with open(self.GENERAL_CONFIG_FILENAME, "r", encoding="utf-8") as cfg_file:
            file_text = cfg_file.read()
        self.general_config = json.loads(file_text)
        with open(self.REQUIREMENTS_CONFIG_FILENAME, "r", encoding="utf-8") as cfg_file:
            file_text = cfg_file.read()
        self.requirements_config = json.loads(file_text)

    # 全設定パラメータを書き込む
    def save_general_config_file(self, conf):
        with open(self.GENERAL_CONFIG_FILENAME, "w", encoding="utf-8") as cfg_file:
            json.dump(conf, cfg_file, indent='\t', ensure_ascii=False)
            cfg_file.write("\n")

    def assert_current_config_requirements(self):
        if self.general_config["apis"]["tts"]["system"] is not None:
            assert self.is_requirements_met(self.requirements_config["tts"][self.general_config["apis"]["tts"]["system"]]["requires"]), "TTS API Key requirements are not satisfied."
        if self.general_config["apis"]["stt"]["system"] is not None:
            assert self.is_requirements_met(self.requirements_config["stt"][self.general_config["apis"]["stt"]["system"]]["requires"]), "STT API Key requirements are not satisfied."
        if self.general_config["apis"]["conversation"]["system"] is not None:
            assert self.is_requirements_met(self.requirements_config["conversation"][self.general_config["apis"]["conversation"]
                                            ["system"]]["requires"]), "Conversation API Key requirements are not satisfied."

    def is_requirements_met(self, req: Tuple[Tuple[str]]) -> bool:
        for requirement_group in req:
            # グループ内の要件のいずれかがos.environに存在するかをチェックします
            if any(requirement in os.environ and os.environ[requirement] != "" for requirement in requirement_group):
                continue  # 少なくとも1つの要件が満たされている場合は、次のグループに進みます
            else:
                return False  # グループ内の要件がいずれも満たされていない場合はFalseを返します
        return True


# TODO: add support for changing apis
# TODO: add support for checking requirements met before changing

# ==================================
#    Setting HTTPハンドラクラス
# ==================================
class HttpReqSettingHandler(http.server.BaseHTTPRequestHandler):

    # GETリクエストを受け取った場合の処理
    def do_GET(self):
        # キャラクタの選択肢を作成する。
        with open("./assets/CLOVA_systems.json", "r", encoding="utf-8") as char_file:
            file_text = char_file.read()
        char_cfg_json = json.loads(file_text)

        char_selection = ""
        for index, char_data in char_cfg_json["characters"].items():
            line_data = "            <option value=\"{}\">{} (CV: {})</option>\n".format(index, char_data["persona"]["name"], index)
            char_selection += line_data
        # print(char_selection)

        # HTMLファイルを読み込む
        with open("./assets/index.html", "r", encoding="utf-8") as html_file:
            html = html_file.read()

        html = html.replace("{characterSelList}", char_selection)

        sys_config = global_config_prov.get_general_config()

        # 変数の値をHTMLに埋め込む
        html = html.replace("{DefaultCharSel}", str(sys_config["character"]))
        html = html.replace("{MicChannels}", str(sys_config["hardware"]["audio"]["microphone"]["num_ch"]))
        html = html.replace("{MicIndex}", str(sys_config["hardware"]["audio"]["microphone"]["index"]))
        html = html.replace("{SilentThreshold}", str(sys_config["hardware"]["audio"]["microphone"]["silent_thresh"]))
        html = html.replace("{TerminateSilentDuration}", str(sys_config["hardware"]["audio"]["microphone"]["term_duration"]))
        html = html.replace("{SpeakerChannels}", str(sys_config["hardware"]["audio"]["speaker"]["num_ch"]))
        html = html.replace("{SpeakerIndex}", str(sys_config["hardware"]["audio"]["speaker"]["index"]))
        # print(html) # for debug

        # HTTPレスポンスを返す
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    # POSTリクエストを受け取った場合の処理
    def do_POST(self):
        sys_config = global_config_prov.get_general_config()

        # POSTデータを取得する
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        post_data = post_data.decode("utf-8")

        data = parse_qs(post_data)

        print(data)  # for debug

        # 変数を更新する
        sys_config["character"] = data["default_char_sel"][0]
        sys_config["hardware"]["audio"]["microphone"]["num_ch"] = int(data["mic_channels"][0])
        sys_config["hardware"]["audio"]["microphone"]["index"] = int(data["mic_index"][0])
        sys_config["hardware"]["audio"]["microphone"]["silent_thresh"] = int(data["silent_thresh"][0])
        sys_config["hardware"]["audio"]["microphone"]["term_duration"] = int(data["term_duration"][0])
        sys_config["hardware"]["audio"]["speaker"]["num_ch"] = int(data["speaker_channels"][0])
        sys_config["hardware"]["audio"]["speaker"]["index"] = int(data["speaker_index"][0])

        print("default_char_sel={}".format(sys_config["character"]))
        print("mic num_ch={}".format(sys_config["hardware"]["audio"]["microphone"]["num_ch"]))
        print("mic index={}".format(sys_config["hardware"]["audio"]["microphone"]["index"]))
        print("mic silent_thresh={}".format(sys_config["hardware"]["audio"]["microphone"]["silent_thresh"]))
        print("mic term_duration={}".format(sys_config["hardware"]["audio"]["microphone"]["term_duration"]))
        print("spk num_ch={}".format(sys_config["hardware"]["audio"]["speaker"]["num_ch"]))
        print("spk index={}".format(sys_config["hardware"]["audio"]["speaker"]["index"]))

        global_config_prov.save_general_config_file(sys_config)

        # HTTPレスポンスを返す
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


# ==================================
#      外部参照用のインスタンス
# ==================================
global_config_prov = ConfigurationProvider()

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
