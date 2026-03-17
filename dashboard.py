import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="QuantumTrader Dashboard", page_icon="🤖", layout="wide")
st.title("🌍 QuantumTrader: Centro de Comando")

# Funciones de lectura de datos
@st.cache_data(ttl=60) # Refresca los datos cada 60 segundos
def cargar_datos():
    try:
        ws_ledger = pd.read_csv("wallstreet_ledger.csv")
    except:
        ws_ledger = pd.DataFrame()
        
    try:
        crypto_bal = pd.read_csv("crypto_balance.csv")
    except:
        crypto_bal = pd.DataFrame()
        
    return ws_ledger, crypto_bal

ws_ledger, crypto_bal = cargar_datos()

# ----------------- SECCIÓN ALPHA (WALL STREET) -----------------
st.header("🦅 Nodo Alpha: Wall Street")
if not ws_ledger.empty:
    col1, col2, col3 = st.columns(3)
    
    total_operaciones = len(ws_ledger)
    capital_invertido = ws_ledger['monto_invertido'].sum()
    confianza_media = ws_ledger['fiabilidad_ia'].mean()
    
    col1.metric("Operaciones Ejecutadas", total_operaciones)
    col2.metric("Capital Asignado (Aprox)", f"${capital_invertido:,.2f}")
    col3.metric("Confianza Media IA", f"{confianza_media:.2f}%")
    
    st.subheader("Últimas Operaciones")
    st.dataframe(ws_ledger.tail(5)[['timestamp', 'ticker', 'señal', 'precio_ejecucion', 'fiabilidad_ia']])
    
    # Gráfico de activos
    fig_ws = px.pie(ws_ledger, names='ticker', title='Distribución de Activos Comprados')
    st.plotly_chart(fig_ws, use_container_width=True)
else:
    st.info("No hay datos de Wall Street disponibles aún.")

st.divider()

# ----------------- SECCIÓN BETA (CRIPTO) -----------------
st.header("🪙 Nodo Beta: Cripto (DCA)")
if not crypto_bal.empty:
    # Asegurar compatibilidad de columnas
    if 'balance_btc' not in crypto_bal.columns:
        crypto_bal['balance_btc'] = 0.0
        
    ultima_fila = crypto_bal.iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Caja Fuerte (USDT)", f"${float(ultima_fila['balance_usdt']):,.2f}")
    col2.metric("Bóveda Bitcoin", f"₿ {float(ultima_fila['balance_btc']):.6f}")
    col3.metric("Último Precio BTC", f"${float(ultima_fila['precio_ejecucion']):,.2f}")
    
    st.subheader("Historial de Operaciones Cripto")
    # Filtrar solo las compras reales o señales importantes
    operaciones_reales = crypto_bal[crypto_bal['operacion'].isin(['BUY_TACTICAL', 'BUY_DCA', 'SELL_OR_WAIT'])].tail(10)
    st.dataframe(operaciones_reales[['timestamp', 'operacion', 'precio_ejecucion', 'balance_usdt']])
    
    # Gráfico de balance
    fig_crypto = px.line(crypto_bal, x='timestamp', y='precio_ejecucion', title='Rastreo de Precio BTC/USDT')
    st.plotly_chart(fig_crypto, use_container_width=True)
else:
    st.info("No hay datos de Cripto disponibles aún.")