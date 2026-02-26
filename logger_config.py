import logging

def setup_logger():
    # Crear un logger personalizado
    logger = logging.getLogger("QuantumTrader")
    logger.setLevel(logging.DEBUG)

    # Formato de los logs: Tiempo - Nivel - Mensaje
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # 1. Handler para Archivo (Guarda todo)
    file_handler = logging.FileHandler('trading_system.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 2. Handler para Consola (Solo información importante)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Añadir los handlers al logger
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger