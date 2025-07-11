import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta

BOT_TOKEN = '7502364961:AAHjBdC4JHEi27K7hdGa3MelAir5VXXDtfs'
CHAT_ID = '1608045019'

def telegram_mesaj_gonder(metin):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': metin, 'parse_mode': 'HTML'}
    r = requests.post(url, data=data)
    print(f"Telegram yanıtı: {r.status_code} - {r.text}")

def teknik_analiz(hisse):
    try:
        df = yf.download(hisse, period="6mo", interval="1d")
        if df.empty or len(df) < 200:
            return f"⚠️ <b>{hisse}</b>: Veri yetersiz"

        df.dropna(inplace=True)

        df['EMA10'] = df['Close'].ewm(span=10).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()

        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        df['StochRSI'] = (
            (df['RSI'] - df['RSI'].rolling(14).min()) /
            (df['RSI'].rolling(14).max() - df['RSI'].rolling(14).min())
        ) * 100

        df = df.dropna()
        if df.empty:
            return f"⚠️ <b>{hisse}</b>: Hesaplamalar tamamlanamadı (NaN)"

        latest = df.iloc[-1]

        close = latest['Close']
        ema = latest['EMA10']
        rsi = latest['RSI']
        stochrsi = latest['StochRSI']
        ma50 = latest['MA50']
        ma200 = latest['MA200']
        high = latest['High']

        sinyaller = []

        if close > ema and rsi < 70:
            sinyaller.append("📈 AL")
        elif close < ema and rsi > 30:
            sinyaller.append("📉 SAT")
        else:
            sinyaller.append("➖ NÖTR")

        if close == high:
            sinyaller.append("🚀 Tavan adayı")

        if close > ma50:
            sinyaller.append("✅ MA50 Üstü")
        if close > ma200:
            sinyaller.append("✅ MA200 Üstü")
        if stochrsi > 80:
            sinyaller.append("⚠️ StochRSI Yüksek")
        elif stochrsi < 20:
            sinyaller.append("🟢 StochRSI Düşük")

        return f"<b>{hisse}</b>: {', '.join(sinyaller)}"

    except Exception as e:
        return f"⚠️ <b>{hisse}</b>: Hata - {str(e)}"

# Hisseler listesi
hisseler = ["THYAO.IS", "SISE.IS", "ASELS.IS", "KRDMD.IS"]

sonuclar = []
for hisse in hisseler:
    sonuc = teknik_analiz(hisse)
    sonuclar.append(sonuc)

tarih = (datetime.utcnow() + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')
rapor = f"📊 <b>{tarih} GÜNLÜK SİNYALLER</b>\n\n" + "\n".join(sonuclar)

telegram_mesaj_gonder(rapor)