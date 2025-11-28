import customtkinter as ctk

def main():
    # Configuración de apariencia
    ctk.set_appearance_mode("dark")          # "dark" o "light"
    ctk.set_default_color_theme("blue")      # tema por defecto

    app = ctk.CTk()
    app.title("Emotion & Gesture App - Menú principal")
    app.geometry("500x300")

    # Título
    title = ctk.CTkLabel(app, text="Menú principal", font=("Arial", 24))
    title.pack(pady=20)

    # Botón: Detector de emociones (todavía sin lógica)
    btn_emociones = ctk.CTkButton(app, text="Detector de emociones")
    btn_emociones.pack(pady=10)

    # Botón: Detector de gestos (todavía sin lógica)
    btn_gestos = ctk.CTkButton(app, text="Detector de gestos")
    btn_gestos.pack(pady=10)

    # Botón: Salir
    btn_salir = ctk.CTkButton(app, text="Salir", command=app.destroy)
    btn_salir.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    main()
