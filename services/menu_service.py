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
        """Crea la estructura inicial del menú con categorías y áreas de impresión asignadas."""
        menu_inicial = [
            # Bebidas (Área: Caja / Cocina)
            Producto(1, "Coca-Cola", 2.50, "Bebidas", area_impresion="Caja"),
            Producto(2, "Jugo Natural", 3.00, "Bebidas", area_impresion="Cocina"),
            Producto(3, "Agua Mineral", 1.50, "Bebidas", area_impresion="Caja"),
            
            # Carnes (Área: Carnes - Requieren configuración)
            Producto(4, "Carne Llanera 300g", 15.00, "Carnes", area_impresion="Carnes", requiere_configuracion_carne=True),
            Producto(5, "Costillas BBQ", 14.50, "Carnes", area_impresion="Carnes", requiere_configuracion_carne=False),
            
            # Platillos (Área: Cocina)
            Producto(6, "Tacos Especiales", 8.50, "Platillos", area_impresion="Cocina"),
            Producto(7, "Hamburguesa de la Casa", 10.00, "Platillos", area_impresion="Cocina"),
            
            # Ejecutivo (Menú especial)
            Producto(8, "Ejecutivo del Día", 12.00, "Ejecutivo", area_impresion="Cocina"),
            
            # Icopor (Empaques)
            Producto(9, "Icopor Pequeño", 0.50, "Icopor", area_impresion="Caja"),
            Producto(10, "Icopor Grande", 1.00, "Icopor", area_impresion="Caja")
        ]
        
        self.guardar_menu(menu_inicial)
        return menu_inicial