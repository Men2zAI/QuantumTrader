import plotly.graph_objects as go
from datetime import datetime

def generate_dashboard(df, ticker):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Precio')])

    # Añadir Media Móvil (EMA)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='orange', width=1.5), name='EMA 20'))

    # Dibujar líneas de Soporte detectadas matemáticamente
    soportes = df['Soporte'].dropna()
    for fecha, valor in soportes.items():
        fig.add_shape(type="line", x0=fecha, y0=valor, x1=df.index[-1], y1=valor,
                      line=dict(color="Green", width=1, dash="dot"))

    fig.update_layout(title=f'Terminal de Análisis: {ticker}',
                      yaxis_title='Precio USD',
                      template='plotly_dark',
                      xaxis_rangeslider_visible=False)
    
    # Guardar y abrir automáticamente
    file_name = f"dashboard_{ticker}.html"
    fig.write_html(file_name)
    print(f"✅ Dashboard generado: {file_name}")