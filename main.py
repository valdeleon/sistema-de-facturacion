from models.pedido import Restaurante
from services.json_service import JsonService
from controllers.main_controller import MainController
from views.main_window import MainWindow
import customtkinter as ctk

def iniciar_sistema():
    """Inicializa y acopla todas las capas de la arquitectura MVC para arrancar la app."""
    
    # 1. Configuración del entorno visual global de CustomTkinter
    ctk.set_appearance_mode("System")  # Adopta el modo claro/oscuro de Windows
    ctk.set_default_color_theme("blue") # Tema de color general de los componentes

    # 2. Inicialización de los componentes de negocio y persistencia
    restaurante_modelo = Restaurante()
    servicio_almacenamiento = JsonService(ruta_archivo="mesas_data.json")

    # 3. Creación del Controlador (Inyectamos el modelo y el servicio como dependencias)
    controlador_principal = MainController(
        restaurante=restaurante_modelo, 
        servicio_json=servicio_almacenamiento
    )

    # 4. Inicialización de la Vista Principal (Le inyectamos su respectivo controlador)
    app = MainWindow(controlador=controlador_principal)
    
    # 5. Encendido del bucle de eventos (Mantiene la aplicación viva en pantalla)
    app.mainloop()

if __name__ == "__main__":
    iniciar_sistema()