# main.py

import requests
import pandas as pd
from datetime import datetime

# TELEGRAM BOT AYARLARI
BOT_TOKEN = '7502364961:AAHjBdC4JHEi27K7hdGa3MelAir5VXXDtfs'
CHAT_ID = '1608045019'

# HİSSE SENEDİ LİSTESİ
HISSE_LISTESI = ['THYAO', 'SISE', 'ASELS', 'KRDMD']

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mesaj}
    requests.post(url, data=payload)

def teknik_analiz(hisse):
    try:
        url = f'https://www.borsagrafik.com/api/indicators/{hisse}?interval=1d'
        response = requests.get(url)

        # API'den gelen ham veriyi yazdır (hata ayıklama)
        print(f"{hisse} - API Cevabı:")
        print(response.text)

        df = pd.DataFrame(response.json()['data'])

        df['ema'] = df['close'].ewm(span=10).mean()
        df['rsi'] = 100 - (100 / (1 + df['close'].pct_change().rolling(14).mean()))

        if df['close'].iloc[-1] > df['ema'].iloc[-1] and df['rsi'].iloc[-1] < 70:
            return f"📈 {hisse}: AL"
        elif df['close'].iloc[-1] < df['ema'].iloc[-1] and df['rsi'].iloc[-1] > 30:
            return f"📉 {hisse}: SAT"
        else:
            return f"➖ {hisse}: NÖTR"

    except Exception as e:
        print(f"Hata: {hisse} verisi alınamadı. {e}")
        return f"⚠️ {hisse} verisi alınamadı."

def main():
    mesajlar = [f"📊 {datetime.now().strftime('%d.%m.%Y %H:%M')} GÜNLÜK SİNYALLER"]
    for hisse in HISSE_LISTESI:
        sinyal = teknik_analiz(hisse)
        mesajlar.append(sinyal)

    final_mesaj = "\n".join(mesajlar)
    print("Telegram mesajı gönderiliyor...")
    telegram_mesaj_gonder(final_mesaj)
    print("Telegram mesajı gönderildi.")

if __name__ == '__main__':
    main()
