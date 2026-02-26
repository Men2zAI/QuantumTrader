import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
import re

def generar_y_enviar_reporte():
    archivo = 'historial_decisiones.csv'
    if not os.path.exists(archivo): return

    df = pd.read_csv(archivo)
    # Filtrar solo las que ya tienen resultado (no PENDIENTE)
    df = df[df['resultado_real'].str.contains('✅|❌', na=False)]
    
    if df.empty: return

    # Extraer la ganancia en USD del texto "✅ (-1.09% | $-2.04)"
    def extraer_usd(row):
        match = re.search(r'\$\s?(-?\d+\.?\d*)', row['resultado_real'])
        if not match: return 0.0
        diff = float(match.group(1))
        return -diff if "VENTA" in row['prediccion'] else diff

    df['ganancia'] = df.apply(extraer_usd, axis=1)
    resumen = df.groupby('ticker')['ganancia'].sum().reset_index()
    total_dia = df['ganancia'].sum()

    # --- Crear Gráfico ---
    plt.figure(figsize=(10, 6))
    colores = ['green' if x > 0 else 'red' for x in resumen['ganancia']]
    plt.bar(resumen['ticker'], resumen['ganancia'], color=colores)
    plt.axhline(0, color='black', linewidth=0.8)
    plt.title(f'Balance del Día: ${total_dia:.2f} USD')
    plt.ylabel('Ganancia/Pérdida ($)')
    plt.savefig('reporte_diario.png')

    # --- Enviar a Telegram ---
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    msg = f"📊 *Resumen de Operaciones*\n\n"
    for _, r in resumen.iterrows():
        msg += f"• {r['ticker']}: {'+' if r['ganancia']>0 else ''}${r['ganancia']:.2f}\n"
    msg += f"\n💰 *Balance Total: ${total_dia:.2f} USD*"

    # Enviar Foto
    url_foto = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open('reporte_diario.png', 'rb') as foto:
        requests.post(url_foto, data={'chat_id': chat_id, 'caption': msg, 'parse_mode': 'Markdown'}, files={'photo': foto})

if __name__ == "__main__":
    generar_y_enviar_reporte()