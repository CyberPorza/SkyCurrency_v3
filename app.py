import requests
from flask import Flask, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

# Tarayıcı gibi görünmek için Header
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

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
        # Takip etmek istediğimiz birimler ve Türkçe karşılıkları
        curr_map = {
            'USD': 'Amerikan Doları', 
            'EUR': 'Euro', 
            'GBP': 'İngiliz Sterlini', 
            'CHF': 'İsviçre Frangı', 
            'CAD': 'Kanada Doları'
        }
        for code, name in curr_map.items():
            rate = c_res['rates'].get(code, 1)
            currencies.append({
                'code': f"{code}/TRY", 
                'name': name, 
                'val': round(usd_val / rate, 2)
            })
    except: pass

    # --- 3. ALTIN PİYASASI (Garantili Kazıma) ---
    gold = []
    try:
        # Doviz.com'un altın sayfası statik veriler için en iyisidir
        res_altin = requests.get("https://www.doviz.com/altin", headers=HEADERS, timeout=10)
        soup_altin = BeautifulSoup(res_altin.text, "html.parser")
        
        # HTML içindeki data-socket-key değerlerini yakalıyoruz
        mapping = {
            "Gram Altın": "gram-altin", 
            "Çeyrek Altın": "ceyrek-altin", 
            "Yarım Altın": "yarim-altin", 
            "Tam Altın": "tam-altin",
            "Cumhuriyet": "cumhuriyet-altini",
            "Ata Altın": "ata-altin"
        }
        
        for name, key in mapping.items():
            tag = soup_altin.find("span", {"data-socket-key": key})
            val = tag.text.strip() if tag else "N/A"
            gold.append({'name': name, 'val': val})
    except Exception as e:
        print(f"Altın Hatası: {e}")
        # Hata durumunda boş kalmasın
        if not gold:
            gold = [{'name': "Hata", 'val': "Bağlantı Yok"}]

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold)

if __name__ == "__main__":
    app.run(debug=True)
