import yfinance as yf
from transformers import pipeline
import warnings
import os

# Ocultar advertencias de TensorFlow/Torch
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

print("🧠 [NLP] Despertando red neuronal lingüística (FinBERT)...")
# Usamos el pipeline de Hugging Face específico para finanzas
try:
    nlp_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")
except Exception as e:
    print(f"⚠️ Error cargando FinBERT: {e}")
    nlp_pipeline = None

def analizar_sentimiento(ticker):
    """
    Sensor NLP: Descarga las últimas noticias del activo y evalúa el sentimiento.
    Devuelve un valor entre 0.0 (Pánico) y 1.0 (Euforia).
    """
    if nlp_pipeline is None:
        return 0.5

    try:
        # Extraemos el feed de noticias crudo
        noticias = yf.Ticker(ticker).news
        if not noticias:
            return 0.5 

        textos = []
        # Leemos los 5 titulares más recientes
        for n in noticias[:5]: 
            titulo = n.get('title', '')
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
        print(f"⚠️ Error leyendo noticias para {ticker}: {e}")
        return 0.5

if __name__ == "__main__":
    # Prueba rápida del sensor
    ticker_prueba = "AAPL"
    print(f"Noticias para {ticker_prueba}...")
    score = analizar_sentimiento(ticker_prueba)
    print(f"Sentimiento del mercado: {score*100:.2f}%")