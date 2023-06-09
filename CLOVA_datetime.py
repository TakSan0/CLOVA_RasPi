import datetime
import re

# ==================================
#             日時クラス
# ==================================
# 日時クラス
class DateTime :
    weekday_dict = {'Mon': '月', 'Tue': '火', 'Wed': '水', 'Thu': '木', 'Fri': '金', 'Sat': '土', 'Sun': '日'}

    # コンストラクタ
    def __init__(self) :
        # 現状ログ出すだけ
        print("Create <DateTime> class")

    # デストラクタ
    def __del__(self) :
        # 現状ログ出すだけ
        print("Delete <DateTime> class")

    # 日時 質問に答える。日時の問い合わせではなければ 空 の文字列を返す
    def GetAnswerIfTextIsRequestDateTime(self, request_string) :
        if ('今' in request_string ) and ('何' in request_string) and ( ( '日' in request_string) or ( '時' in request_string) ) :
            if ("今何時" in request_string) :
                now = datetime.datetime.now()
                answer_text = '今は{0}時{1}分{2}秒です'.format(now.hour, now.minute, now.second)
                print(now)
                return answer_text

            elif ("何日" in request_string) :
                now = datetime.datetime.now()
                answer_text = '今日は{0}年{1}月{2}日{3}曜日です'.format(now.year, now.month, now.day, self.weekday_dict[now.strftime('%a')])
                print(now)
                return answer_text

        # 該当がない場合は空で返信
        return ("")

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

