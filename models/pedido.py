class Producto:
    """Representa un producto individual dentro del menú del restaurante."""
    
    def __init__(
        self, 
        id_producto: int, 
        nombre: str, 
        precio: float, 
        categoria: str,
        area_impresion: str = "Cocina",  # Posibles valores: 'Caja', 'Cocina', 'Carnes'
        requiere_configuracion_carne: bool = False
    ):
        self.id: int = id_producto
        self.nombre: str = nombre
        self.precio: float = precio
        self.categoria: str = categoria  # 'Bebidas', 'Carnes', 'Platillos', 'Ejecutivo', 'Icopor'
        self.area_impresion: str = area_impresion
        self.requiere_configuracion_carne: bool = requiere_configuracion_carne

    def a_diccionario(self) -> dict:
        """Convierte el objeto Producto a un diccionario para serialización JSON."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio": self.precio,
            "categoria": self.categoria,
            "area_impresion": self.area_impresion,
            "requiere_configuracion_carne": self.requiere_configuracion_carne
        }

    @classmethod
    def desde_diccionario(cls, datos: dict) -> 'Producto':
        """Reconstruye un objeto Producto desde un diccionario JSON."""
        return cls(
            id_producto=datos["id"],
            nombre=datos["nombre"],
            precio=datos["precio"],
            categoria=datos["categoria"],
            area_impresion=datos.get("area_impresion", "Cocina"),
            requiere_configuracion_carne=datos.get("requiere_configuracion_carne", False)
        )


class ItemPedido:
    """Representa un producto seleccionado en un pedido junto con su cantidad."""
    
    def __init__(self, producto: Producto, cantidad: int):
        self.producto: Producto = producto
        self.cantidad: int = cantidad

    def calcular_subtotal(self) -> float:
        """Calcula el costo total de este ítem multiplicando precio por cantidad."""
        return self.producto.precio * self.cantidad
    
class Mesa:
    """Representa una mesa del restaurante, su estado y los productos consumidos."""
    
    def __init__(self, id_mesa: str | int):
        self.id: str | int = id_mesa
        self.items: list[ItemPedido] = []
        self.estado: str = "Libre"  # Los estados posibles serán: 'Libre' u 'Ocupada'

    def agregar_producto(self, producto: Producto, cantidad: int = 1) -> None:
        """Agrega un producto a la mesa o incrementa su cantidad si ya existe."""
        if cantidad <= 0:
            return

        # Buscar si el producto ya está en el pedido actual de la mesa
        for item in self.items:
            if item.producto.id == producto.id:
                item.cantidad += cantidad
                self.estado = "Ocupada"
                return

        # Si no existía, creamos un nuevo ítem y lo añadimos
        nuevo_item = ItemPedido(producto, cantidad)
        self.items.append(nuevo_item)
        self.estado = "Ocupada"

    def modificar_cantidad(self, producto_id: int, nueva_cantidad: int) -> None:
        """Modifica la cantidad de un producto. Si llega a 0, lo elimina."""
        for item in self.items:
            if item.producto.id == producto_id:
                if nueva_cantidad <= 0:
                    self.eliminar_producto(producto_id)
                else:
                    item.cantidad = nueva_cantidad
                return

    def eliminar_producto(self, producto_id: int) -> None:
        """Elimina por completo un producto del pedido de la mesa."""
        self.items = [item for item in self.items if item.producto.id != producto_id]
        
        # Si la mesa se quedó sin productos, vuelve a estar libre
        if not self.items:
            self.estado = "Libre"

    def calcular_total(self) -> float:
        """Calcula el total acumulado sumando el subtotal de todos los ítems."""
        return sum(item.calcular_subtotal() for item in self.items)

    def vaciar_pedido(self) -> None:
        """Limpia el pedido y restablece el estado de la mesa a Libre."""
        self.items = []
        self.estado = "Libre"

class Restaurante:
    """Contenedor maestro que gestiona las mesas dinámicas y el menú del establecimiento."""
    
    def __init__(self, menu_inicial: list[Producto] | None = None):
        # Diccionario dinámico {id_mesa: ObjetoMesa}
        self.mesas: dict[str | int, Mesa] = {}
        # Menú dinámico alimentado externamente desde menu_data.json
        self.menu: list[Producto] = menu_inicial if menu_inicial is not None else []
        
        self._cargar_mesas_iniciales()

    def _cargar_mesas_iniciales(self) -> None:
        """Inicializa las primeras mesas requeridas."""
        for i in range(1, 6):
            self.agregar_nueva_mesa(i)

    def agregar_nueva_mesa(self, id_mesa: str | int) -> bool:
        """Agrega una nueva mesa. Retorna False si ya existe."""
        if id_mesa in self.mesas:
            return False
        self.mesas[id_mesa] = Mesa(id_mesa)
        return True

    def obtener_menu_por_categoria(self) -> dict[str, list[Producto]]:
        """Agrupa los productos dinámicamente según las categorías presentes en el menú."""
        categorias: dict[str, list[Producto]] = {}
        for producto in self.menu:
            if producto.categoria not in categorias:
                categorias[producto.categoria] = []
            categorias[producto.categoria].append(producto)
        return categorias