import customtkinter as ctk

from .emotions_view import EmotionsWindow
from .gestures_view import GesturesWindow


class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de apariencia
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Config de la ventana
        self.title("Emotion & Gesture App - Menú principal")
        self.geometry("500x300")

        # Widgets
        title = ctk.CTkLabel(self, text="Menú principal", font=("Arial", 24))
        title.pack(pady=20)

        btn_emociones = ctk.CTkButton(
            self,
            text="Detector de emociones",
            command=self.open_emotions_window,
        )
        btn_emociones.pack(pady=10)

        btn_gestos = ctk.CTkButton(
            self,
            text="Detector de gestos",
            command=self.open_gestures_window,
        )
        btn_gestos.pack(pady=10)

        btn_salir = ctk.CTkButton(self, text="Salir", command=self.destroy)
        btn_salir.pack(pady=20)

    def open_emotions_window(self):
        """Abre la ventana del detector de emociones."""
        EmotionsWindow(master=self)

    def open_gestures_window(self):
        """Abre la ventana del detector de gestos."""
        GesturesWindow(master=self)


def run_app():
    app = MainMenu()
    app.mainloop()
