import re
import requests
import datetime

from clova.processor.skill.base_skill import BaseSkillProvider
from clova.general.logger import BaseLogger
from clova.config.config import global_config_prov

# 大阪市のコード
code = "270000"

# ==================================
#            天気クラス
# ==================================
# 主要地方・都市のエリアコードのテーブル
area_codes = {
    "宗谷": "011000",
    "上川": "012000",
    "留萌": "012000",
    "網走": "013000",
    "北見": "013000",
    "紋別": "013000",
    "十勝": "014030",
    "釧路": "014100",
    "根室": "014100",
    "胆振": "015000",
    "日高": "015000",
    "石狩": "016000",
    "空知": "016000",
    "後志": "016000",
    "渡島": "017000",
    "檜山": "017000",
    "青森": "020000",
    "岩手": "030000",
    "宮城": "040000",
    "秋田": "050000",
    "山形": "060000",
    "福島": "070000",
    "茨城": "080000",
    "栃木": "090000",
    "群馬": "100000",
    "埼玉": "110000",
    "千葉": "120000",
    "東京": "130000",
    "神奈川": "140000",
    "新潟": "150000",
    "富山": "160000",
    "石川": "170000",
    "福井": "180000",
    "山梨": "190000",
    "長野": "200000",
    "岐阜": "210000",
    "静岡": "220000",
    "愛知": "230000",
    "三重": "240000",
    "滋賀": "250000",
    "京都": "260000",
    "大阪": "270000",
    "兵庫": "280000",
    "奈良": "290000",
    "和歌山": "300000",
    "鳥取": "310000",
    "島根": "320000",
    "岡山": "330000",
    "広島": "340000",
    "山口": "350000",
    "徳島": "360000",
    "香川": "370000",
    "愛媛": "380000",
    "高知": "390000",
    "福岡": "400000",
    "佐賀": "410000",
    "長崎": "420000",
    "熊本": "430000",
    "大分": "440000",
    "宮崎": "450000",
    "奄美地方": "460040",
    "鹿児島": "460100",
    "沖縄本島": "471000",
    "大東島": "472000",
    "宮古島": "473000",
    "八重山": "474000",
}


class WeatherSkillProvider(BaseSkillProvider, BaseLogger):
    # コンストラクタ
    def __init__(self):
        super().__init__()

        pass

    # デストラクタ
    def __del__(self):
        super().__del__()

    # 天気 質問に答える。天気の問い合わせではなければ None を返す
    def try_get_answer(self, request_text):
        if (("天気を教えて" in request_text) or ("天気は" in request_text)):
            # 天気情報を取得する日付のデフォルト値(今日の日付文字列)
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            date = "きょう"

            # 明日か明後日かの場合はその日付文字列を取得する
            match = re.search("(明日|あした|明後日|あさって)", request_text)
            if match:
                if match.group(1) in ["明日", "あした"]:
                    date_str = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                    date = "あした"
                else:
                    date_str = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                    date = "あさって"

            # 都市名を取得し、エリアコードを取得する
            for area in area_codes.keys():
                if area in request_text:
                    code = area_codes[area]
                    break

            # 都市名が見つからない場合は空で返す
            else:
                answer_text = "エリア名が不明です。天気を取得したいエリアを指定してください"
                self.log("try_get_answer", answer_text)
                return answer_text

            # APIから天気情報を取得する
            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
            self.log("try_get_answer", "URL={}".format(url))
            response = requests.get(url)
            weather_data = response.json()

            if global_config_prov.verbose():
                self.log("try_get_answer", "weather_data = {}".format(weather_data))
                self.log("try_get_answer", weather_data[0]["timeSeries"][0]["timeDefines"])

            # 取得JSONから日付を検索
            idx = 0
            for time_define in weather_data[0]["timeSeries"][0]["timeDefines"]:
                # 指定日の文字列を含む日時定義を検索し一致したら、そのインデックス値の天気を出力する
                if (date_str in time_define):
                    weather_text = "{} {} の {} の天気は{} です。".format(date, date_str, area, weather_data[0]["timeSeries"][0]["areas"][0]["weathers"][idx])

                    self.log("try_get_answer", weather_text)
                    return weather_text
                idx += 1

            # 該当がない場合は空で返信
            answer_text = "天気データが取得できませんでした。"
            self.log("try_get_answer", answer_text)
            return answer_text

        else:
            # 該当がない場合は空で返信
            self.log("try_get_answer", "No Keyword for Weather")
            return None

    def print_areas(self):
        response = requests.get("https://www.jma.go.jp/bosai/common/const/area.json")
        response_data = response.json()
        for code in response_data["centers"]:
            self.log("print_areas", "    '{}': '{}'".format(response_data["centers"][code]["name"], code))

        self.log("print_areas", "")
        for code in response_data["offices"]:
            self.log("print_areas", "    '{}': '{}',".format(response_data["offices"][code]["name"], code))

# ==================================
#       本クラスのテスト用処理
# ==================================


def module_test():
    weather = WeatherSkillProvider()
    # weather.PrintAreas()
    weather.try_get_answer("明日の東京の天気を教えて")


# ==================================
# 本モジュールを直接呼出した時の処理
# ==================================
if __name__ == "__main__":
    # 直接呼び出したときは、モジュールテストを実行する。
    module_test()
