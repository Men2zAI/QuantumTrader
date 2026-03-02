import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
import re

def generar_y_enviar_reporte():
    archivo = 'historial_decisiones.csv'
    if not os.path.exists(archivo): return

    df = pd.read_csv(archivo)
    df = df[df['resultado_real'].str.contains('✅|❌|🛑', na=False)].copy()
    if df.empty: return

    def extraer_datos_resultado(row):
        texto = str(row['resultado_real'])
        match = re.search(r'\$\s?(-?\d+\.?\d*)', texto)
        ganancia = float(match.group(1)) if match else 0.0
        
        if "✅" in texto: color = 'green'
        elif "🛑" in texto: color = 'orange'
        else: color = 'red'
        
        if "VENTA" in str(row['prediccion']):
            ganancia = -ganancia
            
        return pd.Series([ganancia, color, texto])

    df[['ganancia', 'color', 'texto_original']] = df.apply(extraer_datos_resultado, axis=1)
    resumen = df.groupby('ticker').agg({'ganancia': 'sum', 'color': 'last', 'texto_original': 'last'}).reset_index()
    total_dia = df['ganancia'].sum()

    # Gráfico
    plt.figure(figsize=(12, 6))
    plt.bar(resumen['ticker'], resumen['ganancia'], color=resumen['color'])
    plt.axhline(0, color='black', linewidth=0.8)
    plt.title(f'Balance Total: ${total_dia:.2f} USD')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reporte_diario.png')

    # --- CONSTRUIR EL MENSAJE CON EL LISTADO ---
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    msg = f"📊 *Resumen de Operaciones Detallado*\n\n"
    
    # Bucle para añadir cada empresa al mensaje
    for _, row in resumen.iterrows():
        icono = "🟢" if row['ganancia'] >= 0 else "🔴"
        msg += f"• {row['ticker']}: {icono} ${row['ganancia']:.2f}\n"
    
    msg += f"\n💰 *Balance Total: ${total_dia:.2f} USD*\n"
    msg += f"\n✅ Verde: Acierto | 🛑 Naranja: Stop Loss | ❌ Rojo: Fallo"

    url_foto = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open('reporte_diario.png', 'rb') as foto:
        requests.post(url_foto, data={'chat_id': chat_id, 'caption': msg, 'parse_mode': 'Markdown'}, files={'photo': foto})

if __name__ == "__main__":
    generar_y_enviar_reporte()