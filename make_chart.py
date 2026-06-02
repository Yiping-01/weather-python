import requests
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Windows 中文字型
matplotlib.rcParams["font.family"] = "Microsoft JhengHei"
matplotlib.rcParams["axes.unicode_minus"] = False

API_KEY = "CWA-C00C85F2-5345-4447-B50A-7EB2396408A1"
API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"


def get_first_value(element_value):
    if not element_value:
        return ""

    first_item = element_value[0]

    if not first_item:
        return ""

    return list(first_item.values())[0]


def find_locations(obj, locations=None):
    if locations is None:
        locations = []

    if isinstance(obj, list):
        for item in obj:
            find_locations(item, locations)

    elif isinstance(obj, dict):
        if "LocationName" in obj and "WeatherElement" in obj:
            locations.append(obj)

        for value in obj.values():
            find_locations(value, locations)

    return locations


def parse_weather(location):
    result = {}

    for element in location["WeatherElement"]:
        element_name = element["ElementName"]

        for time_data in element["Time"]:
            start_time = time_data["StartTime"]
            end_time = time_data["EndTime"]
            key = (start_time, end_time)

            if key not in result:
                result[key] = {
                    "startTime": start_time,
                    "endTime": end_time,
                    "weather": "",
                    "maxTemp": "",
                    "minTemp": "",
                    "pop": "",
                    "description": ""
                }

            value = get_first_value(time_data["ElementValue"])

            if element_name == "天氣現象":
                result[key]["weather"] = value
            elif element_name == "最高溫度":
                result[key]["maxTemp"] = value
            elif element_name == "最低溫度":
                result[key]["minTemp"] = value
            elif element_name == "12小時降雨機率":
                result[key]["pop"] = value
            elif element_name == "天氣預報綜合描述":
                result[key]["description"] = value

    return list(result.values())


def short_label(date_string):
    from datetime import datetime

    date = datetime.fromisoformat(date_string)
    week = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    period = "白天" if date.hour < 12 else "晚上"

    return week[date.weekday()] + period


def make_chart(city="桃園市"):
    params = {
        "Authorization": API_KEY,
        "format": "JSON",
        "sort": "time"
    }

    response = requests.get(API_URL, params=params, verify=False)
    data = response.json()

    locations = find_locations(data)

    target = None

    for location in locations:
        if location["LocationName"] == city:
            target = location
            break

    if target is None:
        print(f"找不到地點：{city}")
        return

    weather_data = parse_weather(target)
    first_seven = weather_data[:7]

    labels = [short_label(item["startTime"]) for item in first_seven]

    max_temps = [
        int(item["maxTemp"]) if item["maxTemp"] else 0
        for item in first_seven
    ]

    rain_pops = [
        0 if item["pop"] == "-" or item["pop"] == "" else int(item["pop"])
        for item in first_seven
    ]

    x = np.arange(len(labels))

    fig, ax1 = plt.subplots(figsize=(8, 4.2))

    # 白底
    fig.patch.set_facecolor("white")
    ax1.set_facecolor("white")

    # 右側 Y 軸
    ax2 = ax1.twinx()

    # 最高溫度：粉紅色
    line1 = ax1.plot(
        x,
        max_temps,
        color="#ff7f8a",
        marker="o",
        linewidth=3,
        markersize=7,
        label="最高溫度 °C"
    )

    # 降雨機率：藍色
    line2 = ax2.plot(
        x,
        rain_pops,
        color="#5dade2",
        marker="o",
        linewidth=3,
        markersize=7,
        label="降雨機率 %"
    )

    # X 軸
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=25, ha="right")

    # Y 軸標籤
    ax1.set_ylabel("溫度 °C", color="#666666")
    ax2.set_ylabel("降雨機率 %", color="#666666")

    # Y 軸範圍
    ax1.set_ylim(min(max_temps) - 2, max(max_temps) + 2)
    ax2.set_ylim(0, 100)

    # 格線
    ax1.grid(True, color="#cccccc", alpha=0.45)

    # 邊框淡一點
    for spine in ax1.spines.values():
        spine.set_color("#dddddd")

    for spine in ax2.spines.values():
        spine.set_color("#dddddd")

    ax1.tick_params(colors="#666666")
    ax2.tick_params(colors="#666666")

    # 圖例放上方
    lines = line1 + line2
    labels_legend = [line.get_label() for line in lines]

    ax1.legend(
        lines,
        labels_legend,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=2,
        frameon=False,
        fontsize=12
    )

    plt.tight_layout()

    # 存成白底圖片
    file_name = f"chart_{city}.png"
    plt.savefig(file_name, dpi=160, facecolor="white", bbox_inches="tight")
    plt.close()

    print(f"已產生 {file_name}")


if __name__ == "__main__":
    cities = [
        "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
        "基隆市", "新竹縣", "新竹市", "苗栗縣", "彰化縣", "南投縣",
        "雲林縣", "嘉義縣", "嘉義市", "屏東縣", "宜蘭縣", "花蓮縣",
        "臺東縣", "澎湖縣", "金門縣", "連江縣"
    ]

    for city in cities:
        make_chart(city)