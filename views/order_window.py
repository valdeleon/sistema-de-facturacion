import customtkinter as ctk
from controllers.main_controller import MainController

class OrderWindow(ctk.CTkToplevel):
    """Ventana emergente encargada de gestionar el pedido de una mesa específica."""

    def __init__(self, parent, controlador: MainController, id_mesa: str | int):
        super().__init__(parent)
        self.controlador: MainController = controlador
        self.id_mesa: str | int = id_mesa

        # Configuración visual de la modal emergente
        self.title(f"Gestión de Pedido - Mesa {self.id_mesa}")
        self.geometry("500x600")
        
        # Buenas prácticas de UX: Forzar el foco sobre esta ventana y encima de la principal
        self.transient(parent)
        self.grab_set()
        
        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        """Construye las secciones visuales: Título corporativo y el Menú de categorías."""
        # Encabezado informativo
        self.label_mesa = ctk.CTkLabel(
            self, 
            text=f"MESA {self.id_mesa} - ADICIÓN DE PRODUCTOS", 
            font=("Arial", 18, "bold")
        )
        self.label_mesa.pack(pady=15)

        # Componente avanzado de pestañas organizadas (Pestañas solicitadas en requerimientos)
        self.tabview_menu = ctk.CTkTabview(self, width=460, height=480)
        self.tabview_menu.pack(padx=20, pady=10, fill="both", expand=True)

        # Le pedimos al controlador los productos separados matemáticamente en RAM por categoría
        menu_agrupado = self.controlador.obtener_menu_agrupado()

        # Construimos dinámicamente las pestañas basadas en las categorías del modelo
        for categoria, productos in menu_agrupado.items():
            # Crear la pestaña física
            self.tabview_menu.add(categoria)
            
            # Contenedor interno para que los productos de esta pestaña tengan scrollbar
            frame_scroll = ctk.CTkScrollableFrame(self.tabview_menu.tab(categoria))
            frame_scroll.pack(fill="both", expand=True, padx=5, pady=5)

            # Fábrica visual de ítems del menú
            for producto in productos:
                self._crear_fila_producto(frame_scroll, producto)

    def _crear_fila_producto(self, contenedor, producto) -> None:
        """Genera una fila estilizada con el nombre, precio y un botón rápido de agregar."""
        frame_fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        frame_fila.pack(fill="x", pady=6, padx=5)

        # Nombre y precio formateado limpiamente
        texto_item = f"{producto.nombre}  -  ${producto.precio:.2f}"
        lbl_producto = ctk.CTkLabel(frame_fila, text=texto_item, font=("Arial", 14))
        lbl_producto.pack(side="left", padx=5)

        # Botón de inserción inmediata en RAM y JSON a través de lambda
        btn_add = ctk.CTkButton(
            frame_fila,
            text="+ Añadir",
            width=70,
            height=26,
            font=("Arial", 12, "bold"),
            command=lambda p=producto: self._añadir_producto_a_cuenta(p)
        )
        btn_add.pack(side="right", padx=5)

    def _añadir_producto_a_cuenta(self, producto) -> None:
        """Llama al controlador para impactar la memoria RAM y guardar el archivo JSON."""
        # Por simplicidad del botón directo, agregamos de 1 en 1 unidad
        self.controlador.agregar_producto_a_mesa(self.id_mesa, producto, cantidad=1)
        print(f"DEBUG: Se añadió 1x {producto.nombre} a la Mesa {self.id_mesa}")