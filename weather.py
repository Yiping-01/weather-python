import requests
import pandas as pd
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "CWA-C00C85F2-5345-4447-B50A-7EB2396408A1"
API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"


def find_locations(obj):
    """
    遞迴尋找 API 回傳資料裡的 Location 清單
    只要裡面有 LocationName 和 WeatherElement，就把它抓出來
    """
    locations = []

    if isinstance(obj, dict):
        if "LocationName" in obj and "WeatherElement" in obj:
            locations.append(obj)

        for value in obj.values():
            locations.extend(find_locations(value))

    elif isinstance(obj, list):
        for item in obj:
            locations.extend(find_locations(item))

    return locations


def get_first_value(element_value):
    if not element_value:
        return ""

    first_item = element_value[0]

    if not first_item:
        return ""

    return list(first_item.values())[0]


def get_weather(location_name="臺北市"):
    params = {
        "Authorization": API_KEY,
        "format": "JSON",
        "sort": "time"
    }

    try:
        response = requests.get(API_URL, params=params, verify=False)
    except requests.exceptions.RequestException as e:
        print("連線失敗：")
        print(e)
        return

    if response.status_code != 200:
        print("API 連線失敗，狀態碼：", response.status_code)
        print(response.text)
        return

    try:
        data = response.json()
    except ValueError:
        print("API 回傳不是 JSON 格式")
        print(response.text)
        return

    locations = find_locations(data)

    if not locations:
        print("沒有找到任何縣市天氣資料。")
        return

    target_location = None

    for location in locations:
        if location.get("LocationName") == location_name:
            target_location = location
            break

    if target_location is None:
        print(f"找不到地點：{location_name}")
        print("目前 API 有這些地點：")
        for location in locations:
            print(location.get("LocationName"))
        return

    result = {}

    for element in target_location["WeatherElement"]:
        element_name = element["ElementName"]

        for time_data in element["Time"]:
            start_time = time_data["StartTime"]
            end_time = time_data["EndTime"]
            key = (start_time, end_time)

            if key not in result:
                result[key] = {
                    "開始時間": start_time,
                    "結束時間": end_time,
                    "天氣狀況": "",
                    "最高溫": "",
                    "最低溫": "",
                    "降雨機率": "",
                    "天氣描述": ""
                }

            value = get_first_value(time_data["ElementValue"])

            if element_name == "天氣現象":
                result[key]["天氣狀況"] = value

            elif element_name == "最高溫度":
                result[key]["最高溫"] = value + "°C"

            elif element_name == "最低溫度":
                result[key]["最低溫"] = value + "°C"

            elif element_name == "12小時降雨機率":
                if value == "-":
                    result[key]["降雨機率"] = "-"
                else:
                    result[key]["降雨機率"] = value + "%"

            elif element_name == "天氣預報綜合描述":
                result[key]["天氣描述"] = value

    df = pd.DataFrame(result.values())

    print(f"\n{location_name} 未來七天天氣預報：\n")
    print(df.to_string(index=False))

    file_name = f"{location_name}_未來七天天氣預報.csv"
    df.to_csv(file_name, index=False, encoding="utf-8-sig")

    print(f"\n已儲存成：{file_name}")


if __name__ == "__main__":
    city = input("請輸入縣市名稱，例如 臺北市：").strip()

    if city == "":
        city = "臺北市"

    get_weather(city)