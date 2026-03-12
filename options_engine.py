import yfinance as yf
import numpy as np
import requests # <-- NUEVO MÓDULO DE CAMUFLAJE

def analizar_opciones(ticker):
    try:
        # --- INYECCIÓN DE CAMUFLAJE DE RED ---
        sesion_camuflada = requests.Session()
        sesion_camuflada.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        
        tk = yf.Ticker(ticker, session=sesion_camuflada)
        vencimientos = tk.options
        
        if not vencimientos:
            return 0.50
            
        # Analizamos el vencimiento más cercano
        cadena = tk.option_chain(vencimientos[0])
        calls = cadena.calls
        puts = cadena.puts
        
        volumen_calls = calls['volume'].sum() if 'volume' in calls else 0
        volumen_puts = puts['volume'].sum() if 'volume' in puts else 0
        
        if volumen_calls == 0 and volumen_puts == 0:
            return 0.50
            
        ratio_put_call = volumen_puts / (volumen_calls + 1)
        
        # Lógica de mercado:
        # Ratio bajo (< 0.7) = Mucho optimismo (Calls dominan) -> Probabilidad Alta
        # Ratio alto (> 1.0) = Miedo (Puts dominan) -> Probabilidad Baja
        
        if ratio_put_call < 0.6:
            probabilidad = 0.70 
        elif ratio_put_call < 0.8:
            probabilidad = 0.60
        elif ratio_put_call > 1.2:
            probabilidad = 0.30
        else:
            probabilidad = 0.50
            
        # Extraer volatilidad implícita promedio de las opciones ITM (In The Money)
        # Esto requiere precio actual
        hist_df = tk.history(period="1d")
        if not hist_df.empty:
            precio_actual = hist_df['Close'].iloc[-1]
            # (Futura expansión: ajustar probabilidad según IV)
            
        return probabilidad

    except Exception as e:
        print(f"⚠️ Error Opciones ({ticker}): {e}")
        return 0.50