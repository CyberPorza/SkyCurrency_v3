import requests
from flask import Flask, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

@app.route('/')
def index():
    # --- Hava Durumu ---
    weather = {"temp": "--", "desc": "Yükleniyor..."}
    try:
        w_res = requests.get("https://wttr.in/Istanbul?format=j1", timeout=10).json()
        curr = w_res['current_condition'][0]
        weather = {"temp": curr['temp_C'], "desc": curr.get('lang_tr', [{'value': curr['weatherDesc'][0]['value']}])[0]['value']}
    except: pass

    # --- Döviz Listesi (Türkçe) ---
    currencies = []
    names = {
        'USD': 'Amerikan Doları', 'EUR': 'Euro', 
        'GBP': 'İngiliz Sterlini', 'CHF': 'İsviçre Frangı', 
        'CAD': 'Kanada Doları'
    }
    try:
        c_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10).json()
        base_try = c_res['rates']['TRY']
        for code, full_name in names.items():
            rate = c_res['rates'].get(code, 1)
            val = round(base_try / rate, 2)
            currencies.append({'code': f"{code}/TRY", 'name': full_name, 'val': val})
    except: pass

    # --- ALTIN MOTORU (HAREM ALTIN - GARANTİ) ---
    gold_list = []
    try:
        # Harem Altın anlık verileri çok nettir
        res = requests.get("https://www.haremaltin.com/canli-piyasalar/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Sitedeki fiyatları yakalamak için hedef ID'ler
        # Gram: ga, Ceyrek: c, Yarim: y, Tam: t, Cumhuriyet: cm, Ata: a
        targets = {
            "Gram Altın": "ga_satis",
            "Çeyrek Altın": "ceyrek_satis",
            "Yarım Altın": "yarim_satis",
            "Tam Altın": "tam_satis",
            "Cumhuriyet": "cumhuriyet_satis",
            "Ata Altın": "ata_satis"
        }
        
        for name, element_id in targets.items():
            tag = soup.find("span", {"id": element_id})
            price = tag.text.strip() if tag else "N/A"
            gold_list.append({'name': name, 'val': price})
            
    except:
        # Hata anında fallback (Doviz.com yedeği)
        try:
            res = requests.get("https://www.doviz.com/altin", headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            keys = {"Gram Altın": "gram-altin", "Çeyrek Altın": "ceyrek-altin", "Yarım Altın": "yarim-altin"}
            for name, key in keys.items():
                tag = soup.find("span", {"data-socket-key": key})
                gold_list.append({'name': name, 'val': tag.text.strip() if tag else "N/A"})
        except: pass

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold_list)

if __name__ == "__main__":
    app.run(debug=True)
