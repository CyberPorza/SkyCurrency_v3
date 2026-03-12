import requests
from flask import Flask, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

@app.route('/')
def index():
    # --- HAVA DURUMU (ÜST BAR) ---
    weather = {"temp": "--", "desc": "Yükleniyor..."}
    try:
        w_res = requests.get("https://wttr.in/Istanbul?format=j1", timeout=10).json()
        curr = w_res['current_condition'][0]
        weather = {
            "temp": curr['temp_C'], 
            "desc": curr.get('lang_tr', [{'value': curr['weatherDesc'][0]['value']}])[0]['value']
        }
    except: pass

    # --- TÜM PARA BİRİMLERİ ---
    currencies = {}
    try:
        c_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10).json()
        base_try = c_res['rates']['TRY']
        # Takip edilecek pariteler
        targets = ['USD', 'EUR', 'GBP', 'CHF', 'JPY', 'CAD']
        for t in targets:
            rate_to_usd = c_res['rates'].get(t, 1)
            currencies[t] = round(base_try / rate_to_usd, 2)
    except: pass

    # --- DETAYLI ALTIN VERİLERİ (SCRAPING) ---
    gold_data = {"Gram": "N/A", "Ceyrek": "N/A", "Yarim": "N/A", "Tam": "N/A"}
    try:
        res = requests.get("https://www.doviz.com/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        gold_keys = {
            "Gram": "gram-altin",
            "Ceyrek": "ceyrek-altin",
            "Yarim": "yarim-altin",
            "Tam": "tam-altin"
        }
        for name, key in gold_keys.items():
            tag = soup.find("span", {"data-socket-key": key})
            if tag: gold_data[name] = tag.text.strip()
    except: pass

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold_data)

if __name__ == "__main__":
    app.run(debug=True)
