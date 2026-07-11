import json
import os
from models.pedido import Mesa, ItemPedido, Producto

class JsonService:
    """Servicio encargado de guardar y cargar el estado de las mesas en un archivo JSON."""

    def __init__(self, ruta_archivo: str = "mesas_data.json"):
        self.ruta_archivo: str = ruta_archivo

    def guardar_estado(self, mesas: dict[str | int, Mesa]) -> None:
        """Convierte el diccionario de objetos Mesa a formato JSON y lo escribe en el disco."""
        datos_serializados = {}

        for id_mesa, mesa in mesas.items():
            # Mapeamos la estructura de la mesa a tipos de datos básicos (dict, list, str)
            datos_serializados[str(id_mesa)] = {
                "id": mesa.id,
                "estado": mesa.estado,
                "items": [
                    {
                        "producto_id": item.producto.id,
                        "nombre": item.producto.nombre,
                        "precio": item.producto.precio,
                        "categoria": item.producto.categoria,
                        "cantidad": item.cantidad
                    }
                    for item in mesa.items
                ]
            }

        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos_serializados, archivo, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error crítico al guardar el archivo JSON: {e}")

    def cargar_estado(self, menu_disponible: list[Producto]) -> dict[str | int, Mesa]:
        """Lee el archivo JSON y reconstruye el diccionario dinámico de objetos Mesa."""
        mesas_reconstruidas: dict[str | int, Mesa] = {}

        # Si el archivo no existe, retornamos un contenedor vacío para que el sistema cree las por defecto
        if not os.path.exists(self.ruta_archivo):
            return mesas_reconstructed

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                datos_json = json.load(archivo)

            for id_str, datos_mesa in datos_json.items():
                # El ID del diccionario JSON siempre es un string, intentamos convertirlo a int si es numérico
                id_actual = int(id_str) if id_str.isdigit() else id_str
                
                # Instanciamos un objeto Mesa real en memoria RAM
                nueva_mesa = Mesa(datos_mesa["id"])
                nueva_mesa.estado = datos_mesa["estado"]

                # Reconstruimos cada ítem del pedido de esa mesa
                for datos_item in datos_mesa["items"]:
                    prod = Producto(
                        datos_item["producto_id"],
                        datos_item["nombre"],
                        datos_item["precio"],
                        datos_item["categoria"]
                    )
                    # Añadimos el ítem directo a la lista de la mesa
                    nueva_mesa.items.append(ItemPedido(prod, datos_item["cantidad"]))

                mesas_reconstruidas[id_actual] = nueva_mesa

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Advertencia: Archivo JSON corrupto o inválido. Iniciando vacío. Error: {e}")
            
        return mesas_reconstruidas