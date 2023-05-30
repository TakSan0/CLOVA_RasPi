import socketserver
import threading as th
from clova.processor.skill.line import HttpReqLineHandler
from clova.general.logger import BaseLogger

# ==================================
#       HTTPサーバークラス
# ==================================


class HttpServer(BaseLogger):
    # コンストラクタ
    def __init__(self, port, handler):
        self._port = port
        self._handler = handler
        th.Thread(target=self.serve, args=(), name="HttpServerProcess", daemon=True).start()

    # デストラクタ
    def __del__(self):
        super().__del__()

        self.httpd.shutdown()

    # HTTPサーバーのメイン処理：起動したあとは、MyHandler で待ち受けているだけ
    def serve(self):
        # 8080 番ポートで受け付ける
        self.httpd = socketserver.TCPServer(("", self._port), self._handler)
        self.httpd.serve_forever()
        print("End server")

# ==================================
#       本クラスのテスト用処理
# ==================================


def module_test():
    # インスタンス作成
    HttpServer(8080, HttpReqLineHandler)

    input()


# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    module_test()
