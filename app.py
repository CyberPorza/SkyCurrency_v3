import requests
from flask import Flask, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_gold_from_google(symbol):
    try:
        # Google Finance linki (Gram Altın için GAU-TRY kullanılır)
        url = f"https://www.google.com/finance/quote/{symbol}:TRY"
        res = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Google Finance'daki fiyat hücresinin klası genellikle 'ymv9yc'dir
        price = soup.find("div", {"class": "ymv9yc"}).text
        return price.replace("₺", "").strip()
    except:
        return "N/A"

@app.route('/')
def index():
    # --- HAVA DURUMU ---
    weather = {"temp": "8", "desc": "Parçalı Bulutlu"}
    try:
        w_res = requests.get("https://wttr.in/Istanbul?format=j1", timeout=5).json()
        weather = {"temp": w_res['current_condition'][0]['temp_C'], "desc": w_res['current_condition'][0]['lang_tr'][0]['value']}
    except: pass

    # --- DÖVİZ ---
    currencies = []
    try:
        c_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
        usd_val = c_res['rates']['TRY']
        curr_map = [
            {'code': 'USD', 'name': 'Amerikan Doları', 'flag': 'us'},
            {'code': 'EUR', 'name': 'Euro', 'flag': 'eu'},
            {'code': 'GBP', 'name': 'İngiliz Sterlini', 'flag': 'gb'}
        ]
        for item in curr_map:
            rate = c_res['rates'].get(item['code'], 1)
            currencies.append({'code': f"{item['code']}/TRY", 'name': item['name'], 'val': round(usd_val / rate, 2), 'flag': item['flag']})
    except: pass

    # --- ALTIN (GOOGLE FINANCE) ---
    # Gram altın Google'da 'GAU' olarak geçer.
    # Not: Çeyrek ve Yarım Google Finance'da direkt olmadığı için onları Doviz.com'dan çekmeye devam ediyoruz
    gold = []
    gram_price = get_gold_from_google("GAU")
    gold.append({'name': 'Gram Altın', 'val': gram_price})

    # Diğerleri için hızlı bir yedek kazıma
    try:
        res_altin = requests.get("https://www.doviz.com/altin", headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res_altin.text, "html.parser")
        others = {"Çeyrek Altın": "ceyrek-altin", "Yarım Altın": "yarim-altin", "Tam Altın": "tam-altin"}
        for name, key in others.items():
            tag = soup.find("td", {"data-socket-key": key, "data-socket-attr": "s"})
            gold.append({'name': name, 'val': tag.text.strip() if tag else "N/A"})
    except: pass

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold)

if __name__ == "__main__":
    app.run(debug=True)
