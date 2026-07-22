import json
import os
from models.pedido import Producto

class MenuService:
    """Servicio encargado de la persistencia del menú en un archivo JSON independiente."""

    def __init__(self, ruta_archivo: str = "menu_data.json"):
        self.ruta_archivo: str = ruta_archivo

    def cargar_menu(self) -> list[Producto]:
        """Carga los productos desde el JSON. Si no existe, genera el menú por defecto."""
        if not os.path.exists(self.ruta_archivo):
            return self._generar_menu_predeterminado()

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                datos_json = json.load(archivo)
                return [Producto.desde_diccionario(p) for p in datos_json]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error al leer {self.ruta_archivo}: {e}. Regenerando menú predeterminado.")
            return self._generar_menu_predeterminado()

    def guardar_menu(self, menu: list[Producto]) -> None:
        """Guarda la lista de productos actual en el archivo JSON."""
        datos_serializados = [producto.a_diccionario() for producto in menu]
        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos_serializados, archivo, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error crítico al guardar {self.ruta_archivo}: {e}")

    def _generar_menu_predeterminado(self) -> list[Producto]:
        """Crea la estructura inicial del menú con precios en Pesos Colombianos ($COP)."""
        menu_inicial = [
            # Bebidas
            Producto(1, "Gaseosa 350ml", 3500, "Bebidas", area_impresion="Caja"),
            Producto(2, "Jugo Natural", 5000, "Bebidas", area_impresion="Cocina"),
            Producto(3, "Agua Mineral", 2500, "Bebidas", area_impresion="Caja"),
            
            # Carnes
            Producto(4, "Carne Llanera 300g", 28000, "Carnes", area_impresion="Carnes", requiere_configuracion_carne=True),
            Producto(5, "Costillas BBQ", 32000, "Carnes", area_impresion="Carnes", requiere_configuracion_carne=False),
            
            # Platillos
            Producto(6, "Picada Familiar", 45000, "Platillos", area_impresion="Cocina"),
            Producto(7, "Hamburguesa de la Casa", 18000, "Platillos", area_impresion="Cocina"),
            
            # Ejecutivo
            Producto(8, "Ejecutivo del Día", 16000, "Ejecutivo", area_impresion="Cocina"),
            
            # Icopor
            Producto(9, "Icopor Pequeño", 1000, "Icopor", area_impresion="Caja"),
            Producto(10, "Icopor Grande", 2000, "Icopor", area_impresion="Caja")
        ]
        
        self.guardar_menu(menu_inicial)
        return menu_inicial