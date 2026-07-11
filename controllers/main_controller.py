from models.pedido import Restaurante, Producto, Mesa
from services.json_service import JsonService

class MainController:
    """Controlador principal que conecta las reglas del negocio (Modelos) con el almacenamiento."""

    def __init__(self, restaurante: Restaurante, servicio_json: JsonService):
        self.restaurante: Restaurante = restaurante
        self.servicio_json: JsonService = servicio_json
        
        # Sincronizamos el estado de la RAM con lo que esté guardado en el disco duro
        self._cargar_estado_inicial()

    def _cargar_estado_inicial(self) -> None:
        """Intenta leer el archivo JSON para restaurar las mesas del restaurante."""
        mesas_guardadas = self.servicio_json.cargar_estado(self.restaurante.menu)
        if mesas_guardadas:
            # Si el JSON tenía datos válidos, reemplazamos las mesas vacías en la RAM
            self.restaurante.mesas = mesas_guardadas

    def obtener_todas_las_mesas(self) -> dict[str | int, Mesa]:
        """Devuelve el diccionario actual de mesas para que la Vista pueda dibujarlas."""
        return self.restaurante.mesas

    def obtener_menu_agrupado(self):
        """Devuelve el menú del restaurante organizado por categorías (Bebidas, Carnes, Platillos)."""
        return self.restaurante.obtener_menu_por_categoria()

    def agregar_producto_a_mesa(self, id_mesa: str | int, producto: Producto, cantidad: int) -> None:
        """Ordena a la mesa agregar el consumo y guarda el nuevo estado en el archivo JSON."""
        if id_mesa in self.restaurante.mesas:
            mesa = self.restaurante.mesas[id_mesa]
            mesa.agregar_producto(producto, cantidad)
            # Guardamos de inmediato el cambio en el disco local
            self.servicio_json.guardar_estado(self.restaurante.mesas)

    def modificar_cantidad_en_mesa(self, id_mesa: str | int, producto_id: int, nueva_cantidad: int) -> None:
        """Modifica las unidades de un producto en una mesa y actualiza el archivo JSON."""
        if id_mesa in self.restaurante.mesas:
            mesa = self.restaurante.mesas[id_mesa]
            mesa.modificar_cantidad(producto_id, nueva_cantidad)
            self.servicio_json.guardar_estado(self.restaurante.mesas)

    def liberar_mesa(self, id_mesa: str | int) -> None:
        """Vacía por completo los consumos de una mesa y actualiza el archivo JSON."""
        if id_mesa in self.restaurante.mesas:
            mesa = self.restaurante.mesas[id_mesa]
            mesa.vaciar_pedido()
            self.servicio_json.guardar_estado(self.restaurante.mesas)

    def crear_nueva_mesa_dinamica(self, id_mesa: str | int) -> bool:
        """Añade una mesa extra al negocio. Cumple con el requerimiento de escalabilidad."""
        exito = self.restaurante.agregar_nueva_mesa(id_mesa)
        if exito:
            self.servicio_json.guardar_estado(self.restaurante.mesas)
        return exito