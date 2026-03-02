import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
import re

def generar_y_enviar_reporte():
    archivo = 'historial_decisiones.csv'
    if not os.path.exists(archivo):
        print("⚠️ No se encontró el historial para generar el reporte.")
        return

    # 1. Cargar y filtrar datos procesados
    df = pd.read_csv(archivo)
    df = df[df['resultado_real'].str.contains('✅|❌|🛑', na=False)].copy()
    
    if df.empty:
        print("⚠️ No hay operaciones cerradas para reportar hoy.")
        return

    def extraer_datos_resultado(row):
        texto = str(row['resultado_real'])
        # Extraer el valor numérico después del símbolo $
        match = re.search(r'\$\s?(-?\d+\.?\d*)', texto)
        ganancia = float(match.group(1)) if match else 0.0
        
        # Determinar color para el gráfico
        if "✅" in texto:
            color = 'green'
        elif "🛑" in texto:
            color = 'orange'
        else:
            color = 'red'
        
        # Ajuste de signo: Si fue VENTA y el precio bajó (valor negativo), es GANANCIA
        if "VENTA" in str(row['prediccion']):
            ganancia = -ganancia
            
        return pd.Series([ganancia, color, texto])

    # Aplicar lógica de extracción
    df[['ganancia', 'color', 'texto_original']] = df.apply(extraer_datos_resultado, axis=1)
    
    # Agrupar por ticker para el resumen visual
    resumen = df.groupby('ticker').agg({
        'ganancia': 'sum', 
        'color': 'last', 
        'texto_original': 'last'
    }).reset_index()
    
    total_dia = df['ganancia'].sum()

    # 2. Generar Gráfico de Barras
    plt.figure(figsize=(12, 6))
    plt.bar(resumen['ticker'], resumen['ganancia'], color=resumen['color'])
    plt.axhline(0, color='black', linewidth=0.8)
    plt.title(f'Balance de Operaciones: ${total_dia:.2f} USD')
    plt.ylabel('Ganancia/Pérdida ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reporte_diario.png')

    # 3. Construir Mensaje de Telegram con Iconos Inteligentes
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    msg = f"📊 *Resumen de Operaciones Detallado*\n\n"
    
    for _, row in resumen.iterrows():
        # Lógica de iconos basada en el resultado real del auditor
        texto_audit = row['texto_original']
        if "✅" in texto_audit:
            status_icon = "🟢" # Acierto
        elif "🛑" in texto_audit:
            status_icon = "🟠" # Stop Loss activo (Fusible)
        else:
            status_icon = "🔴" # Fallo de predicción
            
        msg += f"• {row['ticker']}: {status_icon} *${row['ganancia']:.2f}*\n"
    
    msg += f"\n💰 *Balance Total: ${total_dia:.2f} USD*\n"
    msg += f"\n🟢 Acierto | 🟠 Stop Loss | 🔴 Fallo"

    # 4. Envío de Foto y Mensaje
    url_foto = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        with open('reporte_diario.png', 'rb') as foto:
            payload = {
                'chat_id': chat_id,
                'caption': msg,
                'parse_mode': 'Markdown'
            }
            files = {'photo': foto}
            r = requests.post(url_foto, data=payload, files=files)
            if r.status_code == 200:
                print("✅ Reporte enviado con éxito a Telegram.")
            else:
                print(f"❌ Error al enviar a Telegram: {r.text}")
    except Exception as e:
        print(f"❌ Error en el proceso de envío: {e}")

if __name__ == "__main__":
    generar_y_enviar_reporte()