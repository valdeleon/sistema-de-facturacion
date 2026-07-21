from models.pedido import Restaurante
from services.json_service import JsonService
from services.menu_service import MenuService
from controllers.main_controller import MainController
from views.main_window import MainWindow
import customtkinter as ctk

def iniciar_sistema():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # 1. Instanciar Servicios
    servicio_menu = MenuService(ruta_archivo="menu_data.json")
    servicio_almacenamiento = JsonService(ruta_archivo="mesas_data.json")

    # 2. Instanciar Modelo con el menú cargado desde el servicio
    menu_inicial = servicio_menu.cargar_menu()
    restaurante_modelo = Restaurante(menu_inicial=menu_inicial)

    # 3. Instanciar Controlador con sus tres dependencias
    controlador_principal = MainController(
        restaurante=restaurante_modelo, 
        servicio_json=servicio_almacenamiento,
        servicio_menu=servicio_menu
    )

    # 4. Iniciar Interfaz
    app = MainWindow(controlador=controlador_principal)
    app.mainloop()

if __name__ == "__main__":
    iniciar_sistema()