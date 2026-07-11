class Producto:
    """Representa un producto individual dentro del menú del restaurante."""
    
    def __init__(self, id_producto: int, nombre: str, precio: float, categoria: str):
        self.id: int = id_producto
        self.nombre: str = nombre
        self.precio: float = precio
        self.categoria: str = categoria  # Ejemplo: 'Bebidas', 'Carnes', 'Platillos'


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
    """Clase contenedora maestra que gestiona el menú fijo y las mesas dinámicas."""
    
    def __init__(self):
        # Diccionario dinámico para soportar infinitas mesas {id_mesa: ObjetoMesa}
        self.mesas: dict[str | int, Mesa] = {}
        # Lista fija que representará el menú oficial de "El Rancho de Javi"
        self.menu: list[Producto] = []
        
        # Ejecutamos los métodos de inicialización por defecto al instanciar la clase
        self._cargar_menu_predeterminado()
        self._cargar_mesas_iniciales()

    def _cargar_menu_predeterminado(self) -> None:
        """Pobla el menú con los productos fijos divididos por categorías."""
        # Categorías requeridas: Bebidas, Carnes, Platillos
        productos_base = [
            # Bebidas
            Producto(1, "Coca-Cola", 2.50, "Bebidas"),
            Producto(2, "Jugo Natural", 3.00, "Bebidas"),
            Producto(3, "Agua Mineral", 1.50, "Bebidas"),
            # Carnes
            Producto(4, "Filete de Res", 15.00, "Carnes"),
            Producto(5, "Costillas BBQ", 14.50, "Carnes"),
            # Platillos
            Producto(6, "Tacos Especiales", 8.50, "Platillos"),
            Producto(7, "Hamburguesa de la Casa", 10.00, "Platillos")
        ]
        self.menu.extend(productos_base)

    def _cargar_mesas_iniciales(self) -> None:
        """Inicializa las primeras 5 mesas requeridas para el MVP."""
        for i in range(1, 6):
            self.agregar_nueva_mesa(i)

    def agregar_nueva_mesa(self, id_mesa: str | int) -> bool:
        """Agrega una nueva mesa de forma dinámica. Retorna False si ya existe."""
        if id_mesa in self.mesas:
            return False  # Evitamos duplicar o sobreescribir una mesa activa
        
        self.mesas[id_mesa] = Mesa(id_mesa)
        return True

    def obtener_menu_por_categoria(self) -> dict[str, list[Producto]]:
        """Organiza y retorna el menú agrupado por sus categorías para facilitar la vista."""
        categorias: dict[str, list[Producto]] = {"Bebidas": [], "Carnes": [], "Platillos": []}
        for producto in self.menu:
            if producto.categoria in categorias:
                categorias[producto.categoria].append(producto)
        return categorias