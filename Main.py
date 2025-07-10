import requests
import pandas as pd
from datetime import datetime

# TELEGRAM BOT AYARLARI
BOT_TOKEN = '7502364961:AAHjBdC4JHEi27K7hdGa3MelAir5VXXDtfs'
CHAT_ID = '1608045019'

# FINNHUB API ANAHTARI
FINNHUB_API_KEY = 'd1nqjppr01qovv8ku3k0d1nqjppr01qovv8ku3kg'

# HİSSE SENETLERİ
HISSE_LISTESI = ['THYAO', 'SISE', 'ASELS', 'KRDMD']

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mesaj}
    requests.post(url, data=payload)

def teknik_analiz(hisse):
    try:
        symbol = hisse + '.IS'  # BIST sembolleri için
        url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}'
        response = requests.get(url)
        data = response.json()

        close = data['c']
        open_ = data['o']

        # Basit mantık: gün içi yükseliyorsa AL, düşüyorsa SAT
        if close > open_:
            return f"📈 {hisse}: AL"
        elif close < open_:
            return f"📉 {hisse}: SAT"
        else:
            return f"➖ {hisse}: NÖTR"
    except Exception as e:
        return f"⚠️ {hisse} verisi alınamadı."

def main():
    mesajlar = [f"📊 {datetime.now().strftime('%d.%m.%Y %H:%M')} GÜNLÜK SİNYALLER"]
    for hisse in HISSE_LISTESI:
        sinyal = teknik_analiz(hisse)
        mesajlar.append(sinyal)

    final_mesaj = "\n".join(mesajlar)
    telegram_mesaj_gonder(final_mesaj)

if __name__ == '__main__':
    main()
