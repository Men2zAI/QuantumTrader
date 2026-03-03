import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
import re
import json

def generar_y_enviar_reporte():
    archivo_csv = 'historial_decisiones.csv'
    archivo_wallet = 'wallet.json'
    
    if not os.path.exists(archivo_csv):
        print("⚠️ No hay datos para generar el reporte.")
        return

    # 1. Cargar datos y filtrar solo operaciones cerradas
    df = pd.read_csv(archivo_csv)
    df = df[df['resultado_real'].str.contains('✅|❌|🛑', na=False)].copy()
    
    if df.empty:
        print("⚠️ No hay operaciones cerradas hoy.")
        return

    # 2. Lógica de procesamiento de resultados
    def procesar_fila(row):
        texto = str(row['resultado_real'])
        match = re.search(r'\$\s?(-?\d+\.?\d*)', texto)
        # Extraemos la variación de precio o saldo
        valor = float(match.group(1)) if match else 0.0
        
        # Color para el gráfico basado en el símbolo
        if "✅" in texto: color = 'green'
        elif "🛑" in texto: color = 'orange'
        else: color = 'red'
        
        # Cálculo de ganancia nominal (para el gráfico de barras)
        # Nota: Usamos el histórico para calcular la ganancia del movimiento
        # (Precio_Actual - Precio_Entrada). Invertimos si es VENTA.
        try:
            # Si el CSV tiene los datos, calculamos la ganancia por acción
            precio_e = float(row['precio_entrada'])
            # Buscamos el % en el texto para ser precisos
            match_porc = re.search(r'\((-?\d+\.?\d*)\%', texto)
            porc = float(match_porc.group(1)) if match_porc else 0.0
            ganancia_nominal = 100 * (porc / 100) # Basado en inversión de $100
        except:
            ganancia_nominal = 0.0
            
        return pd.Series([ganancia_nominal, color, texto])

    df[['ganancia', 'color', 'texto_status']] = df.apply(procesar_fila, axis=1)
    
    # Agrupamos por ticker
    resumen = df.groupby('ticker').agg({
        'ganancia': 'sum', 
        'color': 'last', 
        'texto_status': 'last'
    }).reset_index()
    
    balance_dia = df['ganancia'].sum()

    # 3. Cargar Saldo de la Wallet
    saldo_actual = 1000.0
    if os.path.exists(archivo_wallet):
        with open(archivo_wallet, 'r') as f:
            wallet_data = json.load(f)
            saldo_actual = wallet_data['saldo_total']

    # 4. Generar Gráfico
    plt.figure(figsize=(12, 6))
    plt.bar(resumen['ticker'], resumen['ganancia'], color=resumen['color'])
    plt.axhline(0, color='black', linewidth=0.8)
    plt.title(f'Rendimiento por Activo (Inversión fija $100)')
    plt.ylabel('Ganancia/Pérdida en la operación ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('reporte_diario.png')

    # 5. Construir Mensaje de Telegram
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    msg = f"📊 *INFORME DE CARTERA VIRTUAL*\n"
    msg += f"📅 Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n\n"
    
    for _, row in resumen.iterrows():
        t = row['texto_status']
        icon = "🟢" if "✅" in t else ("🟠" if "🛑" in t else "🔴")
        msg += f"• {row['ticker']}: {icon} *${row['ganancia']:.2f}*\n"
    
    msg += f"\n💵 *Balance Sesión:* `${balance_dia:+.2f} USD`"
    msg += f"\n🏦 *SALDO TOTAL:* `${saldo_actual:.2f} USD`"
    msg += f"\n\n🟢 Acierto | 🟠 Stop Loss | 🔴 Fallo"

def calcular_metricas_riesgo():
    if not os.path.exists('balance_history.csv'):
        return 0, 0.0
    
    df_h = pd.read_csv('balance_history.csv')
    saldos = df_h['saldo'].tolist()
    
    # 1. Calcular Racha Actual (Días seguidos en positivo)
    racha = 0
    for i in range(len(saldos)-1, 0, -1):
        if saldos[i] > saldos[i-1]:
            racha += 1
        else:
            break
            
    # 2. Calcular Drawdown (Caída máxima desde el pico)
    max_pico = max(saldos) if saldos else 1000.0
    saldo_actual = saldos[-1] if saldos else 1000.0
    drawdown = ((max_pico - saldo_actual) / max_pico) * 100
    
    return racha, drawdown

    # 6. Enviar
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open('reporte_diario.png', 'rb') as foto:
        requests.post(url, data={'chat_id': chat_id, 'caption': msg, 'parse_mode': 'Markdown'}, files={'photo': foto})

if __name__ == "__main__":
    generar_y_enviar_reporte()