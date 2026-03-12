import os
import pandas as pd
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
alpaca = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'), 
    os.getenv('ALPACA_SECRET_KEY'), 
    'https://paper-api.alpaca.markets', 
    api_version='v2'
)

def analizar_opciones(ticker):
    try:
        fin = datetime.now() - timedelta(minutes=16) # Bypass SIP
        inicio = fin - timedelta(days=30) 
        
        barras = alpaca.get_bars(
            ticker, 
            tradeapi.rest.TimeFrame.Day, 
            start=inicio.strftime('%Y-%m-%d'), 
            end=fin.strftime('%Y-%m-%d'),
            feed='iex'
        ).df
        
        if barras.empty or len(barras) < 10:
            return 0.50
            
        volumen_promedio = barras['volume'].mean()
        volumen_reciente = barras['volume'].iloc[-3:].mean()
        
        precio_promedio = barras['close'].mean()
        precio_actual = barras['close'].iloc[-1]
        
        ratio_volumen = volumen_reciente / volumen_promedio
        
        if ratio_volumen > 1.3 and precio_actual > precio_promedio:
            probabilidad = 0.70 
        elif ratio_volumen > 1.3 and precio_actual < precio_promedio:
            probabilidad = 0.30 
        else:
            probabilidad = 0.50 
            
        return probabilidad

    except Exception as e:
        print(f"⚠️ Error Flujo Institucional ({ticker}): {e}")
        return 0.50