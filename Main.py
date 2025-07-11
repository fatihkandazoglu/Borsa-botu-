import yfinance as yf
import requests
from datetime import datetime, timedelta

BOT_TOKEN = '7502364961:AAHjBdC4JHEi27K7hdGa3MelAir5VXXDtfs'
CHAT_ID = '1608045019'

hisseler = ["THYAO.IS", "SISE.IS", "ASELS.IS", "KRDMD.IS"]

def teknik_analiz(hisse):
    try:
        df = yf.download(hisse, period="3mo", interval="1d")
        if df.empty or len(df) < 50:
            return f"⚠️ <b>{hisse}</b>: Veri yetersiz"

        df.dropna(inplace=True)

        df['EMA10'] = df['Close'].ewm(span=10).mean()
        df['MA50'] = df['Close'].rolling(50).mean()

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
        if stochrsi > 80:
            sinyaller.append("⚠️ StochRSI Yüksek")
        elif stochrsi < 20:
            sinyaller.append("🟢 StochRSI Düşük")

        return f"⚠️ <b>{hisse}</b>: {', '.join(sinyaller)}"

    except Exception as e:
        return f"⚠️ <b>{hisse}</b>: Hata - {str(e)}"

def telegram_mesaj_gonder(metin):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': metin,
        'parse_mode': 'HTML'
    }
    r = requests.post(url, data=data)
    print(f"Telegram yanıtı: {r.status_code} - {r.text}")

# Tüm sinyalleri topla
simdi = (datetime.utcnow() + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')
rapor = f"📊 <b>{simdi} GÜNLÜK SİNYALLER</b>\n\n"
for hisse in hisseler:
    rapor += teknik_analiz(hisse) + "\n"

# Telegram'a gönder
telegram_mesaj_gonder(rapor)