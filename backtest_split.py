import yfinance as yf
import pandas as pd

def test_por_año(ticker, año_inicio, año_fin):
    # Descargamos los dos años completos
    inicio = f"{año_inicio}-01-01"
    fin = f"{año_fin}-12-31"
    df = yf.download(ticker, start=inicio, end=fin, interval="1d", auto_adjust=True)
    
    if df.empty: return None

    # Separamos los datos por año
    df_2023 = df[df.index.year == 2023].copy()
    df_2024 = df[df.index.year == 2024].copy()

    def calcular_precision(data):
        aciertos = 0
        total = 0
        # Necesitamos al menos 20 días para la media móvil
        if len(data) < 21: return 0
        
        sma = data['Close'].rolling(window=20).mean()
        
        for i in range(20, len(data) - 1):
            precio_hoy = data['Close'].iloc[i].item()
            media_hoy = sma.iloc[i].item()
            precio_mañana = data['Close'].iloc[i+1].item()
            
            # Estrategia: ¿Precio sobre la media?
            prediccion_sube = precio_hoy > media_hoy
            realidad_subio = precio_mañana > precio_hoy
            
            if prediccion_sube == realidad_subio:
                aciertos += 1
            total += 1
        
        return round((aciertos / total) * 100, 2) if total > 0 else 0

    acc_2023 = calcular_precision(df_2023)
    acc_2024 = calcular_precision(df_2024)
    
    print(f"\n📊 Resultados para {ticker}:")
    print(f"   - 2023 (In-Sample): {acc_2023}%")
    print(f"   - 2024 (Out-of-Sample): {acc_2024}%")
    
    # Análisis de Robustez
    desviacion = abs(acc_2023 - acc_2024)
    if desviacion < 5:
        print(f"   ✅ SISTEMA ROBUSTO: La desviación es de solo {round(desviacion, 2)}%.")
    else:
        print(f"   ⚠️ POSIBLE OVERFITTING: La precisión varió un {round(desviacion, 2)}%.")

if __name__ == "__main__":
    for t in ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL"]:
        test_por_año(t, 2023, 2024)