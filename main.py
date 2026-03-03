import brain, notifier, logger_engine, validator, json, os

EMPRESAS = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", "AMD", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST", "AVGO", "QCOM", "TMUS", "TXN", "AMAT"]

def ejecutar():
    validator.validar_predicciones() # Auditoría primero
    
    elegidos = []
    if os.path.exists('elegidos.json'):
        with open('elegidos.json', 'r') as f: elegidos = json.load(f)
    else: elegidos = EMPRESAS

    candidatos = []
    for e in EMPRESAS:
        try:
            df = brain.obtener_datos(e)
            señal, precio, fiab = brain.predecir(df, e)
            logger_engine.guardar_registro(e, precio, señal, fiab)
            
            if e in elegidos and "ALTA CONFIANZA" in señal and fiab >= 55.0:
                candidatos.append({'ticker': e, 'precio': precio, 'fiab': fiab})
        except: continue

    elite = sorted(candidatos, key=lambda x: x['fiab'], reverse=True)[:5]
    
    if not elite:
        notifier.enviar_telegram("📡 *Escaneo:* No hay señales de Élite (>55%). Saldo protegido. 🛡️")
    else:
        for p in elite:
            msg = f"🎯 *ÉLITE:* {p['ticker']}\n📍 Precio: ${p['precio']:.2f}\n📊 Fiabilidad: {p['fiab']}%"
            notifier.enviar_telegram(msg)
        notifier.enviar_telegram(f"✅ Escaneo finalizado: {len(elite)} picks detectados.")

if __name__ == "__main__": ejecutar()