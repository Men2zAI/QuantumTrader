import os
import alpaca_trade_api as tradeapi
from transformers import pipeline
import warnings
from dotenv import load_dotenv

# Ocultar advertencias de TensorFlow/Torch para mantener los logs limpios
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

print("🧠 [NLP] Despertando red neuronal lingüística (FinBERT)...")
try:
    # Usamos el pipeline de Hugging Face específico para finanzas
    nlp_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")
except Exception as e:
    print(f"⚠️ Error cargando FinBERT: {e}")
    nlp_pipeline = None

# 🔌 Inicialización de la Troncal Institucional (Alpaca)
load_dotenv()
try:
    alpaca = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'), 
        os.getenv('ALPACA_SECRET_KEY'), 
        'https://api.alpaca.markets', 
        api_version='v2'
    )
except Exception as e:
    print(f"⚠️ Error conectando a Alpaca en NLP: {e}")
    alpaca = None

def analizar_sentimiento(ticker):
    """
    Sensor NLP (Alpaca V10): Descarga las últimas noticias institucionales 
    del activo y evalúa el sentimiento.
    Devuelve un valor entre 0.0 (Pánico) y 1.0 (Euforia).
    """
    if nlp_pipeline is None or alpaca is None:
        return 0.5

    try:
        # 🌐 Extracción de noticias vía Alpaca (Bypass de Yahoo)
        noticias = alpaca.get_news(ticker, limit=5)
        if not noticias:
            return 0.5 

        textos = []
        # Leemos los 5 titulares más recientes
        for nota in noticias:
            # Alpaca devuelve objetos con .headline y .summary
            titulo = nota.headline if nota.headline else ''
            
            if titulo:
                textos.append(titulo)

        if not textos:
            return 0.5

        # La IA lee y clasifica los titulares
        resultados = nlp_pipeline(textos)
        
        puntaje_total = 0.0
        for res in resultados:
            etiqueta = res['label']
            score = res['score']
            
            # Traducción del sentimiento a probabilidad matemática
            if etiqueta == 'positive':
                puntaje_total += score         # Empuja hacia 1.0
            elif etiqueta == 'negative':
                puntaje_total += (1.0 - score) # Empuja hacia 0.0
            else:
                puntaje_total += 0.5           # Mantiene el balance (Neutral)
                
        sentimiento_promedio = puntaje_total / len(resultados)
        return round(sentimiento_promedio, 4)

    except Exception as e:
        print(f"⚠️ Error leyendo noticias (Alpaca) para {ticker}: {e}")
        return 0.5

if __name__ == "__main__":
    # Prueba rápida del sensor local
    ticker_prueba = "AAPL"
    print(f"📰 Buscando noticias institucionales para {ticker_prueba}...")
    score = analizar_sentimiento(ticker_prueba)
    print(f"🧠 Sentimiento del mercado (FinBERT): {score*100:.2f}%")