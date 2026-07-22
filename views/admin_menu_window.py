import customtkinter as ctk
from utils.formatters import formatear_cop
from tkinter import messagebox
from controllers.menu_controller import MenuController
from models.pedido import Producto

class AdminMenuWindow(ctk.CTkToplevel):
    """Ventana modal de administración para la gestión del catálogo del menú (CRUD)."""

    def __init__(self, parent, controlador_menu: MenuController, al_cerrar_callback=None):
        super().__init__(parent)
        self.controlador: MenuController = controlador_menu
        self.al_cerrar_callback = al_cerrar_callback
        self.producto_seleccionado: Producto | None = None

        self.title("Administración de Menú - El Rancho de Javi")
        self.geometry("850x600")
        
        self.transient(parent)
        self.grab_set()

        self.CATEGORIAS = ["Bebidas", "Carnes", "Platillos", "Ejecutivo", "Icopor"]
        self.AREAS_IMPRESION = ["Caja", "Cocina", "Carnes"]

        self._crear_interfaz()
        self._cargar_lista_productos()

    def _crear_interfaz(self) -> None:
        """Construye la distribución de dos columnas: Tabla a la izquierda, Formulario a la derecha."""
        self.lbl_titulo = ctk.CTkLabel(self, text="GESTIÓN DEL MENÚ DEL RESTAURANTE", font=("Arial", 18, "bold"))
        self.lbl_titulo.pack(pady=10)

        self.frame_cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cuerpo.pack(fill="both", expand=True, padx=15, pady=10)

        # --- COLUMNA IZQUIERDA: LISTADO DE PRODUCTOS ---
        self.frame_izq = ctk.CTkFrame(self.frame_cuerpo, width=450)
        self.frame_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.lbl_sub_list = ctk.CTkLabel(self.frame_izq, text="Catálogo de Productos", font=("Arial", 14, "bold"))
        self.lbl_sub_list.pack(pady=5)

        self.scroll_productos = ctk.CTkScrollableFrame(self.frame_izq)
        self.scroll_productos.pack(fill="both", expand=True, padx=10, pady=10)

        # --- COLUMNA DERECHA: FORMULARIO DE EDICIÓN / REGISTRO ---
        self.frame_der = ctk.CTkFrame(self.frame_cuerpo, width=350)
        self.frame_der.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.lbl_sub_form = ctk.CTkLabel(self.frame_der, text="Formulario de Producto", font=("Arial", 14, "bold"))
        self.lbl_sub_form.pack(pady=10)

        # Campos del formulario
        self.entry_nombre = ctk.CTkEntry(self.frame_der, placeholder_text="Nombre del Producto")
        self.entry_nombre.pack(fill="x", padx=15, pady=5)

        # Cambiamos el texto de ayuda para orientar al usuario colombiano
        self.entry_precio = ctk.CTkEntry(self.frame_der, placeholder_text="Precio en COP (ej. 3500)")
        self.entry_precio.pack(fill="x", padx=15, pady=5)

        self.lbl_cat = ctk.CTkLabel(self.frame_der, text="Categoría:", font=("Arial", 11))
        self.lbl_cat.pack(anchor="w", padx=15, pady=(5, 0))
        self.combo_categoria = ctk.CTkOptionMenu(self.frame_der, values=self.CATEGORIAS)
        self.combo_categoria.pack(fill="x", padx=15, pady=5)

        self.lbl_area = ctk.CTkLabel(self.frame_der, text="Área de Impresión:", font=("Arial", 11))
        self.lbl_area.pack(anchor="w", padx=15, pady=(5, 0))
        self.combo_area = ctk.CTkOptionMenu(self.frame_der, values=self.AREAS_IMPRESION)
        self.combo_area.pack(fill="x", padx=15, pady=5)

        self.switch_carne = ctk.CTkSwitch(self.frame_der, text="Requiere opción de carne")
        self.switch_carne.pack(anchor="w", padx=15, pady=10)

        # Botones de Acción
        self.btn_guardar = ctk.CTkButton(self.frame_der, text="Guardar Producto", fg_color="#27ae60", command=self._guardar)
        self.btn_guardar.pack(fill="x", padx=15, pady=5)

        self.btn_limpiar = ctk.CTkButton(self.frame_der, text="Limpiar / Nuevo", fg_color="#7f8c8d", command=self._limpiar_formulario)
        self.btn_limpiar.pack(fill="x", padx=15, pady=5)

        self.btn_eliminar = ctk.CTkButton(self.frame_der, text="Eliminar Producto", fg_color="#e74c3c", command=self._eliminar)
        self.btn_eliminar.pack(fill="x", padx=15, pady=(15, 5))

    def _cargar_lista_productos(self) -> None:
        """Renderiza los botones de selección rápida de productos."""
        for widget in self.scroll_productos.winfo_children():
            widget.destroy()

        productos = self.controlador.obtener_todos_los_productos()
        for prod in productos:
            frame_row = ctk.CTkFrame(self.scroll_productos)
            frame_row.pack(fill="x", pady=3, padx=2)

            txt = f"[{prod.categoria}] {prod.nombre} - {formatear_cop(prod.precio)} ({prod.area_impresion})"
            lbl = ctk.CTkLabel(frame_row, text=txt, font=("Arial", 11), anchor="w")
            lbl.pack(side="left", padx=5, fill="x", expand=True)

            btn_sel = ctk.CTkButton(frame_row, text="Editar", width=50, height=22, command=lambda p=prod: self._seleccionar_producto(p))
            btn_sel.pack(side="right", padx=5)

    def _seleccionar_producto(self, producto: Producto) -> None:
        self.producto_seleccionado = producto
        self.entry_nombre.delete(0, "end")
        self.entry_nombre.insert(0, producto.nombre)
        
        self.entry_precio.delete(0, "end")
        # Mostramos el número entero limpio para facilitar su edición
        self.entry_precio.insert(0, str(int(producto.precio)))

        self.combo_categoria.set(producto.categoria)
        self.combo_area.set(producto.area_impresion)
        
        if producto.requiere_configuracion_carne:
            self.switch_carne.select()
        else:
            self.switch_carne.deselect()

    def _limpiar_formulario(self) -> None:
        """Resetea el formulario para agregar un producto desde cero."""
        self.producto_seleccionado = None
        self.entry_nombre.delete(0, "end")
        self.entry_precio.delete(0, "end")
        self.combo_categoria.set(self.CATEGORIAS[0])
        self.combo_area.set(self.AREAS_IMPRESION[0])
        self.switch_carne.deselect()

    def _guardar(self) -> None:
        """Procesa la creación o actualización según si hay un producto seleccionado."""
        nombre = self.entry_nombre.get().strip()
        precio_raw = self.entry_precio.get().strip()
        categoria = self.combo_categoria.get()
        area = self.combo_area.get()
        requiere_carne = bool(self.switch_carne.get())

        if not nombre or not precio_raw:
            messagebox.showwarning("Atención", "Por favor ingrese nombre y precio válidos.")
            return

        try:
            precio = float(precio_raw)
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido.")
            return

        if self.producto_seleccionado:
            # Edición
            self.controlador.actualizar_producto(self.producto_seleccionado.id, nombre, precio, categoria, area, requiere_carne)
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
        else:
            # Creación
            self.controlador.agregar_producto(nombre, precio, categoria, area, requiere_carne)
            messagebox.showinfo("Éxito", "Nuevo producto creado correctamente.")

        self._limpiar_formulario()
        self._cargar_lista_productos()
        if self.al_cerrar_callback:
            self.al_cerrar_callback()

    def _eliminar(self) -> None:
        """Elimina el producto seleccionado."""
        if not self.producto_seleccionado:
            messagebox.showwarning("Atención", "Seleccione un producto del catálogo para eliminar.")
            return

        if messagebox.askyesno("Confirmar", f"¿Desea eliminar '{self.producto_seleccionado.nombre}' del menú?"):
            self.controlador.eliminar_producto(self.producto_seleccionado.id)
            self._limpiar_formulario()
            self._cargar_lista_productos()
            if self.al_cerrar_callback:
                self.al_cerrar_callback()