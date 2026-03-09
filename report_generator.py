import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import notifier
import broker_api  # <--- INYECTAMOS EL BROKER AQUÍ

def generar_y_enviar_reporte():
    archivo_historial = 'historial_decisiones.csv'
    archivo_balance = 'balance_history.csv'
    
    # 1. OBTENER EL SALDO REAL DIRECTAMENTE DE WALL STREET
    try:
        if broker_api.alpaca:
            cuenta = broker_api.alpaca.get_account()
            # Usamos portfolio_value (Efectivo + Valor de las acciones compradas)
            saldo_total = float(cuenta.portfolio_value)
        else:
            saldo_total = 0.0
    except Exception as e:
        print(f"⚠️ Error conectando al broker para el reporte: {e}")
        saldo_total = 0.0

    # 2. Registrar el balance en el historial
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    if not os.path.exists(archivo_balance):
        df_balance = pd.DataFrame(columns=['fecha', 'saldo'])
    else:
        df_balance = pd.read_csv(archivo_balance)
        
    nueva_fila = pd.DataFrame({'fecha': [fecha_hoy], 'saldo': [saldo_total]})
    df_balance = pd.concat([df_balance, nueva_fila], ignore_index=True)
    df_balance.to_csv(archivo_balance, index=False)

    # 3. Analizar operaciones
    operaciones_totales = 0
    tasa_acierto = 0.0
    
    if os.path.exists(archivo_historial):
        df_hist = pd.read_csv(archivo_historial)
        cerradas = df_hist[~df_hist['resultado_real'].isin(['PENDIENTE', '⚪ NO OPERADO'])]
        operaciones_totales = len(cerradas)
        
        if operaciones_totales > 0:
            ganadoras = cerradas[cerradas['resultado_real'].str.contains("TAKE PROFIT|LIQUIDACIÓN|TRAILING STOP", na=False)]
            tasa_acierto = (len(ganadoras) / operaciones_totales) * 100

    # 4. Crear el gráfico de crecimiento
    plt.figure(figsize=(10, 5))
    plt.plot(df_balance['fecha'], df_balance['saldo'], marker='o', color='#00ffcc', linewidth=2)
    plt.title('Rendimiento del Fondo Cuantitativo V9 (Alpaca API)', color='white')
    plt.xlabel('Fecha', color='lightgray')
    plt.ylabel('Capital (USD)', color='lightgray')
    plt.grid(True, linestyle='--', alpha=0.3)
    
    ax = plt.gca()
    ax.set_facecolor('#1e1e1e')
    plt.gcf().set_facecolor('#121212')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333333')
        
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    ruta_imagen = 'reporte_diario.png'
    plt.savefig(ruta_imagen, dpi=300, facecolor='#121212')
    plt.close()

    # 5. Enviar el reporte a Telegram
    mensaje_reporte = (
        f"📊 *REPORTE INSTITUCIONAL V9*\n"
        f"💰 Equidad Total (Alpaca): ${saldo_total:.2f}\n"
        f"📈 Win Rate Histórico: {tasa_acierto:.2f}%\n"
        f"🔄 Operaciones Cerradas: {operaciones_totales}"
    )
    
    notifier.enviar_imagen_telegram(ruta_imagen, mensaje_reporte)