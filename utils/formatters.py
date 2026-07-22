def formatear_cop(valor: float | int) -> str:
    """Formatea un número al estándar de pesos colombianos ($COP).
    
    Ejemplo: 3500 -> "$3.500" | 15000 -> "$15.000"
    """
    try:
        # Convertimos a entero para descartar centavos y formateamos con punto de miles
        valor_entero = int(round(float(valor)))
        return f"${valor_entero:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0"