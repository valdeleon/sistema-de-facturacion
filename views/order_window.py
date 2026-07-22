import customtkinter as ctk
from controllers.main_controller import MainController
from utils.formatters import formatear_cop

class OrderWindow(ctk.CTkToplevel):
    """Ventana emergente encargada de gestionar el menú y la inspección del pedido de la mesa."""

    def __init__(self, parent, controlador: MainController, id_mesa: str | int):
        super().__init__(parent)
        self.controlador: MainController = controlador
        self.id_mesa: str | int = id_mesa

        self.title(f"Gestión de Pedido - Mesa {self.id_mesa}")
        self.geometry("950x600")
        
        self.transient(parent)
        self.grab_set()
        
        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        """Construye las secciones visuales divididas en dos columnas principales."""
        self.label_mesa = ctk.CTkLabel(
            self, 
            text=f"SISTEMA DE PEDIDOS - MESA {self.id_mesa}", 
            font=("Arial", 20, "bold")
        )
        self.label_mesa.pack(pady=10)

        self.frame_cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cuerpo.pack(fill="both", expand=True, padx=20, pady=10)

        # --- COLUMNA IZQUIERDA: MENÚ DE PRODUCTOS ---
        self.frame_izquierdo = ctk.CTkFrame(self.frame_cuerpo, width=450)
        self.frame_izquierdo.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.tabview_menu = ctk.CTkTabview(self.frame_izquierdo, height=480)
        self.tabview_menu.pack(padx=10, pady=10, fill="both", expand=True)

        menu_agrupado = self.controlador.obtener_menu_agrupado()
        for categoria, productos in menu_agrupado.items():
            self.tabview_menu.add(categoria)
            frame_scroll = ctk.CTkScrollableFrame(self.tabview_menu.tab(categoria))
            frame_scroll.pack(fill="both", expand=True, padx=5, pady=5)

            for producto in productos:
                self._crear_fila_menu(frame_scroll, producto)

        # --- COLUMNA DERECHA: TICKET E INSPECCIÓN DE LA CUENTA ---
        self.frame_derecho = ctk.CTkFrame(self.frame_cuerpo, width=430)
        self.frame_derecho.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.lbl_titulo_ticket = ctk.CTkLabel(self.frame_derecho, text="Consumo Actual", font=("Arial", 16, "bold"))
        self.lbl_titulo_ticket.pack(pady=10)

        # Contenedor dinámico con scroll para ver las filas del pedido
        self.frame_items_pedido = ctk.CTkScrollableFrame(self.frame_derecho, height=350)
        self.frame_items_pedido.pack(fill="both", expand=True, padx=15, pady=5)

        # Panel inferior para el total monetario
        self.frame_total = ctk.CTkFrame(self.frame_derecho, height=60, fg_color="transparent")
        self.frame_total.pack(fill="x", side="bottom", padx=15, pady=15)

        self.lbl_total = ctk.CTkLabel(self.frame_total, text="TOTAL: $0", font=("Arial", 18, "bold"), anchor="w")
        self.lbl_total.pack(side="left", padx=10)

        self.btn_facturar = ctk.CTkButton(
            self.frame_total,
            text="Facturar y Cerrar",
            font=("Arial", 13, "bold"),
            fg_color="#27ae60",
            hover_color="#219653",
            command=self._procesar_facturacion
        )
        self.btn_facturar.pack(side="right", padx=10)

        # Cargar los datos actuales en el ticket derecho
        self._actualizar_vista_ticket()

    def _crear_fila_menu(self, contenedor, producto) -> None:
        """Genera un renglón en el menú izquierdo para añadir productos."""
        frame_fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        frame_fila.pack(fill="x", pady=4, padx=5)

        texto_item = f"{producto.nombre}  -  {formatear_cop(producto.precio)}"
        lbl_producto = ctk.CTkLabel(frame_fila, text=texto_item, font=("Arial", 13))
        lbl_producto.pack(side="left", padx=5)

        # Vinculación explícita con captura de variable por defecto p=producto
        btn_add = ctk.CTkButton(
            frame_fila, text="+ Añadir", width=70, height=24, font=("Arial", 11, "bold"),
            command=lambda p=producto: self._añadir_producto(p)
        )
        btn_add.pack(side="right", padx=5)

    def _actualizar_vista_ticket(self) -> None:
        """Limpia y redibuja la lista de consumos de la columna derecha basada en los datos de la RAM."""
        # 1. Limpiar widgets anteriores
        for widget in self.frame_items_pedido.winfo_children():
            widget.destroy()

        # 2. Obtenemos la mesa real del controlador
        mesas = self.controlador.obtener_todas_las_mesas()
        
        if self.id_mesa not in mesas:
            return
            
        mesa_actual = mesas[self.id_mesa]

        # 3. Dibujar filas de productos agregados
        for item in mesa_actual.items:
            frame_item = ctk.CTkFrame(self.frame_items_pedido, height=40)
            frame_item.pack(fill="x", pady=3, padx=2)

            info_texto = f"{item.cantidad}x {item.producto.nombre} ({formatear_cop(item.calcular_subtotal())})"
            lbl_info = ctk.CTkLabel(frame_item, text=info_texto, font=("Arial", 12))
            lbl_info.pack(side="left", padx=10, pady=5)

            # Botón "-"
            btn_menos = ctk.CTkButton(
                frame_item, text="-", width=24, height=24, font=("Arial", 12, "bold"), fg_color="#e67e22",
                command=lambda p_id=item.producto.id, cant=item.cantidad: self._cambiar_cantidad(p_id, cant - 1)
            )
            btn_menos.pack(side="right", padx=5)

            # Botón "+"
            btn_mas = ctk.CTkButton(
                frame_item, text="+", width=24, height=24, font=("Arial", 12, "bold"), fg_color="#3498db",
                command=lambda p_id=item.producto.id, cant=item.cantidad: self._cambiar_cantidad(p_id, cant + 1)
            )
            btn_mas.pack(side="right", padx=2)

        # 4. Actualizar total formateado a Pesos Colombianos
        self.lbl_total.configure(text=f"TOTAL: {formatear_cop(mesa_actual.calcular_total())}")

    def _añadir_producto(self, producto) -> None:
        """Agrega producto, fuerza guardado en JSON y refresca visualmente la columna derecha."""
        self.controlador.agregar_producto_a_mesa(self.id_mesa, producto, cantidad=1)
        self.controlador.servicio_json.guardar_estado(self.controlador.restaurante.mesas)
        self._actualizar_vista_ticket()

    def _cambiar_cantidad(self, producto_id: int, nueva_cantidad: int) -> None:
        """Modifica cantidad, fuerza guardado en JSON y refresca visualmente la columna derecha."""
        self.controlador.modificar_cantidad_en_mesa(self.id_mesa, producto_id, nueva_cantidad)
        self.controlador.servicio_json.guardar_estado(self.controlador.restaurante.mesas)
        self._actualizar_vista_ticket()

    def _procesar_facturacion(self) -> None:
        """Factura y cierra la cuenta."""
        from tkinter import messagebox

        mesas = self.controlador.obtener_todas_las_mesas()
        mesa_actual = mesas[self.id_mesa]

        if not mesa_actual.items:
            messagebox.showwarning("Operación Inválida", "No se puede facturar una mesa que no registra consumos.")
            return

        lineas_ticket = [
            "==================================",
            "        EL RANCHO DE JAVI         ",
            "     TICKET DE FACTURACIÓN        ",
            f"Mesa: {self.id_mesa}",
            "==================================",
            "Cant.  Producto             Subtotal"
        ]

        for item in mesa_actual.items:
            nombre_formateado = item.producto.nombre.ljust(18)[:18]
            lineas_ticket.append(f"{item.cantidad}x     {nombre_formateado}  {formatear_cop(item.calcular_subtotal())}")

        lineas_ticket.append("==================================")
        lineas_ticket.append(f"TOTAL COBRADO:        {formatear_cop(mesa_actual.calcular_total())}")
        lineas_ticket.append("==================================")
        lineas_ticket.append("    ¡Gracias por su preferencia!  ")
        
        texto_final_ticket = "\n".join(lineas_ticket)

        messagebox.showinfo(f"Factura Emitida - Mesa {self.id_mesa}", texto_final_ticket)
        self.controlador.liberar_mesa(self.id_mesa)
        self.destroy()