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
    """Representa una línea dentro del pedido de una mesa (Producto + Cantidad)."""

    def __init__(self, producto: Producto, cantidad: int = 1):
        self.producto: Producto = producto
        self.cantidad: int = cantidad

    def calcular_subtotal(self) -> float:
        return self.producto.precio * self.cantidad

    def a_diccionario(self) -> dict:
        """Convierte la línea del pedido a un diccionario para guardar en JSON."""
        return {
            "producto_id": self.producto.id,
            "cantidad": self.cantidad
        }

    @classmethod
    def desde_diccionario(cls, datos: dict, menu_disponible: list[Producto]) -> 'ItemPedido | None':
        """Reconstruye un ItemPedido buscando el producto por su ID en el menú."""
        prod_id = datos.get("producto_id")
        cantidad = datos.get("cantidad", 1)
        
        # Buscamos el producto en el catálogo actual
        producto_encontrado = next((p for p in menu_disponible if p.id == prod_id), None)
        
        if producto_encontrado:
            return cls(producto=producto_encontrado, cantidad=cantidad)
        return None
    
class Mesa:
    """Representa una mesa del restaurante con su estado, ítems consumidos y tipo de mesa."""
    
    def __init__(self, id_mesa: str | int, es_fija: bool = False, es_vip: bool = False):
        self.id: str | int = id_mesa
        self.estado: str = "Libre"  # 'Libre' o 'Ocupada'
        self.items: list[ItemPedido] = []
        self.es_fija: bool = es_fija
        self.es_vip: bool = es_vip
        self.hora_apertura: str | None = None

    def agregar_producto(self, producto: Producto, cantidad: int = 1) -> None:
        if self.estado == "Libre":
            self.estado = "Ocupada"
            
        for item in self.items:
            if item.producto.id == producto.id:
                item.cantidad += cantidad
                return
        self.items.append(ItemPedido(producto, cantidad))

    def modificar_cantidad(self, producto_id: int, nueva_cantidad: int) -> None:
        for item in self.items:
            if item.producto.id == producto_id:
                if nueva_cantidad <= 0:
                    self.items.remove(item)
                else:
                    item.cantidad = nueva_cantidad
                break
        
        if not self.items:
            self.estado = "Libre"
            self.hora_apertura = None

    def vaciar_pedido(self) -> None:
        self.items.clear()
        self.estado = "Libre"
        self.hora_apertura = None

    def calcular_total(self) -> float:
        return sum(item.calcular_subtotal() for item in self.items)

    def a_diccionario(self) -> dict:
        return {
            "id": self.id,
            "estado": self.estado,
            "es_fija": self.es_fija,
            "es_vip": self.es_vip,
            "hora_apertura": self.hora_apertura,
            "items": [item.a_diccionario() for item in self.items]
        }

    @classmethod
    def desde_diccionario(cls, datos: dict, menu_disponible: list[Producto]) -> 'Mesa':
        mesa = cls(
            id_mesa=datos["id"],
            es_fija=datos.get("es_fija", False),
            es_vip=datos.get("es_vip", False)
        )
        mesa.estado = datos.get("estado", "Libre")
        mesa.hora_apertura = datos.get("hora_apertura", None)
        
        productos_map = {p.id: p for p in menu_disponible}
        for item_dict in datos.get("items", []):
            prod_id = item_dict["producto_id"]
            if prod_id in productos_map:
                prod = productos_map[prod_id]
                cant = item_dict["cantidad"]
                mesa.items.append(ItemPedido(prod, cant))
        return mesa


class Restaurante:
    """Contenedor maestro que gestiona las mesas y el menú."""
    
    def __init__(self, menu_inicial: list[Producto] | None = None):
        self.mesas: dict[str | int, Mesa] = {}
        self.menu: list[Producto] = menu_inicial if menu_inicial is not None else []
        
        self._cargar_mesas_iniciales()

    def _cargar_mesas_iniciales(self) -> None:
        """Inicializa las 24 mesas fijas reglamentarias."""
        for i in range(1, 25):
            self.mesas[i] = Mesa(id_mesa=i, es_fija=True, es_vip=False)

    def agregar_nueva_mesa(self, id_mesa: str | int, es_vip: bool = False) -> bool:
        """Agrega una mesa temporal (dinámica) tradicional o VIP."""
        if id_mesa in self.mesas:
            return False
        self.mesas[id_mesa] = Mesa(id_mesa=id_mesa, es_fija=False, es_vip=es_vip)
        return True

    def eliminar_mesa(self, id_mesa: str | int) -> tuple[bool, str]:
        """Elimina una mesa si no es fija y si no está ocupada."""
        if id_mesa not in self.mesas:
            return False, "La mesa no existe."
            
        mesa = self.mesas[id_mesa]
        if mesa.es_fija:
            return False, "No se pueden eliminar las 24 mesas fijas del establecimiento."
            
        if mesa.estado == "Ocupada":
            return False, "No se puede eliminar una mesa con consumos activos. Factúrela primero."
            
        del self.mesas[id_mesa]
        return True, "Mesa eliminada correctamente."

    def obtener_menu_por_categoria(self) -> dict[str, list[Producto]]:
        categorias: dict[str, list[Producto]] = {}
        for producto in self.menu:
            if producto.categoria not in categorias:
                categorias[producto.categoria] = []
            categorias[producto.categoria].append(producto)
        return categorias