import requests
from flask import Flask, render_template

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

    # --- Döviz Listesi ---
    currencies = []
    names = {'USD': 'Amerikan Doları', 'EUR': 'Euro', 'GBP': 'İngiliz Sterlini', 'CHF': 'İsviçre Frangı', 'CAD': 'Kanada Doları'}
    try:
        c_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10).json()
        base_try = c_res['rates']['TRY']
        for code, full_name in names.items():
            rate = c_res['rates'].get(code, 1)
            val = round(base_try / rate, 2)
            currencies.append({'code': f"{code}/TRY", 'name': full_name, 'val': val})
    except: pass

    # --- ALTIN MOTORU (PROFESYONEL JSON ENDPOINT) ---
    gold_list = []
    try:
        # Doğrudan canlı piyasa verisi veren bir endpoint kullanıyoruz (Scraping değil, Veri Akışı)
        gold_res = requests.get("https://api.genelpara.com/embed/para-birimleri.json", timeout=10).json()
        
        gold_mapping = {
            "GA": "Gram Altın",
            "C": "Çeyrek Altın",
            "Y": "Yarım Altın",
            "T": "Tam Altın",
            "CUM": "Cumhuriyet",
            "ATA": "Ata Altın"
        }
        
        for key, name in gold_mapping.items():
            # genelpara verisi satış fiyatını 's' anahtarında tutar
            price = gold_res.get(key, {}).get('satis', "N/A")
            gold_list.append({'name': name, 'val': price})
            
    except Exception as e:
        print(f"Altın Veri Akışı Hatası: {e}")
        # Yedekleme (Eğer yukarıdaki API çökerse boş kalmasın)
        gold_list = [{'name': k, 'val': "Bağlantı Hatası"} for k in ["Gram Altın", "Çeyrek Altın", "Yarım Altın", "Tam Altın", "Cumhuriyet", "Ata Altın"]]

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold_list)

if __name__ == "__main__":
    app.run(debug=True)
