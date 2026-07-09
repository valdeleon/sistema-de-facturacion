import customtkinter as ctk

def iniciar_aplicacion():
    # Configuración del tema visual y esquema de color predeterminado
    ctk.set_appearance_mode("System")  # Detecta si el sistema operativo usa modo claro u oscuro
    ctk.set_default_color_theme("blue")  # Tema de color base para los componentes

    # Inicialización de la ventana principal de CustomTkinter
    ventana = ctk.CTk()
    ventana.title("Sistema de Facturación - El Rancho de Javi")
    ventana.geometry("400x300")
    ventana.resizable(False, False)

    # Centrar la ventana en pantalla
    ventana.update_idletasks()
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    ancho_ventana = 400
    alto_ventana = 300
    x = (ancho_pantalla // 2) - (ancho_ventana // 2)
    y = (alto_pantalla // 2) - (alto_ventana // 2)
    ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    # Un componente de texto simple para validar el renderizado
    etiqueta = ctk.CTkLabel(master=ventana, text="¡CustomTkinter configurado con éxito!", font=("Arial", 16))
    etiqueta.pack(pady=50, padx=20)

    print("Aplicación iniciada. Se abrió la ventana de interfaz.")

    # El bucle principal mantiene la ventana abierta y escuchando eventos (clics, teclado)
    ventana.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()