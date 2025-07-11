def teknik_analiz(hisse):
    try:
        df = yf.download(hisse, period="3mo", interval="1d")
        df.dropna(inplace=True)

        if len(df) < 30:
            return f"⚠️ {hisse}: Veri yetersiz"

        df['EMA10'] = df['Close'].ewm(span=10).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()

        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Stokastik RSI
        low14 = df['RSI'].rolling(14).min()
        high14 = df['RSI'].rolling(14).max()
        df['StochRSI'] = (df['RSI'] - low14) / (high14 - low14) * 100

        # Son değerler
        close = df['Close'].iloc[-1]
        ema = df['EMA10'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        stochrsi = df['StochRSI'].iloc[-1]
        ma50 = df['MA50'].iloc[-1]
        ma200 = df['MA200'].iloc[-1]
        high = df['High'].iloc[-1]

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