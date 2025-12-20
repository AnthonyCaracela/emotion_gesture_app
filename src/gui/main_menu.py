"""
Menú Principal - Emotion & Gesture App
Diseño profesional con estética moderna y elegante
"""

import customtkinter as ctk
from PIL import Image, ImageDraw
import os

from .emotions_view import EmotionsWindow
from .gestures_view import GesturesWindow


class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de apariencia
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Config de la ventana - MÁS GRANDE
        self.title("Emotion & Gesture App - Menú principal")
        self._center_window(750, 600)
        self.resizable(False, False)

        # Colores personalizados
        self.colors = {
            "bg_dark": "#0a0a0f",
            "bg_card": "#12121a",
            "accent_primary": "#6366f1",
            "accent_secondary": "#8b5cf6",
            "accent_cyan": "#22d3ee",
            "accent_pink": "#ec4899",
            "text_primary": "#f8fafc",
            "text_secondary": "#94a3b8",
            "border": "#1e1e2e",
        }

        # Configurar fondo
        self.configure(fg_color=self.colors["bg_dark"])

        # Crear interfaz
        self._create_ui()

    def _center_window(self, width: int, height: int):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 3
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_ui(self):
        """Crea la interfaz de usuario"""
        
        # ═══════════════════════════════════════════
        # HEADER SECTION - Más espacio
        # ═══════════════════════════════════════════
        header_frame = ctk.CTkFrame(
            self, 
            fg_color="transparent",
        )
        header_frame.pack(fill="x", padx=50, pady=(50, 30))

        # Icono decorativo
        icon_label = ctk.CTkLabel(
            header_frame,
            text="🎭",
            font=("Segoe UI Emoji", 56),
        )
        icon_label.pack(pady=(0, 10))

        # Título principal
        title_label = ctk.CTkLabel(
            header_frame,
            text="Emotion & Gesture",
            font=("Segoe UI", 38, "bold"),
            text_color=self.colors["text_primary"],
        )
        title_label.pack(pady=(0, 8))

        # Subtítulo - CON MÁS ESPACIO
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Sistema de reconocimiento facial y gestual en tiempo real",
            font=("Segoe UI", 14),
            text_color=self.colors["text_secondary"],
        )
        subtitle_label.pack(pady=(0, 10))

        # ═══════════════════════════════════════════
        # CARDS SECTION
        # ═══════════════════════════════════════════
        cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        cards_frame.pack(fill="both", expand=True, padx=50, pady=20)

        # Grid para las cards
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.rowconfigure(0, weight=1)

        # Card 1: Detector de Emociones
        self._create_feature_card(
            parent=cards_frame,
            icon="😊",
            title="Emociones",
            description="Detecta expresiones faciales en tiempo real usando inteligencia artificial",
            color=self.colors["accent_cyan"],
            command=self.open_emotions_window,
            row=0,
            column=0,
        )

        # Card 2: Detector de Gestos
        self._create_feature_card(
            parent=cards_frame,
            icon="✋",
            title="Gestos",
            description="Reconoce gestos manuales y controla tu computadora",
            color=self.colors["accent_pink"],
            command=self.open_gestures_window,
            row=0,
            column=1,
        )

        # ═══════════════════════════════════════════
        # FOOTER SECTION
        # ═══════════════════════════════════════════
        footer_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        footer_frame.pack(fill="x", padx=50, pady=(10, 40))

        # Créditos
        credits_label = ctk.CTkLabel(
            footer_frame,
            text="Arquitectura de Computadoras • UNSA 2025",
            font=("Segoe UI", 12),
            text_color="#4a4a5a",
        )
        credits_label.pack(pady=(0, 15))

        # Botón salir elegante
        btn_salir = ctk.CTkButton(
            footer_frame,
            text="✕  Cerrar aplicación",
            command=self.destroy,
            width=220,
            height=45,
            font=("Segoe UI", 14),
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["border"],
            hover_color="#1a1a2e",
            text_color=self.colors["text_secondary"],
        )
        btn_salir.pack()

    def _create_feature_card(self, parent, icon, title, description, color, command, row, column):
        """Crea una card de feature con hover effect"""
        
        # Frame principal de la card
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["bg_card"],
            corner_radius=20,
            border_width=1,
            border_color=self.colors["border"],
        )
        card.grid(row=row, column=column, padx=12, pady=12, sticky="nsew")

        # Contenido interno con más padding
        inner_frame = ctk.CTkFrame(card, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Icono con fondo de color
        icon_bg = ctk.CTkFrame(
            inner_frame,
            width=70,
            height=70,
            corner_radius=18,
            fg_color=color,
        )
        icon_bg.pack(anchor="w")
        icon_bg.pack_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_bg,
            text=icon,
            font=("Segoe UI Emoji", 32),
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Título de la card
        title_label = ctk.CTkLabel(
            inner_frame,
            text=title,
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["text_primary"],
            anchor="w",
        )
        title_label.pack(fill="x", pady=(20, 8))

        # Descripción con más espacio
        desc_label = ctk.CTkLabel(
            inner_frame,
            text=description,
            font=("Segoe UI", 13),
            text_color=self.colors["text_secondary"],
            anchor="w",
            wraplength=250,
            justify="left",
        )
        desc_label.pack(fill="x", pady=(0, 20))

        # Botón de acción más grande
        btn = ctk.CTkButton(
            inner_frame,
            text="Iniciar →",
            command=command,
            width=140,
            height=45,
            font=("Segoe UI", 14, "bold"),
            fg_color=color,
            hover_color=self._darken_color(color),
            corner_radius=12,
            anchor="center",
        )
        btn.pack(anchor="w")

        # Efectos hover en la card
        self._add_hover_effect(card, color)

    def _add_hover_effect(self, card, accent_color):
        """Añade efecto hover a la card"""
        original_border = self.colors["border"]
        
        def on_enter(e):
            card.configure(border_color=accent_color)
        
        def on_leave(e):
            card.configure(border_color=original_border)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Bind a todos los hijos también
        for child in card.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
            for subchild in child.winfo_children():
                subchild.bind("<Enter>", on_enter)
                subchild.bind("<Leave>", on_leave)
                for subsubchild in subchild.winfo_children():
                    subsubchild.bind("<Enter>", on_enter)
                    subsubchild.bind("<Leave>", on_leave)

    def _darken_color(self, hex_color, factor=0.8):
        """Oscurece un color hex"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def open_emotions_window(self):
        """Abre la ventana del detector de emociones."""
        EmotionsWindow(master=self)

    def open_gestures_window(self):
        """Abre la ventana del detector de gestos."""
        GesturesWindow(master=self)


def run_app():
    app = MainMenu()
    app.mainloop()