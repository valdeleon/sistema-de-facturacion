import customtkinter as ctk
from tkinter import messagebox
from controllers.main_controller import MainController
from utils.formatters import formatear_cop
from models.pedido import Producto
from services.print_service import PrintService

class OrderWindow(ctk.CTkToplevel):
    """Ventana emergente encargada de la adición de productos, selección de carnes y botonera de impresión."""

    def __init__(self, parent, controlador: MainController, id_mesa: str | int):
        super().__init__(parent)
        self.controlador: MainController = controlador
        self.id_mesa: str | int = id_mesa

        self.title(f"Gestión de Pedido - Mesa {self.id_mesa}")
        self.geometry("980x680")
        
        self.transient(parent)
        self.grab_set()
        
        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        """Construye las secciones visuales: Menú, Ticket en vivo y Botonera de Operaciones."""
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
        self.frame_derecho = ctk.CTkFrame(self.frame_cuerpo, width=450)
        self.frame_derecho.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Encabezado del ticket con botón rápido de Icopor
        self.frame_head_ticket = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_head_ticket.pack(fill="x", padx=10, pady=5)

        self.lbl_titulo_ticket = ctk.CTkLabel(self.frame_head_ticket, text="Consumo Actual", font=("Arial", 16, "bold"))
        self.lbl_titulo_ticket.pack(side="left", padx=5)

        self.btn_rapido_icopor = ctk.CTkButton(
            self.frame_head_ticket, text="+ Icopor Rápido", width=110, height=26,
            fg_color="#e67e22", hover_color="#d35400", font=("Arial", 11, "bold"),
            command=self._agregar_icopor_rapido
        )
        self.btn_rapido_icopor.pack(side="right", padx=5)

        # Contenedor dinámico con scroll para ver las filas del pedido
        self.frame_items_pedido = ctk.CTkScrollableFrame(self.frame_derecho, height=320)
        self.frame_items_pedido.pack(fill="both", expand=True, padx=10, pady=5)

        # Total Monetario
        self.lbl_total = ctk.CTkLabel(self.frame_derecho, text="TOTAL: $0", font=("Arial", 18, "bold"), anchor="e")
        self.lbl_total.pack(fill="x", padx=15, pady=5)

        # --- PANEL INFERIOR: BOTONERA DE LAS 4 IMPRESIONES Y ACCIONES ---
        self.frame_acciones = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_acciones.pack(fill="x", side="bottom", padx=10, pady=10)

        # Fila 1 de Botones: Enviar a Producción y Pre-cuenta
        self.btn_enviar_cocina = ctk.CTkButton(
            self.frame_acciones, text="📤 Enviar Cocina/Parrilla", font=("Arial", 11, "bold"),
            fg_color="#3498db", hover_color="#2980b9", command=self._enviar_a_cocina_y_parrilla
        )
        self.btn_enviar_cocina.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        self.btn_precuenta = ctk.CTkButton(
            self.frame_acciones, text="🖨️ Pre-cuenta (Caja)", font=("Arial", 11, "bold"),
            fg_color="#e67e22", hover_color="#d35400", command=self._imprimir_precuenta_caja
        )
        self.btn_precuenta.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        # Fila 2 de Botones: Guardar Pedido y Facturar/Cerrar
        self.btn_guardar = ctk.CTkButton(
            self.frame_acciones, text="💾 Guardar Pedido", font=("Arial", 11, "bold"),
            fg_color="#7f8c8d", hover_color="#707b7c", command=self._guardar_pedido_y_cerrar
        )
        self.btn_guardar.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

        self.btn_facturar = ctk.CTkButton(
            self.frame_acciones, text="✅ Facturar y Cerrar", font=("Arial", 11, "bold"),
            fg_color="#27ae60", hover_color="#219653", command=self._procesar_facturacion
        )
        self.btn_facturar.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        # Distribuir ambas columnas de botones de forma proporcional
        self.frame_acciones.columnconfigure(0, weight=1)
        self.frame_acciones.columnconfigure(1, weight=1)

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
        if producto.requiere_configuracion_carne:
            self._abrir_dialogo_opcion_carne(producto)
        else:
            self._añadir_producto_a_mesa(producto, opcion_carne=None)

    def _abrir_dialogo_opcion_carne(self, producto: Producto) -> None:
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
        mesas = self.controlador.obtener_todas_las_mesas()
        if self.id_mesa in mesas:
            mesa = mesas[self.id_mesa]
            mesa.agregar_producto(producto, cantidad=1, opcion_carne=opcion_carne, observacion=observacion)
            self.controlador.servicio_json.guardar_estado(mesas)
            self._actualizar_vista_ticket()

    def _actualizar_vista_ticket(self) -> None:
        for widget in self.frame_items_pedido.winfo_children():
            widget.destroy()

        mesas = self.controlador.obtener_todas_las_mesas()
        if self.id_mesa not in mesas:
            return
            
        mesa_actual = mesas[self.id_mesa]

        for idx, item in enumerate(mesa_actual.items):
            frame_item = ctk.CTkFrame(self.frame_items_pedido)
            frame_item.pack(fill="x", pady=4, padx=2)

            texto_base = f"{item.cantidad}x {item.producto.nombre}"
            if item.opcion_carne:
                texto_base += f" ({item.opcion_carne})"
            texto_base += f" - {formatear_cop(item.calcular_subtotal())}"

            lbl_info = ctk.CTkLabel(frame_item, text=texto_base, font=("Arial", 12, "bold"), anchor="w")
            lbl_info.pack(fill="x", padx=10, pady=(4, 0))

            if item.observaciones:
                obs_text = "   Notas: " + ", ".join(item.observaciones)
                lbl_obs = ctk.CTkLabel(frame_item, text=obs_text, font=("Arial", 10, "italic"), text_color="#f39c12", anchor="w")
                lbl_obs.pack(fill="x", padx=10, pady=(0, 2))

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
        dialogo = ctk.CTkInputDialog(text=f"Agregar observación para {item_ref.producto.nombre}:", title="Nota de Cocina")
        nota = dialogo.get_input()
        if nota and nota.strip():
            item_ref.observaciones.append(nota.strip())
            mesas = self.controlador.obtener_todas_las_mesas()
            self.controlador.servicio_json.guardar_estado(mesas)
            self._actualizar_vista_ticket()

    def _cambiar_cantidad_especifica(self, producto_id: int, nueva_cantidad: int, opcion_carne: str | None) -> None:
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
        productos = self.controlador.restaurante.menu
        icopor = next((p for p in productos if p.categoria == "Icopor"), None)
        if icopor:
            self._añadir_producto_a_mesa(icopor)
        else:
            messagebox.showwarning("Atención", "No se encontró ningún producto registrado en la categoría 'Icopor'.")

    # --- NUEVOS MÉTODOS DE LA BOTONERA DE 4 ACCIONES ---

    def _enviar_a_cocina_y_parrilla(self) -> None:
        """Acción 1: Envia comanda a Cocina y/o Parrilla sin cerrar la mesa."""
        mesas = self.controlador.obtener_todas_las_mesas()
        mesa_actual = mesas.get(self.id_mesa)

        if not mesa_actual or not mesa_actual.items:
            messagebox.showwarning("Atención", "No hay consumos para enviar a producción.")
            return

        comanda_cocina = PrintService.generar_comanda_area(mesa_actual, area_destino="Cocina")
        comanda_carnes = PrintService.generar_comanda_area(mesa_actual, area_destino="Carnes")

        if not comanda_cocina and not comanda_carnes:
            messagebox.showinfo("Información", "Los productos de esta mesa pertenecen a Caja.")
            return

        if comanda_cocina:
            messagebox.showinfo(f"🖨️ Comanda Impresa - COCINA (Mesa {self.id_mesa})", comanda_cocina)

        if comanda_carnes:
            messagebox.showinfo(f"🖨️ Comanda Impresa - ZONA CARNES (Mesa {self.id_mesa})", comanda_carnes)

    def _imprimir_precuenta_caja(self) -> None:
        """Acción 2: Imprime pre-cuenta para el cliente sin vaciar la mesa."""
        mesas = self.controlador.obtener_todas_las_mesas()
        mesa_actual = mesas.get(self.id_mesa)

        if not mesa_actual or not mesa_actual.items:
            messagebox.showwarning("Atención", "No hay consumos para imprimir pre-cuenta.")
            return

        ticket_caja = PrintService.generar_ticket_caja(mesa_actual)
        messagebox.showinfo(f"🖨️ Pre-cuenta (CAJA) - Mesa {self.id_mesa}", ticket_caja)

    def _guardar_pedido_y_cerrar(self) -> None:
        """Acción 3: Garantiza el guardado en JSON y cierra la ventana manteniendo la mesa ocupada."""
        mesas = self.controlador.obtener_todas_las_mesas()
        self.controlador.servicio_json.guardar_estado(mesas)
        self.destroy()

    def _procesar_facturacion(self) -> None:
        """Acción 4: Factura final, imprime, vacía la mesa y la libera."""
        mesas = self.controlador.obtener_todas_las_mesas()
        mesa_actual = mesas.get(self.id_mesa)

        if not mesa_actual or not mesa_actual.items:
            messagebox.showwarning("Operación Inválida", "No se puede facturar una mesa que no registra consumos.")
            return

        ticket_caja = PrintService.generar_ticket_caja(mesa_actual)
        messagebox.showinfo(f"FACTURA EMITIDA - MESA {self.id_mesa}", ticket_caja)

        self.controlador.liberar_mesa(self.id_mesa)
        self.destroy()