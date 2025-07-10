import yfinance as yf
from datetime import datetime
import requests

BOT_TOKEN = '7502364961:AAHjBdC4JHEi27K7hdGa3MelAir5VXXDtfs'
CHAT_ID = '1608045019'
HISSE_LISTESI = ['THYAO.IS', 'SISE.IS', 'ASELS.IS', 'KRDMD.IS']

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mesaj}
    requests.post(url, data=payload)

def teknik_analiz_yap(hisse):
    try:
        data = yf.download(hisse, period='5d', interval='1d')
        if data.empty:
            return f"⚠️ {hisse} verisi alınamadı."
        
        kapanis = data['Close'].iloc[-1]
        onceki = data['Close'].iloc[-2]
        
        if kapanis > onceki:
            return f"📈 {hisse}: AL"
        elif kapanis < onceki:
            return f"📉 {hisse}: SAT"
        else:
            return f"➖ {hisse}: NÖTR"
    except Exception as e:
        return f"⚠️ {hisse} verisi alınamadı. Hata: {str(e)}"

def main():
    mesajlar = [f"📊 {datetime.now().strftime('%d.%m.%Y %H:%M')} GÜNLÜK SİNYALLER"]
    for hisse in HISSE_LISTESI:
        mesajlar.append(teknik_analiz_yap(hisse))
    telegram_mesaj_gonder("\n".join(mesajlar))

if __name__ == '__main__':
    main()
