import customtkinter as ctk
from controllers.main_controller import MainController

class MainWindow(ctk.CTk):
    """Ventana principal del sistema de facturación. Se encarga del renderizado de las mesas."""

    def __init__(self, controlador: MainController):
        super().__init__()
        self.controlador: MainController = controlador

        # Configuración de la ventana contenedora principal
        self.title("Sistema de Facturación - El Rancho de Javi")
        self.geometry("900x650")
        
        # Estilos visuales corporativos (Buenas prácticas: paleta de colores fija)
        self.COLOR_LIBRE = "#2ecc71"   # Verde esmeralda moderno
        self.COLOR_OCUPADA = "#e74c3c" # Rojo coral moderno

        # Contenedores principales (Layout Desacoplado)
        self._crear_componentes_globales()
        self._renderizar_mesas()

    def _crear_componentes_globales(self) -> None:
        """Crea las barras de título y los botones de administración global."""
        # Frame superior para el encabezado
        self.frame_header = ctk.CTkFrame(self, height=80, corner_radius=0)
        self.frame_header.pack(fill="x", side="top", padx=0, pady=0)

        self.label_titulo = ctk.CTkLabel(
            self.frame_header, 
            text="EL RANCHO DE JAVI - CONTROL DE MESAS", 
            font=("Arial", 22, "bold")
        )
        self.label_titulo.pack(side="left", padx=20, pady=20)

        # Botón dinámico para expandir el restaurante (Tu requerimiento de escalabilidad)
        self.btn_agregar_mesa = ctk.CTkButton(
            self.frame_header, 
            text="+ Agregar Mesa", 
            font=("Arial", 14, "bold"),
            command=self._accion_agregar_mesa
        )
        self.btn_agregar_mesa.pack(side="right", padx=20, pady=20)

        # Contenedor central donde vivirán las mesas en cuadrícula (Grid)
        self.frame_grid_mesas = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.frame_grid_mesas.pack(fill="both", expand=True, padx=20, pady=20)

    def _renderizar_mesas(self) -> None:
        """Limpia el contenedor visual y dibuja los botones de las mesas según su estado actual."""
        # Limpieza de elementos viejos para evitar duplicación visual en RAM al refrescar
        for widget in self.frame_grid_mesas.winfo_children():
            widget.destroy()

        mesas = self.controlador.obtener_todas_las_mesas()
        
        columnas_maximas = 4
        fila_actual = 0
        columna_actual = 0

        for id_mesa, mesa in mesas.items():
            # Decisión de diseño: El color responde directamente al estado del objeto del Modelo
            color_boton = self.COLOR_LIBRE if mesa.estado == "Libre" else self.COLOR_OCUPADA
            texto_boton = f"Mesa {id_mesa}\n({mesa.estado})"

            # Instanciamos el botón de la mesa
            btn_mesa = ctk.CTkButton(
                self.frame_grid_mesas,
                text=texto_boton,
                font=("Arial", 16, "bold"),
                fg_color=color_boton,
                hover_color=color_boton, # Mantiene la consistencia del color al pasar el mouse
                width=160,
                height=120,
                corner_radius=12,
                # Buena práctica: Uso de lambda para capturar el ID exacto de la mesa en el clic
                command=lambda m=id_mesa: self._mesa_seleccionada(m)
            )
            
            # Posicionamos el botón en la cuadrícula
            btn_mesa.grid(row=fila_actual, column=columna_actual, padx=20, pady=20)

            columna_actual += 1
            if columna_actual >= columnas_maximas:
                columna_actual = 0
                fila_actual += 1

    def _mesa_seleccionada(self, id_mesa: str | int) -> None:
        """Punto de captura del evento clic. Instancia la ventana de pedidos acoplada."""
        from views.order_window import OrderWindow
        # Instanciamos la modal pasándole 'self' (MainWindow) como el padre visual
        OrderWindow(parent=self, controlador=self.controlador, id_mesa=id_mesa)
        
        # Hito de sincronización reactiva: Cuando se cierre la ventana de pedidos,
        # obligamos a la pantalla principal a refrescarse para actualizar los colores (Verde -> Rojo)
        self.master.after(200, self._renderizar_mesas)

    def _accion_agregar_mesa(self) -> None:
        """Pregunta el número de la nueva mesa y le ordena al controlador registrarla."""
        # Creamos una ventana de diálogo nativa de CustomTkinter para pedir el nombre/número
        dialogo = ctk.CTkInputDialog(text="Ingrese el número o nombre de la nueva mesa:", title="Nueva Mesa")
        entrada = dialogo.get_input()

        if entrada:
            # Si el usuario ingresa un número, intentamos guardarlo como entero para mantener el orden limpio
            id_nueva = int(entrada) if entrada.isdigit() else entrada
            
            exito = self.controlador.crear_nueva_mesa_dinamica(id_nueva)
            if exito:
                # Si el controlador la guardó bien en RAM y JSON, redibujamos la pantalla
                self._renderizar_mesas()
            else:
                print("DEBUG: La mesa ya existe en el sistema.")