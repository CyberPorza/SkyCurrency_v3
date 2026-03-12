import requests
from flask import Flask, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

@app.route('/')
def index():
    # --- Üst Bar Verileri ---
    weather = {"temp": "--", "desc": "Yükleniyor..."}
    try:
        w_res = requests.get("https://wttr.in/Istanbul?format=j1", timeout=10).json()
        curr = w_res['current_condition'][0]
        weather = {"temp": curr['temp_C'], "desc": curr.get('lang_tr', [{'value': curr['weatherDesc'][0]['value']}])[0]['value']}
    except: pass

    # --- Döviz Listesi ---
    currencies = []
    names = {
        'USD': 'Amerikan Doları', 'EUR': 'Avrupa Para Birimi', 
        'GBP': 'İngiliz Sterlini', 'CHF': 'İsviçre Frangı', 
        'JPY': 'Japon Yeni', 'CAD': 'Kanada Doları'
    }
    try:
        c_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10).json()
        base_try = c_res['rates']['TRY']
        for code, full_name in names.items():
            rate = c_res['rates'].get(code, 1)
            val = round(base_try / rate, 2)
            currencies.append({'code': f"{code}/TRY", 'name': full_name, 'val': val})
    except: pass

    # --- GARANTİ ALTIN LİSTESİ ---
    gold_list = []
    # Doviz.com'daki en popüler altınların anahtarları
    gold_keys = {
        "Gram Altın": "gram-altin",
        "Çeyrek Altın": "ceyrek-altin",
        "Yarım Altın": "yarim-altin",
        "Tam Altın": "tam-altin",
        "Cumhuriyet": "cumhuriyet-altini",
        "Reşat Altın": "resat-altin"
    }
    
    try:
        # Altın verilerini daha geniş bir sayfadan çekiyoruz
        res = requests.get("https://www.doviz.com/altin", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        for full_name, key in gold_keys.items():
            # Sitedeki her altının fiyatı 'data-socket-key' içinde saklanır
            tag = soup.find("td", {"data-socket-key": key, "data-socket-attr": "s"})
            if not tag: # Eğer td içinde bulamazsa span içinde ara
                tag = soup.find("span", {"data-socket-key": key})
            
            price = tag.text.strip() if tag else "N/A"
            gold_list.append({'name': full_name, 'val': price})
    except Exception as e:
        print(f"Altın Hatası: {e}")
        # Hata anında listeyi boş bırakma, N/A doldur
        if not gold_list:
            for name in gold_keys.keys():
                gold_list.append({'name': name, 'val': "N/A"})

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold_list)

if __name__ == "__main__":
    app.run(debug=True)
