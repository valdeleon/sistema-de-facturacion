from models.pedido import Restaurante, Producto, Mesa
from services.json_service import JsonService
from services.menu_service import MenuService

class MainController:
    """Controlador principal que coordina los servicios de persistencia y el modelo Restaurante."""

    def __init__(self, restaurante: Restaurante, servicio_json: JsonService, servicio_menu: MenuService):
        self.restaurante: Restaurante = restaurante
        self.servicio_json: JsonService = servicio_json
        self.servicio_menu: MenuService = servicio_menu
        
        # Cargar el menú persistente al iniciar
        self.actualizar_menu_desde_disco()
        # Restaurar estado de las mesas
        self._cargar_estado_inicial()

    def actualizar_menu_desde_disco(self) -> None:
        """Lee menu_data.json y actualiza la lista de productos del restaurante."""
        self.restaurante.menu = self.servicio_menu.cargar_menu()

    def _cargar_estado_inicial(self) -> None:
        """Restaura el estado de las mesas desde mesas_data.json."""
        mesas_guardadas = self.servicio_json.cargar_estado(self.restaurante.menu)
        if mesas_guardadas:
            self.restaurante.mesas = mesas_guardadas

    def obtener_todas_las_mesas(self) -> dict[str | int, Mesa]:
        return self.restaurante.mesas

    def obtener_menu_agrupado(self) -> dict[str, list[Producto]]:
        return self.restaurante.obtener_menu_por_categoria()

    def agregar_producto_a_mesa(self, id_mesa: str | int, producto: Producto, cantidad: int) -> None:
        if id_mesa in self.restaurante.mesas:
            mesa = self.restaurante.mesas[id_mesa]
            mesa.agregar_producto(producto, cantidad)
            self.servicio_json.guardar_estado(self.restaurante.mesas)

    def modificar_cantidad_en_mesa(self, id_mesa: str | int, producto_id: int, nueva_cantidad: int) -> None:
        if id_mesa in self.restaurante.mesas:
            mesa = self.restaurante.mesas[id_mesa]
            mesa.modificar_cantidad(producto_id, nueva_cantidad)
            self.servicio_json.guardar_estado(self.restaurante.mesas)

    def liberar_mesa(self, id_mesa: str | int) -> None:
        if id_mesa in self.restaurante.mesas:
            mesa = self.restaurante.mesas[id_mesa]
            mesa.vaciar_pedido()
            self.servicio_json.guardar_estado(self.restaurante.mesas)

    def crear_nueva_mesa_dinamica(self, id_mesa: str | int) -> bool:
        exito = self.restaurante.agregar_nueva_mesa(id_mesa)
        if exito:
            self.servicio_json.guardar_estado(self.restaurante.mesas)
        return exito
    
    def crear_nueva_mesa_dinamica(self, id_mesa: str | int, es_vip: bool = False) -> bool:
        """Añade una mesa temporal tradicional o VIP."""
        exito = self.restaurante.agregar_nueva_mesa(id_mesa, es_vip=es_vip)
        if exito:
            self.servicio_json.guardar_estado(self.restaurante.mesas)
        return exito

    def eliminar_mesa_dinamica(self, id_mesa: str | int) -> tuple[bool, str]:
        """Elimina una mesa dinámica si cumple las condiciones de seguridad."""
        exito, mensaje = self.restaurante.eliminar_mesa(id_mesa)
        if exito:
            self.servicio_json.guardar_estado(self.restaurante.mesas)
        return exito, mensaje