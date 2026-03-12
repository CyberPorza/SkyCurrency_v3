import requests
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # 1. Varsayılan (Fallback) Veriler - API patlasa bile uygulama çalışır
    weather_data = {"temp": "0", "desc": "Veri Alınamadı"}
    currency_list = [
        {'code': 'USD/TRY', 'name': 'Amerikan Doları', 'val': '0.00'},
        {'code': 'EUR/TRY', 'name': 'Euro', 'val': '0.00'},
        {'code': 'GBP/TRY', 'name': 'İngiliz Sterlini', 'val': '0.00'}
    ]
    gold_data = [
        {'name': 'Gram Altın', 'val': '0.00'},
        {'name': 'Çeyrek Altın', 'val': '0.00'},
        {'name': 'Yarım Altın', 'val': '0.00'},
        {'name': 'Tam Altın', 'val': '0.00'}
    ]

    # 2. Hava Durumu Çekme
    try:
        w_res = requests.get("https://wttr.in/Istanbul?format=j1", timeout=5).json()
        weather_data['temp'] = w_res['current_condition'][0]['temp_C']
        weather_data['desc'] = w_res['current_condition'][0]['lang_tr'][0]['value']
    except:
        pass

    # 3. Döviz Çekme
    try:
        c_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
        usd_try = c_res['rates']['TRY']
        currency_list[0]['val'] = round(usd_try, 2)
        currency_list[1]['val'] = round(usd_try / c_res['rates']['EUR'], 2)
        currency_list[2]['val'] = round(usd_try / c_res['rates']['GBP'], 2)
    except:
        pass

    # 4. Altın Çekme (GenelPara API)
    try:
        g_res = requests.get("https://api.genelpara.com/embed/para-birimleri.json", timeout=5).json()
        gold_mapping = {"GA": 0, "C": 1, "Y": 2, "T": 3}
        for api_key, index_no in gold_mapping.items():
            if api_key in g_res:
                gold_data[index_no]['val'] = g_res[api_key]['satis']
    except:
        pass

    return render_template('index.html', weather=weather_data, currencies=currency_list, gold=gold_data)

if __name__ == "__main__":
    app.run(debug=True)
