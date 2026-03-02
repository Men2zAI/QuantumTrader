import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
import re

def generar_y_enviar_reporte():
    archivo = 'historial_decisiones.csv'
    if not os.path.exists(archivo): return

    df = pd.read_csv(archivo)
    # Filtrar solo registros procesados (✅, ❌ o 🛑)
    df = df[df['resultado_real'].str.contains('✅|❌|🛑', na=False)]
    
    if df.empty: return

    def extraer_datos_resultado(row):
        texto = str(row['resultado_real'])
        # Extraer el valor en dólares
        match = re.search(r'\$\s?(-?\d+\.?\d*)', texto)
        ganancia = float(match.group(1)) if match else 0.0
        
        # Determinar color según el tipo de resultado
        if "✅" in texto:
            color = 'green'
        elif "🛑" in texto:
            color = 'orange'  # ¡El color de seguridad!
        else:
            color = 'red'
        
        # Ajuste de signo: si era VENTA y el precio bajó (-$), es ganancia (+)
        if "VENTA" in str(row['prediccion']):
            ganancia = -ganancia
            
        return pd.Series([ganancia, color])

    df[['ganancia', 'color']] = df.apply(extraer_datos_resultado, axis=1)
    resumen = df.groupby('ticker').agg({'ganancia': 'sum', 'color': 'last'}).reset_index()
    total_dia = df['ganancia'].sum()

    # --- Crear Gráfico ---
    plt.figure(figsize=(12, 6))
    plt.bar(resumen['ticker'], resumen['ganancia'], color=resumen['color'])
    plt.axhline(0, color='black', linewidth=0.8)
    plt.title(f'Balance del Día: ${total_dia:.2f} USD (Fusibles Activos 🛡️)')
    plt.ylabel('Ganancia/Pérdida ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reporte_diario.png')

    # --- Enviar a Telegram ---
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    msg = f"📊 *Resumen Robusto de Operaciones*\n\n"
    msg += f"✅ Verde: Aciertos\n"
    msg += f"🛑 Naranja: Stop Loss (Pérdida limitada)\n"
    msg += f"❌ Rojo: Pérdida en curso\n\n"
    msg += f"💰 *Balance Total: ${total_dia:.2f} USD*"

    url_foto = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open('reporte_diario.png', 'rb') as foto:
        requests.post(url_foto, data={'chat_id': chat_id, 'caption': msg, 'parse_mode': 'Markdown'}, files={'photo': foto})

if __name__ == "__main__":
    generar_y_enviar_reporte()