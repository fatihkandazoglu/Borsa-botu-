import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Hisse listesi
HISSE_LISTESI = ['THYAO.IS', 'SISE.IS', 'ASELS.IS', 'KRDMD.IS', 'TUPRS.IS', 'HEKTS.IS', 'SASA.IS', 'EREGL.IS']

# RSI ve Stokastik RSI fonksiyonu
def hesapla_teknik_analiz(hisse):
    try:
        df = yf.download(hisse, period="3mo", interval="1d")
        df.dropna(inplace=True)

        if len(df) < 30:
            return None

        df['EMA'] = df['Close'].ewm(span=10).mean()

        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Stokastik RSI
        min_rsi = df['RSI'].rolling(14).min()
        max_rsi = df['RSI'].rolling(14).max()
        df['StochRSI'] = (df['RSI'] - min_rsi) / (max_rsi - min_rsi)

        close = df['Close'].iloc[-1]
        ema = df['EMA'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        stoch = df['StochRSI'].iloc[-1]

        # Tavan adayı: EMA üstü, RSI < 70, StochRSI > 0.8
        if close > ema and rsi < 70 and stoch > 0.8:
            return {
                "Hisse": hisse,
                "Kapanış": round(close, 2),
                "EMA": round(ema, 2),
                "RSI": round(rsi, 2),
                "StochRSI": round(stoch, 2)
            }
        return None
    except Exception as e:
        return None

def main():
    print(f"📊 {datetime.now().strftime('%d.%m.%Y %H:%M')} TAVAN ADAYLARI")
    adaylar = []
    for hisse in HISSE_LISTESI:
        sonuc = hesapla_teknik_analiz(hisse)
        if sonuc:
            adaylar.append(sonuc)

    if not adaylar:
        print("⚠️ Uygun tavan adayı bulunamadı.")
    else:
        df = pd.DataFrame(adaylar)
        print(df)

if __name__ == "__main__":
    main()