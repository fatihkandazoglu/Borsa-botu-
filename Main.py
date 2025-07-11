import requests
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

BOT_TOKEN = '7502364961:AAHjBdC4JHEi27K7hdGa3MelAir5VXXDtfs'
CHAT_ID = '1608045019'

def telegram_mesaj_gonder(metin):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': metin}
    r = requests.post(url, data=data)
    print(f"Telegram yanıtı: {r.status_code} - {r.text}")

def teknik_analiz(hisse):
    try:
        df = yf.download(hisse, period="3mo", interval="1d")
        df.dropna(inplace=True)

        if len(df) < 60:
            return f"⚠️ {hisse}: Veri yetersiz"

        df['EMA10'] = df['Close'].ewm(span=10).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()

        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        low14 = df['RSI'].rolling(14).min()
        high14 = df['RSI'].rolling(14).max()
        df['StochRSI'] = ((df['RSI'] - low14) / (high14 - low14)) * 100

        close = df['Close'].iloc[-1]
        ema = df['EMA10'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        stochrsi = df['StochRSI'].iloc[-1]
        ma50 = df['MA50'].iloc[-1]
        ma200 = df['MA200'].iloc[-1]
        high = df['High'].iloc[-1]

        if any(pd.isna([ema, rsi, stochrsi, ma50, ma200])):
            return f"⚠️ {hisse}: Hesaplamalar tamamlanamadı (NaN)."

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

        return f"{hisse}: {', '.join(sinyaller)}"

    except Exception as e:
        return f"⚠️ {hisse}: Hata - {str(e)}"

# Hisse listesi örneği
hisseler = ["THYAO.IS", "ASELS.IS", "SISE.IS", "KRDMD.IS"]

# Mesajı oluştur
simdi = (datetime.utcnow() + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')
rapor = f"📊 {simdi} SİNYAL RAPORU\n\n"

for hisse in hisseler:
    rapor += teknik_analiz(hisse) + "\n"

# Mesajı gönder
telegram_mesaj_gonder(rapor)