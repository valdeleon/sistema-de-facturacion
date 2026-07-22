import customtkinter as ctk
from utils.formatters import formatear_cop
from controllers.main_controller import MainController

class OrderWindow(ctk.CTkToplevel):
    """Ventana emergente encargada de gestionar el menú y la inspección del pedido de la mesa."""

    def __init__(self, parent, controlador: MainController, id_mesa: str | int):
        super().__init__(parent)
        self.controlador: MainController = controlador
        self.id_mesa: str | int = id_mesa

        # Expandimos la geometría para dar espacio a la columna del ticket derecho
        self.title(f"Gestión de Pedido - Mesa {self.id_mesa}")
        self.geometry("950x600")
        
        self.transient(parent)
        self.grab_set()
        
        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        """Construye las secciones visuales divididas en dos columnas principales."""
        # Encabezado informativo general
        self.label_mesa = ctk.CTkLabel(
            self, 
            text=f"SISTEMA DE PEDIDOS - MESA {self.id_mesa}", 
            font=("Arial", 20, "bold")
        )
        self.label_mesa.pack(pady=10)

        # Contenedor maestro horizontal dividido por columnas
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

        # Panel inferior para el total monetario y el botón de facturar
        self.frame_total = ctk.CTkFrame(self.frame_derecho, height=60, fg_color="transparent")
        self.frame_total.pack(fill="x", side="bottom", padx=15, pady=15)

        self.lbl_total = ctk.CTkLabel(self.frame_total, text="TOTAL: $0.00", font=("Arial", 18, "bold"), anchor="w")
        self.lbl_total.pack(side="left", padx=10)

        # Botón corporativo para procesar el cobro y liberar la mesa (Fase 15)
        self.btn_facturar = ctk.CTkButton(
            self.frame_total,
            text="Facturar y Cerrar",
            font=("Arial", 13, "bold"),
            fg_color="#27ae60", # Verde corporativo de cobro exitoso
            hover_color="#219653",
            command=self._procesar_facturacion
        )
        self.btn_facturar.pack(side="right", padx=10)

        # Renderizamos por primera vez las filas del ticket acumulado
        self._actualizar_vista_ticket()

    def _crear_fila_menu(self, contenedor, producto) -> None:
        """Genera un renglón en el menú izquierdo para añadir productos."""
        frame_fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        frame_fila.pack(fill="x", pady=4, padx=5)

        # Usamos el formateador COP
        texto_item = f"{producto.nombre}  -  {formatear_cop(producto.precio)}"
        lbl_producto = ctk.CTkLabel(frame_fila, text=texto_item, font=("Arial", 13))
        lbl_producto.pack(side="left", padx=5)

        btn_add = ctk.CTkButton(
            frame_fila, text="+ Añadir", width=70, height=24, font=("Arial", 11, "bold"),
            command=lambda p=producto: self._añadir_producto(p)
        )
        btn_add.pack(side="right", padx=5)

    def _actualizar_vista_ticket(self) -> None:
        """Limpia y redibuja la lista de consumos de la columna derecha basada en los datos de la RAM."""
        for widget in self.frame_items_pedido.winfo_children():
            widget.destroy()

        # Obtenemos el objeto mesa real para inspeccionar sus listas internas
        mesas = self.controlador.obtener_todas_las_mesas()
        mesa_actual = mesas[self.id_mesa]

        # Fábrica de filas para el ticket de consumo
        for item in mesa_actual.items:
            frame_item = ctk.CTkFrame(self.frame_items_pedido, height=40)
            frame_item.pack(fill="x", pady=3, padx=2)

            # Información del consumo formateada en COP
            info_texto = f"{item.cantidad}x {item.producto.nombre} ({formatear_cop(item.calcular_subtotal())})"
            lbl_info = ctk.CTkLabel(frame_item, text=lbl_info_txt if 'lbl_info_txt' in locals() else info_texto, font=("Arial", 12))
            lbl_info.pack(side="left", padx=10, pady=5) 

            # Botones de control de cantidad reactivos (+ / -)
            btn_menos = ctk.CTkButton(
                frame_item, text="-", width=24, height=24, font=("Arial", 12, "bold"), fg_color="#e67e22",
                command=lambda p_id=item.producto.id, cant=item.cantidad: self._cambiar_cantidad(p_id, cant - 1)
            )
            btn_menos.pack(side="right", padx=5)

            btn_mas = ctk.CTkButton(
                frame_item, text="+", width=24, height=24, font=("Arial", 12, "bold"), fg_color="#3498db",
                command=lambda p_id=item.producto.id, cant=item.cantidad: self._cambiar_cantidad(p_id, cant + 1)
            )
            btn_mas.pack(side="right", padx=2)

        # Actualizamos la etiqueta del total formateada a dos decimales
        self.lbl_total.configure(text=f"TOTAL: {formatear_cop(mesa_actual.calcular_total())}")

    def _añadir_producto(self, producto) -> None:
        """Impacta la lógica a través del controlador y refresca el ticket de inmediato."""
        self.controlador.agregar_producto_a_mesa(self.id_mesa, producto, cantidad=1)
        self._actualizar_vista_ticket()

    def _cambiar_cantidad(self, producto_id: int, nueva_cantidad: int) -> None:
        """Modifica las unidades de un consumo y actualiza la pantalla en consecuencia."""
        self.controlador.modificar_cantidad_en_mesa(self.id_mesa, producto_id, nueva_cantidad)
        self._actualizar_vista_ticket()

    def _procesar_facturacion(self) -> None:
        """Genera el ticket en pantalla, limpia la mesa en la RAM/JSON y cierra la modal."""
        from tkinter import messagebox

        mesas = self.controlador.obtener_todas_las_mesas()
        mesa_actual = mesas[self.id_mesa]

        # Validación de seguridad corporativa: No se puede facturar una mesa vacía
        if not mesa_actual.items:
            messagebox.showwarning("Operación Inválida", "No se puede facturar una mesa que no registra consumos.")
            return

        # Estructuración visual del ticket (Simulación de impresión física)
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
            subtotal_txt = formatear_cop(item.calcular_subtotal())
            lineas_ticket.append(f"{item.cantidad}x     {nombre_formateado}  {subtotal_txt}")

        lineas_ticket.append("==================================")
        lineas_ticket.append(f"TOTAL COBRADO:        {formatear_cop(mesa_actual.calcular_total())}")
        lineas_ticket.append("==================================")
        lineas_ticket.append("    ¡Gracias por su preferencia!  ")
        
        texto_final_ticket = "\n".join(lineas_ticket)

        # 1. Mostramos el ticket impreso en pantalla
        messagebox.showinfo(f"Factura Emitida - Mesa {self.id_mesa}", texto_final_ticket)

        # 2. Ordenamos al controlador limpiar la mesa en RAM y sobreescribir el JSON
        self.controlador.liberar_mesa(self.id_mesa)

        # 3. Destruimos esta ventana emergente de forma segura
        self.destroy()