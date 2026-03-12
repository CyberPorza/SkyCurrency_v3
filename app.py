import requests
from flask import Flask, render_template

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

@app.route('/')
def index():
    # --- 1. HAVA DURUMU ---
    weather = {"temp": "0", "desc": "Yükleniyor"}
    try:
        w_res = requests.get("https://wttr.in/Istanbul?format=j1", timeout=5).json()
        weather['temp'] = w_res['current_condition'][0]['temp_C']
        weather['desc'] = w_res['current_condition'][0]['lang_tr'][0]['value']
    except: pass

    # --- 2. DÖVİZ KURLARI ---
    currencies = []
    try:
        c_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
        usd_val = c_res['rates']['TRY']
        curr_map = {'USD': 'Amerikan Doları', 'EUR': 'Euro', 'GBP': 'İngiliz Sterlini', 'CHF': 'İsviçre Frangı', 'CAD': 'Kanada Doları'}
        for code, name in curr_map.items():
            rate = c_res['rates'].get(code, 1)
            currencies.append({'code': f"{code}/TRY", 'name': name, 'val': round(usd_val / rate, 2)})
    except: pass

    # --- 3. ALTIN PİYASASI (JSON ENDPOINT) ---
    gold = []
    try:
        g_res = requests.get("https://api.genelpara.com/embed/para-birimleri.json", timeout=5).json()
        gold_map = {"GA": "Gram Altın", "C": "Çeyrek Altın", "Y": "Yarım Altın", "T": "Tam Altın", "CUM": "Cumhuriyet", "ATA": "Ata Altın"}
        for key, name in gold_map.items():
            if key in g_res:
                gold.append({'name': name, 'val': g_res[key]['satis']})
    except: pass

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold)

if __name__ == "__main__":
    app.run(debug=True)
