import json
import os
from models.pedido import Mesa, Producto

class JsonService:
    """Servicio de persistencia encargado de guardar y recuperar el estado de las mesas."""

    def __init__(self, ruta_archivo: str = "mesas_data.json"):
        self.ruta_archivo: str = ruta_archivo

    def guardar_estado(self, mesas: dict[str | int, Mesa]) -> None:
        """Serializa el diccionario completo de mesas y lo guarda en el archivo JSON."""
        datos_serializados = {
            str(id_mesa): mesa.a_diccionario() 
            for id_mesa, mesa in mesas.items()
        }
        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos_serializados, archivo, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error crítico al guardar {self.ruta_archivo}: {e}")

    def cargar_estado(self, menu_disponible: list[Producto]) -> dict[str | int, Mesa] | None:
        """Carga las mesas desde el archivo JSON preservando sus atributos (es_fija, es_vip, items)."""
        if not os.path.exists(self.ruta_archivo):
            return None

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                datos_json = json.load(archivo)
                
            mesas_reconstruidas: dict[str | int, Mesa] = {}
            for id_str, mesa_dict in datos_json.items():
                # Convertimos la clave a entero si es un dígito
                key = int(id_str) if id_str.isdigit() else id_str
                
                # Usamos el constructor desde_diccionario que respeta es_fija y es_vip
                mesa_obj = Mesa.desde_diccionario(mesa_dict, menu_disponible)
                mesas_reconstruidas[key] = mesa_obj

            return mesas_reconstruidas
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error al leer {self.ruta_archivo}: {e}. Se generará el estado por defecto.")
            return None