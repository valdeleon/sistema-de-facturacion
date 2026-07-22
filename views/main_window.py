import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
from controllers.main_controller import MainController

class MainWindow(ctk.CTk):
    """Ventana principal del sistema de facturación con renderizado de mesas tradicionales y VIP."""

    def __init__(self, controlador: MainController):
        super().__init__()
        self.controlador: MainController = controlador

        self.title("Sistema POS - El Rancho de Javi")
        self.geometry("1000x700")
        
        # Paleta de colores corporativos
        self.COLOR_LIBRE = "#2ecc71"      # Verde esmeralda
        self.COLOR_OCUPADA = "#e74c3c"    # Rojo coral
        self.COLOR_VIP_LIBRE = "#f1c40f"  # Dorado / Amarillo VIP Libre
        self.COLOR_VIP_OCUPADA = "#d35400"# Naranja oscuro VIP Ocupada

        # Diccionario para guardar referencias a los botones y poder actualizar su texto en vivo
        self.botones_mesas: dict[str | int, ctk.CTkButton] = {}

        self._crear_componentes_globales()
        self._renderizar_mesas()
        
        # Iniciar el bucle de actualización del cronómetro cada segundo
        self._actualizar_cronometros()

    def _crear_componentes_globales(self) -> None:
        self.frame_header = ctk.CTkFrame(self, height=80, corner_radius=0)
        self.frame_header.pack(fill="x", side="top", padx=0, pady=0)

        self.label_titulo = ctk.CTkLabel(
            self.frame_header, 
            text="EL RANCHO DE JAVI - CONTROL DE MESAS", 
            font=("Arial", 20, "bold")
        )
        self.label_titulo.pack(side="left", padx=20, pady=20)

        # Botón de Administración de Menú
        self.btn_admin_menu = ctk.CTkButton(
            self.frame_header, text="⚙️ Menú", font=("Arial", 12, "bold"),
            fg_color="#8e44ad", hover_color="#732d91", width=90,
            command=self._abrir_admin_menu
        )
        self.btn_admin_menu.pack(side="right", padx=10, pady=20)

        # Botón Agregar Mesa VIP
        self.btn_agregar_vip = ctk.CTkButton(
            self.frame_header, text="⭐ + Mesa VIP", font=("Arial", 12, "bold"),
            fg_color="#f39c12", hover_color="#d68910", width=110,
            command=lambda: self._accion_agregar_mesa(es_vip=True)
        )
        self.btn_agregar_vip.pack(side="right", padx=5, pady=20)

        # Botón Agregar Mesa Normal
        self.btn_agregar_mesa = ctk.CTkButton(
            self.frame_header, text="+ Agregar Mesa", font=("Arial", 12, "bold"),
            width=110, command=lambda: self._accion_agregar_mesa(es_vip=False)
        )
        self.btn_agregar_mesa.pack(side="right", padx=5, pady=20)

        # Contenedor central con scrollbar
        self.frame_grid_mesas = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.frame_grid_mesas.pack(fill="both", expand=True, padx=20, pady=20)

    def _renderizar_mesas(self) -> None:
        for widget in self.frame_grid_mesas.winfo_children():
            widget.destroy()

        self.botones_mesas.clear()
        mesas = self.controlador.obtener_todas_las_mesas()
        
        columnas_maximas = 4
        fila_actual = 0
        columna_actual = 0

        for id_mesa, mesa in mesas.items():
            if mesa.es_vip:
                color_boton = self.COLOR_VIP_LIBRE if mesa.estado == "Libre" else self.COLOR_VIP_OCUPADA
                prefijo = "⭐ MESA VIP"
                texto_color = "black" if mesa.estado == "Libre" else "white"
            else:
                color_boton = self.COLOR_LIBRE if mesa.estado == "Libre" else self.COLOR_OCUPADA
                prefijo = "MESA"
                texto_color = "white"

            texto_boton = f"{prefijo} {id_mesa}\n({mesa.estado})"
            
            # Si está ocupada y tiene hora de apertura, calculamos el tiempo
            if mesa.estado == "Ocupada" and mesa.hora_apertura:
                tiempo_txt = self._calcular_tiempo_transcurrido(mesa.hora_apertura)
                texto_boton += f"\n⏱️ {tiempo_txt}"

            if not mesa.es_fija:
                texto_boton += "\n[Temporal]"

            frame_mesa = ctk.CTkFrame(self.frame_grid_mesas, fg_color="transparent")
            frame_mesa.grid(row=fila_actual, column=columna_actual, padx=15, pady=15)

            btn_mesa = ctk.CTkButton(
                frame_mesa,
                text=texto_boton,
                font=("Arial", 13, "bold"),
                fg_color=color_boton,
                hover_color=color_boton,
                text_color=texto_color,
                width=160,
                height=110,
                corner_radius=12,
                border_width=2 if mesa.es_vip else 0,
                border_color="#d35400" if mesa.es_vip else None,
                command=lambda m=id_mesa: self._mesa_seleccionada(m)
            )
            btn_mesa.pack()
            
            # Guardamos la referencia para el reloj
            self.botones_mesas[id_mesa] = btn_mesa

            if not mesa.es_fija:
                btn_del = ctk.CTkButton(
                    frame_mesa, text="Eliminar Mesa", font=("Arial", 10),
                    fg_color="#c0392b", hover_color="#962d22", width=160, height=20,
                    command=lambda m=id_mesa: self._accion_eliminar_mesa(m)
                )
                btn_del.pack(pady=(4, 0))

            columna_actual += 1
            if columna_actual >= columnas_maximas:
                columna_actual = 0
                fila_actual += 1

    def _calcular_tiempo_transcurrido(self, hora_iso: str) -> str:
        """Calcula los HH:MM:SS transcurridos desde la hora de apertura."""
        try:
            hora_inicio = datetime.fromisoformat(hora_iso)
            diferencia = datetime.now() - hora_inicio
            segundos_totales = int(diferencia.total_seconds())
            
            horas = segundos_totales // 3600
            minutos = (segundos_totales % 3600) // 60
            segundos = segundos_totales % 60
            
            return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        except Exception:
            return "00:00:00"

    def _actualizar_cronometros(self) -> None:
        """Bucle liviano que refresca el texto del tiempo en los botones ocupados cada segundo."""
        mesas = self.controlador.obtener_todas_las_mesas()
        
        for id_mesa, mesa in mesas.items():
            if mesa.estado == "Ocupada" and mesa.hora_apertura and id_mesa in self.botones_mesas:
                tiempo_txt = self._calcular_tiempo_transcurrido(mesa.hora_apertura)
                prefijo = "⭐ MESA VIP" if mesa.es_vip else "MESA"
                nuevo_texto = f"{prefijo} {id_mesa}\n({mesa.estado})\n⏱️ {tiempo_txt}"
                if not mesa.es_fija:
                    nuevo_texto += "\n[Temporal]"
                
                # Actualizamos solo el texto del botón sin destruir widgets
                self.botones_mesas[id_mesa].configure(text=nuevo_texto)

        # Reprogramar la ejecución para dentro de 1000 milisegundos (1 segundo)
        self.after(1000, self._actualizar_cronometros)

    def _mesa_seleccionada(self, id_mesa: str | int) -> None:
        from views.order_window import OrderWindow
        ventana_pedidos = OrderWindow(parent=self, controlador=self.controlador, id_mesa=id_mesa)
        self.wait_window(ventana_pedidos)
        self._renderizar_mesas()

    def _accion_agregar_mesa(self, es_vip: bool = False) -> None:
        tipo_txt = "VIP" if es_vip else "Normal"
        dialogo = ctk.CTkInputDialog(text=f"Ingrese el número/nombre para la nueva Mesa {tipo_txt}:", title=f"Nueva Mesa {tipo_txt}")
        entrada = dialogo.get_input()

        if entrada:
            id_nueva = int(entrada) if entrada.isdigit() else entrada
            exito = self.controlador.crear_nueva_mesa_dinamica(id_nueva, es_vip=es_vip)
            if exito:
                self._renderizar_mesas()
            else:
                messagebox.showwarning("Atención", f"La mesa '{id_nueva}' ya existe en el sistema.")

    def _accion_eliminar_mesa(self, id_mesa: str | int) -> None:
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar la mesa temporal '{id_mesa}'?"):
            exito, mensaje = self.controlador.eliminar_mesa_dinamica(id_mesa)
            if exito:
                self._renderizar_mesas()
            else:
                messagebox.showwarning("No se puede eliminar", mensaje)

    def _abrir_admin_menu(self) -> None:
        from services.menu_service import MenuService
        from controllers.menu_controller import MenuController
        from views.admin_menu_window import AdminMenuWindow

        servicio_menu = MenuService(ruta_archivo="menu_data.json")
        controlador_menu = MenuController(servicio_menu)

        def al_cerrar():
            self.controlador.actualizar_menu_desde_disco()

        AdminMenuWindow(parent=self, controlador_menu=controlador_menu, al_cerrar_callback=al_cerrar)