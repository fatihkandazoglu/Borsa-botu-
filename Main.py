import yfinance as yf

def teknik_analiz(hisse):
    try:
        # Daha uzun periyotla veri çek, örneğin 6 ay
        df = yf.download(hisse, period="6mo", interval="1d")
        
        if df.empty or len(df) < 50:
            return f"⚠️ {hisse}: Yetersiz veri (veri boş veya 50 günden az)"

        df.dropna(inplace=True)

        # EMA, MA, RSI hesaplamaları
        df['EMA10'] = df['Close'].ewm(span=10).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()

        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Stokastik RSI hesaplaması
        df['StochRSI'] = (
            (df['RSI'] - df['RSI'].rolling(14).min()) /
            (df['RSI'].rolling(14).max() - df['RSI'].rolling(14).min())
        ) * 100

        # En son satırda eksik veri varsa hata döndür
        latest = df.iloc[-1]
        if latest[['EMA10', 'MA50', 'MA200', 'RSI', 'StochRSI']].isnull().any():
            return f"⚠️ {hisse}: Hesaplamalar tamamlanamadı (NaN)"

        # Değerleri al
        close = latest['Close']
        ema = latest['EMA10']
        rsi = latest['RSI']
        stochrsi = latest['StochRSI']
        ma50 = latest['MA50']
        ma200 = latest['MA200']
        high = latest['High']

        # Sinyal üret
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