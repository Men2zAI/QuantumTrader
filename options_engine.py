import yfinance as yf
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def analizar_opciones(ticker):
    """
    Sensor de Derivados: Extrae el Ratio Put/Call del mercado de opciones.
    Devuelve un valor entre 0.0 (Pánico Institucional/Trampa) y 1.0 (Euforia/Apoyo).
    """
    try:
        activo = yf.Ticker(ticker)
        fechas_expiracion = activo.options
        
        # Si la empresa no tiene mercado de opciones, devolvemos neutralidad
        if not fechas_expiracion:
            return 0.50
            
        # Analizamos el vencimiento más cercano (donde hay más especulación a corto plazo)
        vencimiento_proximo = fechas_expiracion[0]
        cadena = activo.option_chain(vencimiento_proximo)
        
        calls = cadena.calls
        puts = cadena.puts
        
        # Sumamos el volumen total de transacciones de hoy
        volumen_calls = calls['volume'].sum() if 'volume' in calls else 0
        volumen_puts = puts['volume'].sum() if 'volume' in puts else 0
        
        # Evitar división por cero
        if volumen_calls == 0:
            return 0.50
            
        # Calcular el Put/Call Ratio
        pcr = volumen_puts / volumen_calls
        
        # Traducir el PCR a una señal para la IA (0.0 a 1.0)
        # PCR normal es alrededor de 0.7 a 1.0
        if pcr > 1.2:
            score = 0.20  # Fuerte sesgo bajista (Ballenas comprando Puts)
        elif pcr > 1.0:
            score = 0.40  # Ligeramente bajista
        elif pcr < 0.6:
            score = 0.80  # Fuerte sesgo alcista (Ballenas comprando Calls)
        elif pcr < 0.8:
            score = 0.60  # Ligeramente alcista
        else:
            score = 0.50  # Neutral
            
        return score
        
    except Exception as e:
        # Silenciamos el error para no ensuciar la consola del orquestador
        return 0.50

if __name__ == "__main__":
    # Prueba de diagnóstico local
    print("🐋 [OPCIONES] Iniciando barrido de telemetría institucional...")
    empresas_prueba = ["NVDA", "AAPL", "TSLA"]
    
    for emp in empresas_prueba:
        resultado = analizar_opciones(emp)
        print(f"📊 {emp} -> Sentimiento de Opciones: {resultado*100:.1f}%")