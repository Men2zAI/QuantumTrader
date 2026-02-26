import os
from datetime import datetime

def guardar_registro(ticker, precio, prediccion, fiabilidad):
    """
    Guarda la predicción en el archivo CSV para su posterior auditoría.
    """
    archivo = 'historial_decisiones.csv'
    # Encabezado estándar para que el validador y el generador de reportes no fallen
    header = "fecha,ticker,precio_entrada,prediccion,fiabilidad,resultado_real\n"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Si el archivo no existe, lo creamos con el encabezado
    if not os.path.exists(archivo):
        with open(archivo, 'w') as f:
            f.write(header)

    # Preparamos la línea de datos con el estado inicial 'PENDIENTE'
    nueva_linea = f"{fecha},{ticker},{precio},{prediccion},{fiabilidad}%,PENDIENTE\n"

    # Añadimos la línea al final del archivo (modo append 'a')
    try:
        with open(archivo, 'a') as f:
            f.write(nueva_linea)
    except Exception as e:
        print(f"❌ Error físico escribiendo en el CSV: {e}")