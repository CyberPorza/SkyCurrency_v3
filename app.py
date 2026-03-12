import requests
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # En basit veri yapısı
    weather = {"temp": "8", "desc": "Parçalı Bulutlu"}
    currencies = [
        {'code': 'USD/TRY', 'name': 'Amerikan Doları', 'val': '44.13'},
        {'code': 'EUR/TRY', 'name': 'Euro', 'val': '51.02'}
    ]
    gold = [
        {'name': 'Gram Altın', 'val': '7.215,00'},
        {'name': 'Çeyrek Altın', 'val': '11.850,00'}
    ]

    try:
        # Sadece hava durumunu çekmeyi dene, diğerleri hata verirse uygulama çökmesin
        w_res = requests.get("https://wttr.in/Istanbul?format=j1", timeout=5).json()
        weather['temp'] = w_res['current_condition'][0]['temp_C']
        weather['desc'] = w_res['current_condition'][0]['lang_tr'][0]['value']
    except:
        pass

    return render_template('index.html', weather=weather, currencies=currencies, gold=gold)

if __name__ == "__main__":
    app.run(debug=True)
