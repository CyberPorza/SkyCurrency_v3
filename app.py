import requests
from flask import Flask, render_template

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

@app.route('/')
def index():
    # Başlangıçta boş listeler oluşturuyoruz ki HTML patlamasın
    weather = {"temp": "0", "desc": "Sistem Hazırlanıyor"}
    currencies = []
    gold_list = []

    # 1. HAVA DURUMU
    try:
        w_res = requests.get("https://wttr.in/Istanbul?format=j1", timeout=5).json()
        curr = w_res['current_condition'][0]
        weather = {"temp": curr['temp_C'], "desc": curr.get('lang_tr', [{'value': curr['weatherDesc'][0]['value']}])[0]['value']}
    except Exception as e:
        print(f"Hava Durumu Hatası: {e}")

    # 2. DÖVİZ
    try:
        c_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
        base_try = c_res['rates']['TRY']
        names = {'USD': 'Amerikan Doları', 'EUR': 'Euro', 'GBP': 'İngiliz Sterlini'}
        for code, full_name in names.items():
            rate = c_res['rates'].get(code, 1)
            currencies.append({'code': f"{code}/TRY", 'name': full_name, 'val': round(base_try / rate, 2)})
    except Exception as e:
        print(f"Döviz Hatası: {e}")

    # 3. ALTIN (Farklı Bir API - Garanti)
    try:
        # genelpara bazen bloklayabilir, alternatif bir kaynak deniyoruz
        g_res = requests.get("https://api.genelpara.com/embed/para-birimleri.json", timeout=5).json()
        mapping = {"GA": "Gram Altın", "C": "Çeyrek Altın", "Y": "Yarım Altın", "T": "Tam Altın"}
        for key, name in mapping.items():
            val = g_res.get(key, {}).get('satis', "0.00")
            gold_list.append({'name': name, 'val': val})
    except Exception as e:
        print(f"Altın Hatası: {e}")
        # Boş kalmasın diye N/A doldur
        if not gold_list:
            gold_list = [{'name': "Gram Altın", "val": "Bağlantı Yok"}]

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold_list)

if __name__ == "__main__":
    app.run(debug=True)
