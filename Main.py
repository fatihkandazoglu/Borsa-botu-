import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# TELEGRAM BOT AYARLARI
BOT_TOKEN = '7502364961:AAHjBdC4JHEi27K7hdGa3MelAir5VXXDtfs'
CHAT_ID = '1608045019'

# HİSSE LİSTESİ
HISSE_LISTESI = ['THYAO.IS', 'SISE.IS', 'ASELS.IS', 'KRDMD.IS']

# Telegram mesaj gönderme fonksiyonu
def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mesaj}
    requests.post(url, data=payload)

# Teknik analiz fonksiyonu
def teknik_analiz(hisse):
    try:
        df = yf.download(hisse, period="2mo", interval="1d")
        df.dropna(inplace=True)

        if len(df) < 15:
            return f"⚠️ {hisse} verisi yetersiz."

        df['EMA'] = df['Close'].ewm(span=10).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        close = df['Close'].iloc[-1]
        ema = df['EMA'].iloc[-1]
        rsi = df['RSI'].iloc[-1]

        if close > ema and rsi < 70:
            return f"📈 {hisse}: AL"
        elif close < ema and rsi > 30:
            return f"📉 {hisse}: SAT"
        else:
            return f"➖ {hisse}: NÖTR"
    except Exception as e:
        return f"⚠️ {hisse} verisi alınamadı. Hata: {str(e)}"

# Ana fonksiyon
def main():
    türkiye_saati = datetime.utcnow() + timedelta(hours=3)
    mesajlar = [f"📊 {türkiye_saati.strftime('%d.%m.%Y %H:%M')} GÜNLÜK SİNYALLER"]

    for hisse in HISSE_LISTESI:
        mesajlar.append(teknik_analiz(hisse))

    telegram_mesaj_gonder("\n".join(mesajlar))

# Çalıştır
if __name__ == "__main__":
    main()