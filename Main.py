import yfinance as yf
import requests
from datetime import datetime, timedelta

BOT_TOKEN = '7502364961:AAHjBdC4JHEi27K7hdGa3MelAir5VXXDtfs'
CHAT_ID = '1608045019'

def telegram_mesaj_gonder(metin):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': metin, 'parse_mode': 'HTML'}
    requests.post(url, data=data)

def teknik_analiz(hisse):
    try:
        df = yf.download(hisse, period="6mo", interval="1d")

        if df.empty or len(df) < 50:
            return f"⚠️ <a href='https://finance.yahoo.com/quote/{hisse}'>{hisse}</a>: Veri yetersiz"

        df['EMA10'] = df['Close'].ewm(span=10).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()

        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        min_rsi = df['RSI'].rolling(14).min()
        max_rsi = df['RSI'].rolling(14).max()
        df['StochRSI'] = ((df['RSI'] - min_rsi) / (max_rsi - min_rsi)) * 100

        df.dropna(inplace=True)

        if df.empty:
            return f"⚠️ <a href='https://finance.yahoo.com/quote/{hisse}'>{hisse}</a>: Tüm göstergeler NaN oldu"

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

        return f"📊 <a href='https://finance.yahoo.com/quote/{hisse}'>{hisse}</a>: {', '.join(sinyaller)}"

    except Exception as e:
        return f"⚠️ <a href='https://finance.yahoo.com/quote/{hisse}'>{hisse}</a>: Hata - {str(e)}"

if __name__ == "__main__":
    hisseler = ['THYAO.IS', 'SISE.IS', 'ASELS.IS', 'KRDMD.IS']
    simdi = (datetime.utcnow() + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')
    rapor = f"📉 <b>{simdi} GÜNLÜK SİNYALLER</b>\n\n"

    for hisse in hisseler:
        sonuc = teknik_analiz(hisse)
        rapor += sonuc + "\n"

    telegram_mesaj_gonder(rapor)