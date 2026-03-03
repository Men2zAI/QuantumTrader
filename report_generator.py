import pandas as pd
import matplotlib.pyplot as plt
import os, requests, re, json

def calcular_proyeccion_roi():
    archivo = 'balance_history.csv'
    if not os.path.exists(archivo): return "📈 Calculando tendencia..."
    df = pd.read_csv(archivo)
    if len(df) < 2: return "📈 Datos iniciales..."
    
    saldo_act = df['saldo'].iloc[-1]
    roi_total = ((saldo_act - 1000) / 1000) * 100
    promedio_dia = (saldo_act - 1000) / len(df)
    
    if promedio_dia <= 0: return f"📊 ROI: {roi_total:.2f}% | Tendencia lateral."
    dias_duplicar = int((2000 - saldo_act) / promedio_dia)
    return f"🚀 *ROI:* `{roi_total:.2f}%` | *Meta $2,000:* `{dias_duplicar} días` aprox."

def generar_y_enviar_reporte():
    df = pd.read_csv('historial_decisiones.csv')
    df = df[df['resultado_real'].str.contains('✅|❌|🛑', na=False)].copy()
    if df.empty: return

    def extraer(row):
        t = str(row['resultado_real'])
        match = re.search(r'\$\s?(-?\d+\.?\d*)', t)
        val = float(match.group(1)) if match else 0.0
        color = 'green' if "✅" in t else ('orange' if "🛑" in t else 'red')
        # Ganancia nominal basada en inversión de $100
        match_p = re.search(r'\((-?\d+\.?\d*)\%', t)
        p = float(match_p.group(1)) if match_p else 0.0
        return pd.Series([100 * (p/100), color, t])

    df[['ganancia', 'color', 'texto']] = df.apply(extraer, axis=1)
    res = df.groupby('ticker').agg({'ganancia':'sum', 'color':'last', 'texto':'last'}).reset_index()
    
    plt.figure(figsize=(12, 6))
    plt.bar(res['ticker'], res['ganancia'], color=res['color'])
    plt.axhline(0, color='black', linewidth=0.8)
    plt.title(f'Rendimiento por Activo')
    plt.savefig('reporte_diario.png')

    with open('wallet.json', 'r') as f: saldo_total = json.load(f)['saldo_total']
    
    msg = f"📊 *INFORME DE CARTERA VIRTUAL*\n\n"
    for _, r in res.iterrows():
        icon = "🟢" if "✅" in r['texto'] else ("🟠" if "🛑" in r['texto'] else "🔴")
        msg += f"• {r['ticker']}: {icon} *${r['ganancia']:.2f}*\n"
    
    msg += f"\n🏦 *SALDO TOTAL:* `${saldo_total:.2f} USD`"
    msg += f"\n{calcular_proyeccion_roi()}"

    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendPhoto"
    with open('reporte_diario.png', 'rb') as f:
        requests.post(url, data={'chat_id': os.getenv('TELEGRAM_CHAT_ID'), 'caption': msg, 'parse_mode': 'Markdown'}, files={'photo': f})

if __name__ == "__main__": generar_y_enviar_reporte()