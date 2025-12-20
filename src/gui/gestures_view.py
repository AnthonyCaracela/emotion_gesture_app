"""
Detector de Gestos - Vista Moderna
Diseño profesional que combina con el menú principal
"""

import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

from vision.camera import Camera
from vision.hand_tracker import HandTracker
from vision.gesture_recognizer import GestureRecognizer
from control.keyboard_controller import KeyboardController


class GesturesWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)

        # Colores personalizados (mismos que el menú)
        self.colors = {
            "bg_dark": "#0a0a0f",
            "bg_card": "#12121a",
            "bg_card_light": "#1a1a24",
            "accent_cyan": "#22d3ee",
            "accent_pink": "#ec4899",
            "accent_green": "#22c55e",
            "accent_red": "#ef4444",
            "accent_yellow": "#eab308",
            "accent_purple": "#a855f7",
            "accent_orange": "#f97316",
            "text_primary": "#f8fafc",
            "text_secondary": "#94a3b8",
            "border": "#1e1e2e",
        }

        # Configurar ventana
        self.title("Detector de gestos")
        self.configure(fg_color=self.colors["bg_dark"])
        self._center_window(1050, 750)
        self.resizable(True, True)

        # Ventana modal
        self.grab_set()

        # --- Estado interno ---
        self.camera = Camera(index=0)
        self.hand_tracker = HandTracker(max_num_hands=1)
        self.gesture_recognizer = GestureRecognizer()
        self.keyboard_controller = KeyboardController()
        self.running = False

        self.last_sent_gesture: str | None = None
        self.control_enabled = ctk.BooleanVar(value=False)

        # Crear interfaz
        self._create_ui()

        # Cerrar con la X
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Inicializar mapeo
        self.apply_mapping()

        # Iniciar cámara
        if self.camera.open():
            self.running = True
            self.update_frame()
        else:
            self.video_label.configure(text="❌ No se pudo abrir la cámara")

    def _center_window(self, width: int, height: int):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 4
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_ui(self):
        """Crea la interfaz de usuario moderna"""

        # ═══════════════════════════════════════════
        # HEADER
        # ═══════════════════════════════════════════
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(25, 15))

        # Título con icono
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack()

        icon_label = ctk.CTkLabel(
            title_container,
            text="✋",
            font=("Segoe UI Emoji", 32),
        )
        icon_label.pack(side="left", padx=(0, 12))

        title_text_frame = ctk.CTkFrame(title_container, fg_color="transparent")
        title_text_frame.pack(side="left")

        title = ctk.CTkLabel(
            title_text_frame,
            text="Detector de Gestos",
            font=("Segoe UI", 28, "bold"),
            text_color=self.colors["text_primary"],
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_text_frame,
            text="Reconocimiento de gestos y control de teclado",
            font=("Segoe UI", 13),
            text_color=self.colors["text_secondary"],
        )
        subtitle.pack(anchor="w")

        # ═══════════════════════════════════════════
        # CONTENIDO PRINCIPAL
        # ═══════════════════════════════════════════
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Layout: Video a la izquierda, Config a la derecha
        content_frame.columnconfigure(0, weight=3)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # --- VIDEO FRAME ---
        video_card = ctk.CTkFrame(
            content_frame,
            fg_color=self.colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"],
        )
        video_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        self.video_label = ctk.CTkLabel(
            video_card,
            text="🎥 Iniciando cámara...",
            font=("Segoe UI", 16),
            text_color=self.colors["text_secondary"],
        )
        self.video_label.pack(expand=True, padx=15, pady=15)

        # --- PANEL DE CONFIGURACIÓN ---
        config_card = ctk.CTkFrame(
            content_frame,
            fg_color=self.colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"],
        )
        config_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        config_inner = ctk.CTkFrame(config_card, fg_color="transparent")
        config_inner.pack(fill="both", expand=True, padx=20, pady=20)

        # Título del panel
        config_title = ctk.CTkLabel(
            config_inner,
            text="⚙️ Configuración",
            font=("Segoe UI", 18, "bold"),
            text_color=self.colors["text_primary"],
        )
        config_title.pack(anchor="w", pady=(0, 15))

        # Gesto actual (destacado)
        gesture_card = ctk.CTkFrame(
            config_inner,
            fg_color=self.colors["bg_card_light"],
            corner_radius=12,
        )
        gesture_card.pack(fill="x", pady=(0, 15))

        gesture_inner = ctk.CTkFrame(gesture_card, fg_color="transparent")
        gesture_inner.pack(fill="x", padx=15, pady=15)

        gesture_title = ctk.CTkLabel(
            gesture_inner,
            text="Gesto detectado",
            font=("Segoe UI", 11),
            text_color=self.colors["text_secondary"],
        )
        gesture_title.pack(anchor="w")

        self.gesture_label = ctk.CTkLabel(
            gesture_inner,
            text="---",
            font=("Segoe UI", 22, "bold"),
            text_color=self.colors["accent_pink"],
        )
        self.gesture_label.pack(anchor="w", pady=(5, 0))

        self.key_label = ctk.CTkLabel(
            gesture_inner,
            text="Tecla: ---",
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"],
        )
        self.key_label.pack(anchor="w")

        # Separador
        separator = ctk.CTkFrame(
            config_inner,
            fg_color=self.colors["border"],
            height=1,
        )
        separator.pack(fill="x", pady=10)

        # Switch de control
        switch_frame = ctk.CTkFrame(config_inner, fg_color="transparent")
        switch_frame.pack(fill="x", pady=(5, 15))

        self.control_switch = ctk.CTkSwitch(
            switch_frame,
            text="Control de teclado",
            variable=self.control_enabled,
            font=("Segoe UI", 13),
            progress_color=self.colors["accent_green"],
            button_color=self.colors["accent_green"],
            button_hover_color="#1da34d",
        )
        self.control_switch.pack(anchor="w")

        self.status_label = ctk.CTkLabel(
            switch_frame,
            text="⚪ Desactivado",
            font=("Segoe UI", 11),
            text_color=self.colors["text_secondary"],
        )
        self.status_label.pack(anchor="w", pady=(5, 0))

        # Monitorear cambios del switch
        self.control_enabled.trace_add("write", self._on_switch_change)

        # Separador
        separator2 = ctk.CTkFrame(
            config_inner,
            fg_color=self.colors["border"],
            height=1,
        )
        separator2.pack(fill="x", pady=10)

        # Mapeo de teclas
        mapping_title = ctk.CTkLabel(
            config_inner,
            text="🎮 Mapeo de teclas",
            font=("Segoe UI", 13, "bold"),
            text_color=self.colors["text_primary"],
        )
        mapping_title.pack(anchor="w", pady=(5, 10))

        # Container para mapeos
        self.mapping_entries: dict[str, ctk.CTkEntry] = {}

        gestures_config = [
            ("OPEN_HAND", "🖐️ Mano abierta", "d", self.colors["accent_cyan"]),
            ("FIST", "✊ Puño", "a", self.colors["accent_red"]),
            ("PEACE", "✌️ Paz", "w", self.colors["accent_green"]),
            ("INDEX", "☝️ Índice", "s", self.colors["accent_yellow"]),
            ("LIKE", "👍 Like", "l", self.colors["accent_purple"]),
        ]

        for gesture_name, label_text, default_key, color in gestures_config:
            self._create_mapping_row(
                config_inner, gesture_name, label_text, default_key, color
            )

        # Botón aplicar
        btn_apply = ctk.CTkButton(
            config_inner,
            text="✓ Aplicar mapeo",
            command=self.apply_mapping,
            width=160,
            height=38,
            font=("Segoe UI", 13, "bold"),
            fg_color=self.colors["accent_pink"],
            hover_color="#d63d84",
            corner_radius=10,
        )
        btn_apply.pack(anchor="w", pady=(15, 0))

        # ═══════════════════════════════════════════
        # FOOTER
        # ═══════════════════════════════════════════
        footer_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"],
        )
        footer_frame.pack(fill="x", padx=30, pady=(10, 25))

        footer_inner = ctk.CTkFrame(footer_frame, fg_color="transparent")
        footer_inner.pack(fill="x", padx=25, pady=15)

        # Info
        info_label = ctk.CTkLabel(
            footer_inner,
            text="💡 Activa el control de teclado para enviar teclas con gestos",
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"],
        )
        info_label.pack(side="left")

        # Botón cerrar
        btn_close = ctk.CTkButton(
            footer_inner,
            text="✕ Cerrar",
            command=self.close_window,
            width=100,
            height=38,
            font=("Segoe UI", 13),
            fg_color=self.colors["accent_red"],
            hover_color="#dc2626",
        )
        btn_close.pack(side="right")

    def _create_mapping_row(self, parent, gesture_name, label_text, default_key, color):
        """Crea una fila de mapeo gesto->tecla"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)

        label = ctk.CTkLabel(
            row,
            text=label_text,
            font=("Segoe UI", 12),
            text_color=color,
            width=130,
            anchor="w",
        )
        label.pack(side="left")

        arrow = ctk.CTkLabel(
            row,
            text="→",
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"],
        )
        arrow.pack(side="left", padx=5)

        entry = ctk.CTkEntry(
            row,
            width=50,
            height=30,
            font=("Segoe UI", 12),
            fg_color=self.colors["bg_card_light"],
            border_color=self.colors["border"],
            justify="center",
        )
        entry.pack(side="left")
        entry.insert(0, default_key)

        self.mapping_entries[gesture_name] = entry

    def _on_switch_change(self, *args):
        """Actualiza el label de estado cuando cambia el switch"""
        if self.control_enabled.get():
            self.status_label.configure(
                text="🟢 Activado",
                text_color=self.colors["accent_green"],
            )
        else:
            self.status_label.configure(
                text="⚪ Desactivado",
                text_color=self.colors["text_secondary"],
            )

    def _get_gesture_emoji(self, gesture: str) -> str:
        """Retorna el emoji según el gesto"""
        emoji_map = {
            "OPEN_HAND": "🖐️",
            "FIST": "✊",
            "PEACE": "✌️",
            "INDEX": "☝️",
            "LIKE": "👍",
            "UNKNOWN": "❓",
        }
        return emoji_map.get(gesture, "❓")

    def _get_gesture_color(self, gesture: str) -> str:
        """Retorna el color según el gesto"""
        color_map = {
            "OPEN_HAND": self.colors["accent_cyan"],
            "FIST": self.colors["accent_red"],
            "PEACE": self.colors["accent_green"],
            "INDEX": self.colors["accent_yellow"],
            "LIKE": self.colors["accent_purple"],
            "UNKNOWN": self.colors["text_secondary"],
        }
        return color_map.get(gesture, self.colors["accent_pink"])

    def apply_mapping(self):
        """Lee las entradas de texto y actualiza el mapeo gesto->tecla."""
        for gesture, entry in self.mapping_entries.items():
            key = entry.get().strip()
            if key:
                self.keyboard_controller.set_mapping(gesture, key)

    def update_frame(self):
        """Lee un frame, detecta mano, dibuja landmarks y muestra el gesto."""
        if not self.running:
            return

        ret, frame = self.camera.read()
        if not ret or frame is None:
            self.after(50, self.update_frame)
            return

        frame_annotated, landmarks_list = self.hand_tracker.process(frame)

        gesture = "UNKNOWN"
        if landmarks_list:
            hand_landmarks = landmarks_list[0]
            gesture = self.gesture_recognizer.classify(hand_landmarks)

        # Actualizar UI del gesto
        emoji = self._get_gesture_emoji(gesture)
        color = self._get_gesture_color(gesture)
        self.gesture_label.configure(
            text=f"{emoji} {gesture}",
            text_color=color,
        )

        mapped_key = "---"
        if self.control_enabled.get():
            if gesture != "UNKNOWN":
                mapped_key = self.keyboard_controller.get_mapping(gesture)

                if gesture != self.last_sent_gesture and mapped_key:
                    self.keyboard_controller.press_for_gesture(gesture)
                    self.last_sent_gesture = gesture

                if mapped_key:
                    self.key_label.configure(text=f"Tecla: {mapped_key}")
            else:
                self.last_sent_gesture = None
                self.key_label.configure(text="Tecla: ---")
        else:
            self.last_sent_gesture = None
            self.key_label.configure(text="Tecla: ---")

        # Mostrar frame
        frame_rgb = cv2.cvtColor(frame_annotated, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        image = image.resize((640, 420), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image=image)

        self.video_label.configure(image=photo, text="")
        self.video_label.image = photo

        self.after(30, self.update_frame)

    def close_window(self):
        """Detiene el loop, libera cámara y cierra ventana."""
        self.running = False
        self.camera.release()
        self.destroy()