import brain
import notifier
import logger_engine
import validator
import json
import os

# Tu matriz de 20 sensores configurada
EMPRESAS = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", 
            "AMD", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST", "AVGO", 
            "QCOM", "TMUS", "TXN", "AMAT"]

def ejecutar_analisis_dinamico():
    # 1. Auditoría de ciclos previos para actualizar saldo y cerrar Stop Loss
    validator.validar_predicciones()
    
    # 2. Carga de activos que la IA ha marcado como rentables
    elegidos = []
    if os.path.exists('elegidos.json'):
        with open('elegidos.json', 'r') as f:
            elegidos = json.load(f)
    else:
        elegidos = EMPRESAS

    candidatos = []
    
    # 3. Escaneo Global
    for empresa in EMPRESAS:
        try:
            df = brain.obtener_datos(empresa)
            señal, precio, fiabilidad = brain.predecir(df, empresa)
            
            # Registro obligatorio para el entrenamiento de la IA
            logger_engine.guardar_registro(empresa, precio, señal, fiabilidad)
            
            # Filtro de Élite Base (Umbral mínimo de 52% para no perder oportunidades)
            if empresa in elegidos and "ALTA CONFIANZA" in señal and fiabilidad >= 52.0:
                candidatos.append({
                    'ticker': empresa,
                    'precio': precio,
                    'fiabilidad': fiabilidad
                })
        except Exception as e:
            print(f"⚠️ Error en sensor {empresa}: {e}")

    # 4. SELECCIÓN TOP 5: Priorizamos las señales más robustas
    elite_picks = sorted(candidatos, key=lambda x: x['fiabilidad'], reverse=True)[:5]
    
    # 5. GESTIÓN DE CAPITAL DINÁMICO (Smart Sizing)
    if not elite_picks:
        notifier.enviar_telegram("📡 *Escaneo:* No hay señales claras (>52%). Capital de $1004.68 protegido. 🛡️")
    else:
        for pick in elite_picks:
            # ... dentro del bucle de elite_picks en main.py ...
            fiab = pick['fiabilidad']
            monto = 200.0 if fiab >= 60.0 else (100.0 if fiab >= 55.0 else 50.0)
        
        # Guardamos con el nuevo dato de monto
            logger_engine.guardar_registro(pick['ticker'], pick['precio'], pick['señal'], fiab, monto)
            
            # Lógica de asignación de recursos según potencia de señal
            if fiab >= 60.0:
                monto = 200.0
                prefijo = "🚀 *ÉLITE CONVICCIÓN*"
            elif fiab >= 55.0:
                monto = 100.0
                prefijo = "🎯 *ÉLITE ESTÁNDAR*"
            else:
                monto = 50.0
                prefijo = "🔬 *ÉLITE EXPLORACIÓN*"

            msg = (f"{prefijo}: {pick['ticker']}\n"
                   f"📍 Precio: ${pick['precio']:.2f}\n"
                   f"📊 Fiabilidad: {fiab}%\n"
                   f"💰 Inversión sugerida: ${monto}")
            
            notifier.enviar_telegram(msg)
        
        notifier.enviar_telegram(f"✅ Escaneo finalizado con {len(elite_picks)} señales dinámicas.")

if __name__ == "__main__":
    ejecutar_analisis_dinamico()