import requests
from flask import Flask, render_template

app = Flask(__name__)

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

    # --- ALTIN (HAM VERİ AKIŞI - GARANTİLİ) ---
    gold = []
    try:
        # Bu API doğrudan veri akışı sağlar, bloklanma riski %0'a yakındır
        g_res = requests.get("https://finans.truncgil.com/today.json", timeout=10).json()
        
        targets = {
            "Gram Altın": "gram-altin",
            "Çeyrek Altın": "ceyrek-altin",
            "Yarım Altın": "yarim-altin",
            "Tam Altın": "tam-altin"
        }
        
        for display_name, api_key in targets.items():
            # API'dan gelen 'Satış' verisini alıyoruz
            val = g_res.get(api_key, {}).get('Satış', "N/A")
            gold.append({'name': display_name, 'val': val})
    except:
        # Eğer yukarıdaki API patlarsa yedek (GenelPara)
        try:
            g_res = requests.get("https://api.genelpara.com/embed/para-birimleri.json", timeout=5).json()
            gold = [
                {'name': 'Gram Altın', 'val': g_res.get('GA', {}).get('satis', 'N/A')},
                {'name': 'Çeyrek Altın', 'val': g_res.get('C', {}).get('satis', 'N/A')},
                {'name': 'Yarım Altın', 'val': g_res.get('Y', {}).get('satis', 'N/A')},
                {'name': 'Tam Altın', 'val': g_res.get('T', {}).get('satis', 'N/A')}
            ]
        except: pass

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold)

if __name__ == "__main__":
    app.run(debug=True)
