import customtkinter as ctk
from tkinter import messagebox
from controllers.main_controller import MainController
from utils.formatters import formatear_cop
from models.pedido import Producto

class OrderWindow(ctk.CTkToplevel):
    """Ventana emergente encargada de la adición de productos, selección de carnes y notas."""

    def __init__(self, parent, controlador: MainController, id_mesa: str | int):
        super().__init__(parent)
        self.controlador: MainController = controlador
        self.id_mesa: str | int = id_mesa

        self.title(f"Gestión de Pedido - Mesa {self.id_mesa}")
        self.geometry("980x650")
        
        self.transient(parent)
        self.grab_set()
        
        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        """Construye las secciones visuales: Menú, Ticket en vivo y accesos rápidos."""
        self.label_mesa = ctk.CTkLabel(
            self, 
            text=f"SISTEMA DE PEDIDOS - MESA {self.id_mesa}", 
            font=("Arial", 20, "bold")
        )
        self.label_mesa.pack(pady=10)

        self.frame_cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cuerpo.pack(fill="both", expand=True, padx=20, pady=5)

        # --- COLUMNA IZQUIERDA: MENÚ DE PRODUCTOS ---
        self.frame_izquierdo = ctk.CTkFrame(self.frame_cuerpo, width=460)
        self.frame_izquierdo.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.tabview_menu = ctk.CTkTabview(self.frame_izquierdo, height=450)
        self.tabview_menu.pack(padx=10, pady=10, fill="both", expand=True)

        menu_agrupado = self.controlador.obtener_menu_agrupado()
        for categoria, productos in menu_agrupado.items():
            self.tabview_menu.add(categoria)
            frame_scroll = ctk.CTkScrollableFrame(self.tabview_menu.tab(categoria))
            frame_scroll.pack(fill="both", expand=True, padx=5, pady=5)

            for producto in productos:
                self._crear_fila_menu(frame_scroll, producto)

        # --- COLUMNA DERECHA: TICKET E INSPECCIÓN DE LA CUENTA ---
        self.frame_derecho = ctk.CTkFrame(self.frame_cuerpo, width=450)
        self.frame_derecho.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Encabezado del ticket con botón rápido de Icopor
        self.frame_head_ticket = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_head_ticket.pack(fill="x", padx=10, pady=5)

        self.lbl_titulo_ticket = ctk.CTkLabel(self.frame_head_ticket, text="Consumo Actual", font=("Arial", 16, "bold"))
        self.lbl_titulo_ticket.pack(side="left", padx=5)

        # Botón rápido para agregar Icopor (Módulo 3)
        self.btn_rapido_icopor = ctk.CTkButton(
            self.frame_head_ticket, text="+ Icopor Rápido", width=110, height=26,
            fg_color="#e67e22", hover_color="#d35400", font=("Arial", 11, "bold"),
            command=self._agregar_icopor_rapido
        )
        self.btn_rapido_icopor.pack(side="right", padx=5)

        # Contenedor dinámico con scroll para ver las filas del pedido
        self.frame_items_pedido = ctk.CTkScrollableFrame(self.frame_derecho, height=380)
        self.frame_items_pedido.pack(fill="both", expand=True, padx=10, pady=5)

        # Panel inferior para el total monetario y botón de facturar
        self.frame_total = ctk.CTkFrame(self.frame_derecho, height=60, fg_color="transparent")
        self.frame_total.pack(fill="x", side="bottom", padx=10, pady=10)

        self.lbl_total = ctk.CTkLabel(self.frame_total, text="TOTAL: $0", font=("Arial", 18, "bold"), anchor="w")
        self.lbl_total.pack(side="left", padx=10)

        self.btn_facturar = ctk.CTkButton(
            self.frame_total, text="Facturar y Cerrar", font=("Arial", 13, "bold"),
            fg_color="#27ae60", hover_color="#219653", command=self._procesar_facturacion
        )
        self.btn_facturar.pack(side="right", padx=10)

        self._actualizar_vista_ticket()

    def _crear_fila_menu(self, contenedor, producto: Producto) -> None:
        """Genera un renglón en el menú izquierdo."""
        frame_fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        frame_fila.pack(fill="x", pady=4, padx=5)

        texto_item = f"{producto.nombre}  -  {formatear_cop(producto.precio)}"
        lbl_producto = ctk.CTkLabel(frame_fila, text=texto_item, font=("Arial", 13))
        lbl_producto.pack(side="left", padx=5)

        btn_add = ctk.CTkButton(
            frame_fila, text="+ Añadir", width=70, height=24, font=("Arial", 11, "bold"),
            command=lambda p=producto: self._procesar_adicion_producto(p)
        )
        btn_add.pack(side="right", padx=5)

    def _procesar_adicion_producto(self, producto: Producto) -> None:
        """Determina si requiere diálogo de opción de carne antes de agregar al pedido."""
        if producto.requiere_configuracion_carne:
            self._abrir_dialogo_opcion_carne(producto)
        else:
            self._añadir_producto_a_mesa(producto, opcion_carne=None)

    def _abrir_dialogo_opcion_carne(self, producto: Producto) -> None:
        """Despliega una ventana emergente para elegir la opción de carne requerida."""
        modal_carne = ctk.CTkToplevel(self)
        modal_carne.title("Opción de Carne")
        modal_carne.geometry("350x250")
        modal_carne.transient(self)
        modal_carne.grab_set()

        lbl_tit = ctk.CTkLabel(modal_carne, text=f"Seleccione tipo de carne para:\n{producto.nombre}", font=("Arial", 14, "bold"))
        lbl_tit.pack(pady=15)

        opciones = ["Trifásico", "Mixto", "Solo Res", "Solo Cerdo"]

        for opc in opciones:
            btn = ctk.CTkButton(
                modal_carne, text=opc, font=("Arial", 12, "bold"),
                command=lambda o=opc: [
                    self._añadir_producto_a_mesa(producto, opcion_carne=o),
                    modal_carne.destroy()
                ]
            )
            btn.pack(fill="x", padx=30, pady=4)

    def _añadir_producto_a_mesa(self, producto: Producto, opcion_carne: str | None = None, observacion: str | None = None) -> None:
        """Impacta la memoria RAM y guarda inmediatamente en el archivo JSON."""
        mesas = self.controlador.obtener_todas_las_mesas()
        if self.id_mesa in mesas:
            mesa = mesas[self.id_mesa]
            mesa.agregar_producto(producto, cantidad=1, opcion_carne=opcion_carne, observacion=observacion)
            self.controlador.servicio_json.guardar_estado(mesas)
            self._actualizar_vista_ticket()

    def _actualizar_vista_ticket(self) -> None:
        """Limpia y redibuja la lista de consumos con soporte para notas y tipo de carne."""
        for widget in self.frame_items_pedido.winfo_children():
            widget.destroy()

        mesas = self.controlador.obtener_todas_las_mesas()
        if self.id_mesa not in mesas:
            return
            
        mesa_actual = mesas[self.id_mesa]

        for idx, item in enumerate(mesa_actual.items):
            frame_item = ctk.CTkFrame(self.frame_items_pedido)
            frame_item.pack(fill="x", pady=4, padx=2)

            # Texto descriptivo con opción de carne si aplica
            texto_base = f"{item.cantidad}x {item.producto.nombre}"
            if item.opcion_carne:
                texto_base += f" ({item.opcion_carne})"
            texto_base += f" - {formatear_cop(item.calcular_subtotal())}"

            lbl_info = ctk.CTkLabel(frame_item, text=texto_base, font=("Arial", 12, "bold"), anchor="w")
            lbl_info.pack(fill="x", padx=10, pady=(4, 0))

            # Si el ítem registra observaciones/notas, se listan abajo en texto secundario
            if item.observaciones:
                obs_text = "   Notas: " + ", ".join(item.observaciones)
                lbl_obs = ctk.CTkLabel(frame_item, text=obs_text, font=("Arial", 10, "italic"), text_color="#f39c12", anchor="w")
                lbl_obs.pack(fill="x", padx=10, pady=(0, 2))

            # Fila de botones de control (+ / - / 📝 Nota)
            frame_ctrls = ctk.CTkFrame(frame_item, fg_color="transparent")
            frame_ctrls.pack(fill="x", padx=5, pady=2)

            btn_nota = ctk.CTkButton(
                frame_ctrls, text="📝 Nota", width=55, height=22, font=("Arial", 10, "bold"), fg_color="#8e44ad",
                command=lambda item_ref=item: self._agregar_observacion_dialogo(item_ref)
            )
            btn_nota.pack(side="left", padx=5)

            btn_menos = ctk.CTkButton(
                frame_ctrls, text="-", width=24, height=22, font=("Arial", 11, "bold"), fg_color="#e67e22",
                command=lambda p_id=item.producto.id, cant=item.cantidad, opc=item.opcion_carne: self._cambiar_cantidad_especifica(p_id, cant - 1, opc)
            )
            btn_menos.pack(side="right", padx=2)

            btn_mas = ctk.CTkButton(
                frame_ctrls, text="+", width=24, height=22, font=("Arial", 11, "bold"), fg_color="#3498db",
                command=lambda p_id=item.producto.id, cant=item.cantidad, opc=item.opcion_carne: self._cambiar_cantidad_especifica(p_id, cant + 1, opc)
            )
            btn_mas.pack(side="right", padx=2)

        self.lbl_total.configure(text=f"TOTAL: {formatear_cop(mesa_actual.calcular_total())}")

    def _agregar_observacion_dialogo(self, item_ref) -> None:
        """Abre un cuadro de entrada para agregar notas al plato (ej. 'Sin salsa')."""
        dialogo = ctk.CTkInputDialog(text=f"Agregar observación para {item_ref.producto.nombre}:", title="Nota de Cocina")
        nota = dialogo.get_input()
        if nota and nota.strip():
            item_ref.observaciones.append(nota.strip())
            mesas = self.controlador.obtener_todas_las_mesas()
            self.controlador.servicio_json.guardar_estado(mesas)
            self._actualizar_vista_ticket()

    def _cambiar_cantidad_especifica(self, producto_id: int, nueva_cantidad: int, opcion_carne: str | None) -> None:
        """Modifica la cantidad de un ítem específico considerando su opción de carne."""
        mesas = self.controlador.obtener_todas_las_mesas()
        if self.id_mesa in mesas:
            mesa = mesas[self.id_mesa]
            for item in list(mesa.items):
                if item.producto.id == producto_id and item.opcion_carne == opcion_carne:
                    if nueva_cantidad <= 0:
                        mesa.items.remove(item)
                    else:
                        item.cantidad = nueva_cantidad
                    break
            
            if not mesa.items:
                mesa.estado = "Libre"

            self.controlador.servicio_json.guardar_estado(mesas)
            self._actualizar_vista_ticket()

    def _agregar_icopor_rapido(self) -> None:
        """Busca el primer producto de categoría 'Icopor' en el menú y lo añade rápidamente."""
        productos = self.controlador.restaurante.menu
        icopor = next((p for p in productos if p.categoria == "Icopor"), None)
        if icopor:
            self._añadir_producto_a_mesa(icopor)
        else:
            messagebox.showwarning("Atención", "No se encontró ningún producto registrado en la categoría 'Icopor'. Regístrelo en el Menú.")

    def _procesar_facturacion(self) -> None:
        """Factura y cierra la mesa incluyendo detalles de carnes y notas en la tirilla."""
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
            nombre = item.producto.nombre
            if item.opcion_carne:
                nombre += f" ({item.opcion_carne})"
            nombre_formateado = nombre.ljust(18)[:18]
            lineas_ticket.append(f"{item.cantidad}x     {nombre_formateado}  {formatear_cop(item.calcular_subtotal())}")
            
            # Si tiene notas, se imprimen debajo del producto en el ticket
            if item.observaciones:
                for obs in item.observaciones:
                    lineas_ticket.append(f"       * Nota: {obs}")

        lineas_ticket.append("==================================")
        lineas_ticket.append(f"TOTAL COBRADO:        {formatear_cop(mesa_actual.calcular_total())}")
        lineas_ticket.append("==================================")
        lineas_ticket.append("    ¡Gracias por su preferencia!  ")
        
        texto_final_ticket = "\n".join(lineas_ticket)

        messagebox.showinfo(f"Factura Emitida - Mesa {self.id_mesa}", texto_final_ticket)
        self.controlador.liberar_mesa(self.id_mesa)
        self.destroy()