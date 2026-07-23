from models.pedido import Mesa, ItemPedido

class PrintService:
    """Servicio encargado de enrutar y generar los formatos de impresión para Caja, Cocina y Carnes."""

    @staticmethod
    def generar_ticket_caja(mesa: Mesa) -> str:
        """Genera la factura legal completa con valores monetarios para la Impresora de Caja."""
        lineas = [
            "==================================",
            "        EL RANCHO DE JAVI         ",
            "         FACTURA DE VENTA         ",
            f"Mesa: {mesa.id}",
            "==================================",
            "Cant.  Producto             Subtotal"
        ]

        for item in mesa.items:
            nombre = item.producto.nombre
            if item.opcion_carne:
                nombre += f" ({item.opcion_carne})"
            nombre_fmt = nombre.ljust(18)[:18]
            
            # Formato simple sin formateador externo para mantener el servicio desacoplado
            valor_entero = int(round(float(item.calcular_subtotal())))
            subtotal_str = f"${valor_entero:,}".replace(",", ".")
            
            lineas.append(f"{item.cantidad}x     {nombre_fmt}  {subtotal_str}")
            
            if item.observaciones:
                for obs in item.observaciones:
                    lineas.append(f"       * Nota: {obs}")

        total_entero = int(round(float(mesa.calcular_total())))
        total_str = f"${total_entero:,}".replace(",", ".")

        lineas.extend([
            "==================================",
            f"TOTAL COBRADO:        {total_str}",
            "==================================",
            "    ¡Gracias por su preferencia!  "
        ])
        return "\n".join(lineas)

    @staticmethod
    def generar_comanda_area(mesa: Mesa, area_destino: str) -> str | None:
        """Filtra y genera la comanda de producción para una zona específica (Cocina o Carnes)."""
        # Filtrar solo los ítems pertenecientes al área solicitada
        items_filtrados = [
            item for item in mesa.items 
            if item.producto.area_impresion.lower() == area_destino.lower()
        ]

        # Si la mesa no tiene productos para esta área, no se imprime nada
        if not items_filtrados:
            return None

        titulo_area = f"COMANDA - ZONA DE {area_destino.upper()}"
        lineas = [
            "----------------------------------",
            f"       {titulo_area}              ",
            f"Mesa: {mesa.id}",
            "----------------------------------",
            "Cant.  Producto / Especificación"
        ]

        for item in items_filtrados:
            linea_prod = f"{item.cantidad}x     {item.producto.nombre}"
            if item.opcion_carne:
                linea_prod += f" [{item.opcion_carne}]"
            lineas.append(linea_prod)

            if item.observaciones:
                for obs in item.observaciones:
                    lineas.append(f"       >> NOTA: {obs}")

        lineas.extend([
            "----------------------------------",
            "       FIN DE COMANDA             "
        ])
        return "\n".join(lineas)