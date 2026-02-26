# Crea un archivo llamado fix_csv.py y ejecútalo
with open('historial_decisiones.csv', 'r') as f:
    contenido = f.read()

# Buscamos donde termina el encabezado y empieza la fecha
header_end = "resultado_real"
if header_end in contenido and "resultado_real2026" in contenido:
    nuevo_contenido = contenido.replace("resultado_real2026", "resultado_real\n2026")
    with open('historial_decisiones.csv', 'w') as f:
        f.write(nuevo_contenido)
    print("✅ Archivo CSV corregido.")