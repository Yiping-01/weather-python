from flask import Flask, jsonify
from flask_cors import CORS
import requests
import urllib3

# 關閉 SSL 安全警告（因為 verify=False）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
# 啟用 CORS 允許前端 HTML 網頁跨來源存取這個 Python 服務
CORS(app)

# 政府氣象署 API 設定（安全地保留在後端）
API_KEY = "CWA-A369996B-2E49-49D7-AE5C-FDAC712BB9FC"
API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"


@app.route("/api/get-cwa-weather", methods=["GET"])
def get_cwa_weather():
    """由 Python 負責串接政府 Open Data API"""
    params = {"Authorization": API_KEY, "format": "JSON", "sort": "time"}

    try:
        # Python 執行網路連線要求
        response = requests.get(API_URL, params=params, verify=False)

        if response.status_code == 200:
            # 將政府回傳的原始天氣 JSON 資料，直接轉手送給前端網頁
            return jsonify(response.json())
        else:
            return (
                jsonify(
                    {"error": f"政府 API 連線失敗，狀態碼：{response.status_code}"}
                ),
                response.status_code,
            )

    except Exception as e:
        return jsonify({"error": f"Python 後端發生錯誤：{str(e)}"}), 500


if __name__ == "__main__":
    # 啟動本地伺服器，預設網址為 http://127.0.0.1:5000
    app.run(debug=True, port=5000)