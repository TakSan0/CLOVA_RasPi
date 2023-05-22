import os
import http.server
import threading as th
import json
import urllib.parse
import urllib.request

# ==================================
#       設定パラメータ管理クラス
# ==================================
class KeysSetting :
    KEYS_FILENAME = os.path.expanduser("~/.CLOVA_RasPi.keys")

    # コンストラクタ
    def __init__(self) :
        print("Create <KeysSetting> class")

        self.LoadAllKeys()

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <KeysSetting> class")

    # ファイルからキー値を読み取る
    def GetKeyFromFile(self, key_name) :
        with open(self.KEYS_FILENAME, 'r') as file:
            for line in file:
                if line.startswith(key_name + '='):
                    return line[len(key_name)+1:].strip()
        return None

    # 環境変数にキー値を設定する
    def SetKeyToEnv(self, key_name, key_val) :
        if key_val is not None:
            print("SET {}='{}'".format(key_name, ("*"*len(key_val))))
            os.environ[key_name] = key_val
        else :
            print("Err : {} != {}".format(key_name,key_val))

    # 全キーを読み出す
    def LoadAllKeys(self) :
        name = 'GOOGLE_APPLICATION_CREDENTIALS'
        val = self.GetKeyFromFile(name)
        if val is not None :
            self.SetKeyToEnv(name, val)

        name = 'OPENAI_API_KEY'
        val = self.GetKeyFromFile(name)
        if val is not None :
            self.SetKeyToEnv(name, val)

        name = 'VOICE_TEXT_API_KEY'
        val = self.GetKeyFromFile(name)
        if val is not None :
            self.SetKeyToEnv(name, val)

        name = 'WEB_VOICEVOX_API_KEY'
        val = self.GetKeyFromFile(name)
        if val is not None :
            self.SetKeyToEnv(name, val)

        name = 'AITALK_USER'
        val = self.GetKeyFromFile(name)
        if val is not None :
            self.SetKeyToEnv(name, val)

        name = 'AITALK_PASSWORD'
        val = self.GetKeyFromFile(name)
        if val is not None :
            self.SetKeyToEnv(name, val)

        name = 'LINE_CH_ACC_TOKEN'
        val = self.GetKeyFromFile(name)
        if val is not None :
            self.SetKeyToEnv(name, val)

# ==================================
#       設定パラメータ管理クラス
# ==================================
class SysConfig :
    setting = None
    CONFIG_FILENAME = os.path.expanduser("~/.CLOVA_RasPi.cfg")

    # コンストラクタ
    def __init__(self) :
        print("Create <SysConfig> class")
        print("CONFIG_FILENAME={}".format(self.CONFIG_FILENAME))

        self.LoadConfigFile()

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <SysConfig> class")

    # 全設定パラメータを読み取る
    def LoadConfigFile(self) :
        with open(self.CONFIG_FILENAME, 'r', encoding='utf-8') as cfg_file:
            file_text = cfg_file.read()
        self.settings = json.loads(file_text)

    # 全設定パラメータを書き込む
    def SaveConfigFile(self) :
        with open(self.CONFIG_FILENAME, 'w', encoding='utf-8') as cfg_file:
            json.dump(self.settings, cfg_file, indent=2, ensure_ascii=False)


# ==================================
#    Setting HTTPハンドラクラス
# ==================================
class HttpReqSettingHandler(http.server.BaseHTTPRequestHandler) :

    # GETリクエストを受け取った場合の処理
    def do_GET(self):
        sys_config = SysConfig()

        # キャラクタの選択肢を作成する。
        with open(os.path.expanduser("~/CLOVA_RasPi/CLOVA_charactor.json"), 'r', encoding='utf-8') as char_file:
            file_text = char_file.read()
        char_cfg_json = json.loads(file_text)

        char_selection = ""
        index = 0
        for char_data in char_cfg_json["charactors"] :
            line_data = "            <option value=\"{}\">{}</option>\n".format(index, char_data["Name"])
            char_selection += line_data
            index += 1
        #print(char_selection)

        # HTMLファイルを読み込む
        with open(os.path.expanduser("~/CLOVA_RasPi/index.html"), "r", encoding="utf-8") as html_file:
            html = html_file.read()

        html = html.replace("{CharactorSelList}", char_selection)

        # 変数の値をHTMLに埋め込む
        html = html.replace("{DefaultCharSel}", str(sys_config.settings["charactor"]["default_sel"]))
        html = html.replace("{MicChannels}", str(sys_config.settings["hardware"]["audio"]["microphone"]["num_ch"]))
        html = html.replace("{MicIndex}", str(sys_config.settings["hardware"]["audio"]["microphone"]["index"]))
        html = html.replace("{SilentThreshold}", str(sys_config.settings["hardware"]["audio"]["microphone"]["silent_thresh"]))
        html = html.replace("{TerminateSilentDuration}", str(sys_config.settings["hardware"]["audio"]["microphone"]["term_duration"]))
        html = html.replace("{SpeakerChannels}", str(sys_config.settings["hardware"]["audio"]["speaker"]["num_ch"]))
        html = html.replace("{SpeakerIndex}", str(sys_config.settings["hardware"]["audio"]["speaker"]["index"]))
        #print(html) # for debug

        # HTTPレスポンスを返す
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    # POSTリクエストを受け取った場合の処理
    def do_POST(self):
        sys_config = global_config_sys

        # POSTデータを取得する
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        post_data = post_data.decode("utf-8")
        print(post_data)# for debug

        # 変数を更新する
        #global MicChannels, MicIndex, SpeakerChannels, SpeakerIndex
        sys_config.settings["charactor"]["default_sel"] = int(post_data.split("&")[0].split("=")[1])
        sys_config.settings["hardware"]["audio"]["microphone"]["num_ch"] = int(post_data.split("&")[1].split("=")[1])
        sys_config.settings["hardware"]["audio"]["microphone"]["index"] = int(post_data.split("&")[2].split("=")[1])
        sys_config.settings["hardware"]["audio"]["microphone"]["silent_thresh"] = int(post_data.split("&")[3].split("=")[1])
        sys_config.settings["hardware"]["audio"]["microphone"]["term_duration"] = int(post_data.split("&")[4].split("=")[1])
        sys_config.settings["hardware"]["audio"]["speaker"]["num_ch"] = int(post_data.split("&")[5].split("=")[1])
        sys_config.settings["hardware"]["audio"]["speaker"]["index"] = int(post_data.split("&")[6].split("=")[1])

        print("default_char_sel={}".format(sys_config.settings["charactor"]["default_sel"]))
        print("mic num_ch={}".format(sys_config.settings["hardware"]["audio"]["microphone"]["num_ch"]))
        print("mic index={}".format(sys_config.settings["hardware"]["audio"]["microphone"]["index"]))
        print("mic silent_thresh={}".format(sys_config.settings["hardware"]["audio"]["microphone"]["silent_thresh"]))
        print("mic term_duration={}".format(sys_config.settings["hardware"]["audio"]["microphone"]["term_duration"]))
        print("spk num_ch={}".format(sys_config.settings["hardware"]["audio"]["speaker"]["num_ch"]))
        print("spk index={}".format(sys_config.settings["hardware"]["audio"]["speaker"]["index"]))

        sys_config.SaveConfigFile()

        # HTTPレスポンスを返す
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

# ==================================
#      外部参照用のインスタンス
# ==================================
global_config_keys = KeysSetting()
global_config_sys = SysConfig()

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

