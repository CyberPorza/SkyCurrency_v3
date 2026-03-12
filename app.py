import requests
from flask import Flask, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_google_gold(query):
    try:
        url = f"https://www.google.com/search?q={query}+fiyatı"
        res = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        # Google'ın döviz/altın kartındaki fiyat hücresini buluyoruz
        price = soup.find("span", {"class": "SwH9u"}).text # Bu class genelde fiyattır
        if not price:
            price = soup.find("div", {"class": "BNeawe iE14Cc AP7Wnd"}).text
        return price.split(" ")[0] # Sadece rakamı al
    except:
        return "N/A"

@app.route('/')
def index():
    # --- 1. HAVA DURUMU ---
    weather = {"temp": "8", "desc": "Parçalı Bulutlu"}
    try:
        w_res = requests.get("https://wttr.in/Istanbul?format=j1", timeout=5).json()
        weather = {"temp": w_res['current_condition'][0]['temp_C'], "desc": w_res['current_condition'][0]['lang_tr'][0]['value']}
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

    # --- 3. ALTIN PİYASASI (GOOGLE SCRAPER) ---
    gold = []
    gold_queries = {
        "Gram Altın": "gram+altın",
        "Çeyrek Altın": "çeyrek+altın",
        "Yarım Altın": "yarım+altın",
        "Tam Altın": "tam+altın"
    }
    
    # Google'dan çekmeyi dene, olmazsa yedek bir siteye bak
    try:
        res_altin = requests.get("https://www.doviz.com/altin", headers=HEADERS, timeout=10)
        soup_altin = BeautifulSoup(res_altin.text, "html.parser")
        
        mapping = {"Gram Altın": "gram-altin", "Çeyrek Altın": "ceyrek-altin", "Yarım Altın": "yarim-altin", "Tam Altın": "tam-altin"}
        
        for name, key in mapping.items():
            tag = soup_altin.find("span", {"data-socket-key": key})
            val = tag.text.strip() if tag else "N/A"
            gold.append({'name': name, 'val': val})
    except:
        gold = [{'name': k, 'val': "Bağlantı Yok"} for k in gold_queries.keys()]

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold)

if __name__ == "__main__":
    app.run(debug=True)
