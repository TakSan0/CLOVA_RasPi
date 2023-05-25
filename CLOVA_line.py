import os
import os.path
import re
import http.server
import json
import requests
import urllib.parse
import urllib.request

from CLOVA_queue import global_speech_queue
from CLOVA_config import global_config_sys

speech_queue = None
# ==================================
#           LINE受信クラス
# ==================================
class LineReciever :
    # コンストラクタ
    def __init__(self) :
        # 現状ログ出すだけ
        print("Create <LineReciever> class")

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <LineReciever> class")

    def conv_id_to_call_name(self, id) :
        # 未サポート（やり方調査中）
        print("ID:{} の名前を取得できませんでした。".format(self.json_data["events"][0]["message"]["id"]))
        return "誰か"

    # 受信時処理
    def on_message_recv(self, body, query_data) :
        # 取得データを展開
        print ("POST body=")
        print (body)
        print ("POST query_data=")
        print (query_data)

        # ボディー部分の JSonを取り出す
        self.json_data = json.loads(body)
        print ("Json=")
        print (self.json_data)

        # IDをハンドル名に変換
        sender = self.conv_id_to_call_name(self.json_data["events"][0]["message"]["id"])

        # ライン受信をまず通知
        sender_read = "{} さんから次のラインメッセージが届きました。".format(sender)
        global_speech_queue.add(sender_read)
        print("From>'{}'".format(sender_read))

        # メッセージを取得
        line_str = self.json_data["events"][0]["message"]["text"]
        print ("LINE Message=")
        print(line_str)

        # メッセージ読み上げ
        message_list = line_str.splitlines()
        #print ("LINE message=")
        for message in message_list:
            global_speech_queue.add(message)
            print("Send>'{}'".format(message))

# ==================================
#           LINE送信クラス
# ==================================
class LineSender :
    POST_URL = "https://api.line.me/v2/bot/message/push"
    request_header = {"Content-Type": "application/json",  "Authorization": "Bearer channel_access_token"}
    request_body = {"to": "user ID", "messages": [{"type": "text", "text": "Message to send" }]}

    # コンストラクタ
    def __init__(self) :
        # 現状ログ出すだけ
        print("Create <LineSender> class")
        self.ACCESS_TOKEN = os.environ["LINE_CH_ACC_TOKEN"]

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <LineSender> class")

    # メッセージ送信
    def send_message(self, to_id, message) :
        # データをセット
        self.request_body["to"] = to_id
        self.request_body["messages"][0]["text"] = message
        self.request_header["Authorization"] = "Bearer {}".format(self.ACCESS_TOKEN)

        # print("HEADER:")
        # print(self.request_header)
        # print("BODY:")
        # print(self.request_body)

        # メッセージの送信
        response = requests.post(self.POST_URL, headers = self.request_header, json=self.request_body)

    def conv_call_name_to_id(self, call_name) :
        found_id = ""
        default_id = ""

        for id_inf in global_config_sys.settings["sns"]["line"]["user_id"] :
            if (id_inf["name"] == "default" ) :
                default_id = id_inf["id"]
            elif (id_inf["callname"] == call_name ) :
                found_id = id_inf["id"]

        if (found_id == "") :
            print("呼び名:{} のIDを取得できませんでした。デフォルトのIDを使用します。")
            found_id = default_id

        return found_id

    def try_get_answer(self, request_text):
        if ( ( ("LINE" in request_text) or ("ライン" in request_text) ) and ( ("送信して" in request_text) or ("送って" in request_text) or  ("して" in request_text) ) ) :
            name_str = request_text.split("に")[0]

            # 正規表現パターンを定義
            # TODO: check `U+3000` is correct or not; probably not right
            pattern = r"^(?P<name_str>.+?)[ 　]*に[ 　]*(?P<message>.+?)\s*([と|って]+[ 　]*[ライン|LINE]+[ 　]*[して|を送って|送って|送信して]+)[。]*$"

            # 正規表現によるマッチング
            match = re.match(pattern, request_text)

            if match:
                # マッチした場合、name_str と Message 変数に格納
                name_str = match.group("name_str")
                message = match.group("message")
                print("name_str: {}".format(name_str))
                print("Message: {}".format(message))

                # メッセージ送信
                id = self.conv_call_name_to_id(name_str)
                print("Send[LINE]>Id:{},Msg:{}".format(id, message))
                self.send_message(id, message)

                answer_text = "{} に {} とラインメッセージ送りました".format(name_str, message)
                return answer_text

            else :
                # 該当がない場合は空で返信
                answer_text = "メッセージを解釈できませんでした。"
                print(answer_text)
                return answer_text

        else:
            # 該当がない場合は空で返信
            print("No Keyword for Weather")
            self._news_count = 0
            return ""


# ==================================
#      LINE HTTPハンドラクラス
# ==================================
class HttpReqLineHandler(http.server.BaseHTTPRequestHandler) :
    line_recv = LineReciever()

    def do_POST(self):
        body = self.rfile.read( int(self.headers.get("Content-Length") ) )
        query_data = urllib.parse.parse_qs( body.decode(encoding="utf8",errors="replace") )

        self.line_recv.on_message_recv(body, query_data)

# ==================================
#       本クラスのテスト用処理
# ==================================
def module_test() :
    # APIキー類の読み込み
    sender = LineSender()
    ret = sender.try_get_answer("クローバに おはようございます！ って LINE して。")
    print(ret)

# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    module_test()

