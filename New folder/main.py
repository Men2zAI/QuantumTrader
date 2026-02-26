<<<<<<< HEAD
import yfinance as yf
from brain import TradingBrain
from risk_manager import RiskManager
from notifier import TelegramNotifier
import sys

def run_quantum_system(ticker):
    print(f"🔍 Escaneando {ticker} con sensores de precisión...")
    notifier = TelegramNotifier()
    
    try:
        df = yf.download(ticker, period="2y", interval="1d", progress=False)
        
        brain = TradingBrain()
        df_feat = brain.prepare_features(df)
        prediction, confidence = brain.train_predictive_model(df_feat)
        
        # Extracción segura de escalares
        ultimo_precio = float(df['Close'].values[-1])        # Usamos el RSI como proxy de volatilidad para el Risk Manager si no hay ATR
        volatilidad_estimada = float(df_feat['Volatilidad'].iloc[-1]) * ultimo_precio
        
        risk = RiskManager(total_balance=10000)
        plan = risk.calculate_position(ultimo_precio, volatilidad_estimada)
        
        status = "🟢 COMPRA" if prediction > ultimo_precio and confidence > 0.51 else "⚪ ESPERA"
        
        msg = (
            f"📊 <b>REPORTE IA: {ticker}</b>\n"
            f"───────────────────\n"
            f"• Precio: ${ultimo_precio:.2f}\n"
            f"• Predicción: ${prediction:.2f}\n"
            f"• Fiabilidad Direccional: {confidence:.1%}\n"
            f"• Estado: <b>{status}</b>\n"
            f"───────────────────\n"
        )
        
        if status == "🟢 COMPRA":
            msg += f"✅ <b>PLAN:</b> Comprar {plan['units']} un. | SL: ${plan['stop_loss']}"
            
        notifier.send_notification(msg)
        print(f"✅ Proceso finalizado. Fiabilidad: {confidence:.1%}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
=======
import yfinance as yf
from brain import TradingBrain
from risk_manager import RiskManager
from notifier import TelegramNotifier
import sys

def run_quantum_system(ticker):
    print(f"🔍 Escaneando {ticker} con sensores de precisión...")
    notifier = TelegramNotifier()
    
    try:
        df = yf.download(ticker, period="2y", interval="1d", progress=False)
        
        brain = TradingBrain()
        df_feat = brain.prepare_features(df)
        prediction, confidence = brain.train_predictive_model(df_feat)
        
        # Extracción segura de escalares
        ultimo_precio = float(df['Close'].values[-1])        # Usamos el RSI como proxy de volatilidad para el Risk Manager si no hay ATR
        volatilidad_estimada = float(df_feat['Volatilidad'].iloc[-1]) * ultimo_precio
        
        risk = RiskManager(total_balance=10000)
        plan = risk.calculate_position(ultimo_precio, volatilidad_estimada)
        
        status = "🟢 COMPRA" if prediction > ultimo_precio and confidence > 0.51 else "⚪ ESPERA"
        
        msg = (
            f"📊 <b>REPORTE IA: {ticker}</b>\n"
            f"───────────────────\n"
            f"• Precio: ${ultimo_precio:.2f}\n"
            f"• Predicción: ${prediction:.2f}\n"
            f"• Fiabilidad Direccional: {confidence:.1%}\n"
            f"• Estado: <b>{status}</b>\n"
            f"───────────────────\n"
        )
        
        if status == "🟢 COMPRA":
            msg += f"✅ <b>PLAN:</b> Comprar {plan['units']} un. | SL: ${plan['stop_loss']}"
            
        notifier.send_notification(msg)
        print(f"✅ Proceso finalizado. Fiabilidad: {confidence:.1%}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
>>>>>>> f166bfe0cf293ddad91f7123819bf678ce1e708d
    run_quantum_system(target)