def teknik_analiz(hisse):
    try:
        df = yf.download(hisse, period="2mo", interval="1d")
        df.dropna(inplace=True)

        if df.shape[0] < 15:
            return f"⚠️ {hisse} verisi yetersiz."

        df['EMA'] = df['Close'].ewm(span=10).mean()

        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Series yerine float değer alın
        close = float(df['Close'].iloc[-1])
        ema = float(df['EMA'].iloc[-1])
        rsi = float(df['RSI'].iloc[-1])

        if close > ema and rsi < 70:
            return f"📈 {hisse}: AL"
        elif close < ema and rsi > 30:
            return f"📉 {hisse}: SAT"
        else:
            return f"➖ {hisse}: NÖTR"
    except Exception as e:
        return f"⚠️ {hisse} verisi alınamadı. Hata: {str(e)}"