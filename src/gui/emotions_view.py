"""
Detector de Emociones - Vista Moderna
Diseño profesional que combina con el menú principal
"""

import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from datetime import datetime

from vision.camera import Camera
from vision.emotion_recognizer import EmotionRecognizer
from reports.emotion_report import generate_emotion_report
from music.player import MusicPlayer


class EmotionsWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)

        # Colores personalizados (mismos que el menú)
        self.colors = {
            "bg_dark": "#0a0a0f",
            "bg_card": "#12121a",
            "bg_card_light": "#1a1a24",
            "accent_cyan": "#22d3ee",
            "accent_green": "#22c55e",
            "accent_red": "#ef4444",
            "accent_yellow": "#eab308",
            "accent_blue": "#3b82f6",
            "accent_purple": "#a855f7",
            "text_primary": "#f8fafc",
            "text_secondary": "#94a3b8",
            "border": "#1e1e2e",
        }

        # Configurar ventana
        self.title("Detector de emociones")
        self.configure(fg_color=self.colors["bg_dark"])
        self._center_window(1000, 820)
        self.resizable(True, True)

        # Ventana modal
        self.grab_set()

        # --- Estado interno ---
        self.camera = Camera(index=0)
        self.emotion_recognizer = EmotionRecognizer()
        self.music_player = MusicPlayer()
        self.running = False

        self.current_emotion: str | None = None
        self.emotion_counts: dict[str, int] = {}
        self.emotion_history: list[dict] = []

        # Crear interfaz
        self._create_ui()

        # Cerrar con la X
        self.protocol("WM_DELETE_WINDOW", self.close_window)

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
            text="😊",
            font=("Segoe UI Emoji", 32),
        )
        icon_label.pack(side="left", padx=(0, 12))

        title_text_frame = ctk.CTkFrame(title_container, fg_color="transparent")
        title_text_frame.pack(side="left")

        title = ctk.CTkLabel(
            title_text_frame,
            text="Detector de Emociones",
            font=("Segoe UI", 28, "bold"),
            text_color=self.colors["text_primary"],
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_text_frame,
            text="Análisis en tiempo real con inteligencia artificial",
            font=("Segoe UI", 13),
            text_color=self.colors["text_secondary"],
        )
        subtitle.pack(anchor="w")

        # ═══════════════════════════════════════════
        # CONTENIDO PRINCIPAL
        # ═══════════════════════════════════════════
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Layout: Video a la izquierda, Stats a la derecha
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

        # --- STATS PANEL ---
        stats_card = ctk.CTkFrame(
            content_frame,
            fg_color=self.colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"],
        )
        stats_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        stats_inner = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_inner.pack(fill="both", expand=True, padx=20, pady=20)

        # Título del panel
        stats_title = ctk.CTkLabel(
            stats_inner,
            text="📊 Estadísticas",
            font=("Segoe UI", 18, "bold"),
            text_color=self.colors["text_primary"],
        )
        stats_title.pack(anchor="w", pady=(0, 15))

        # Emoción actual (destacada)
        emotion_card = ctk.CTkFrame(
            stats_inner,
            fg_color=self.colors["bg_card_light"],
            corner_radius=12,
        )
        emotion_card.pack(fill="x", pady=(0, 15))

        emotion_inner = ctk.CTkFrame(emotion_card, fg_color="transparent")
        emotion_inner.pack(fill="x", padx=15, pady=15)

        emotion_title = ctk.CTkLabel(
            emotion_inner,
            text="Emoción actual",
            font=("Segoe UI", 11),
            text_color=self.colors["text_secondary"],
        )
        emotion_title.pack(anchor="w")

        self.emotion_label = ctk.CTkLabel(
            emotion_inner,
            text="---",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["accent_cyan"],
        )
        self.emotion_label.pack(anchor="w", pady=(5, 0))

        self.confidence_label = ctk.CTkLabel(
            emotion_inner,
            text="Confianza: ---%",
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"],
        )
        self.confidence_label.pack(anchor="w")

        # Separador
        separator = ctk.CTkFrame(
            stats_inner,
            fg_color=self.colors["border"],
            height=1,
        )
        separator.pack(fill="x", pady=10)

        # Contadores de emociones
        counters_title = ctk.CTkLabel(
            stats_inner,
            text="Contadores",
            font=("Segoe UI", 13, "bold"),
            text_color=self.colors["text_primary"],
        )
        counters_title.pack(anchor="w", pady=(5, 10))

        self.counters_frame = ctk.CTkFrame(stats_inner, fg_color="transparent")
        self.counters_frame.pack(fill="x")

        # Labels para cada emoción
        self.emotion_counter_labels = {}
        emotions_config = [
            ("happy", "😊", self.colors["accent_green"]),
            ("sad", "😢", self.colors["accent_blue"]),
            ("angry", "😠", self.colors["accent_red"]),
            ("surprise", "😮", self.colors["accent_yellow"]),
            ("neutral", "😐", self.colors["text_secondary"]),
        ]

        for emotion, emoji, color in emotions_config:
            row = ctk.CTkFrame(self.counters_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)

            label = ctk.CTkLabel(
                row,
                text=f"{emoji} {emotion.capitalize()}",
                font=("Segoe UI", 12),
                text_color=color,
            )
            label.pack(side="left")

            count_label = ctk.CTkLabel(
                row,
                text="0",
                font=("Segoe UI", 12, "bold"),
                text_color=self.colors["text_primary"],
            )
            count_label.pack(side="right")

            self.emotion_counter_labels[emotion] = count_label

        # Separador
        separator2 = ctk.CTkFrame(
            stats_inner,
            fg_color=self.colors["border"],
            height=1,
        )
        separator2.pack(fill="x", pady=15)

        # Música actual
        music_title = ctk.CTkLabel(
            stats_inner,
            text="🎵 Música",
            font=("Segoe UI", 13, "bold"),
            text_color=self.colors["text_primary"],
        )
        music_title.pack(anchor="w", pady=(0, 8))

        self.music_label = ctk.CTkLabel(
            stats_inner,
            text="Esperando...",
            font=("Segoe UI", 11),
            text_color=self.colors["accent_cyan"],
            wraplength=180,
            justify="left",
        )
        self.music_label.pack(anchor="w")

        # ═══════════════════════════════════════════
        # CONTROLES INFERIORES
        # ═══════════════════════════════════════════
        controls_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"],
        )
        controls_frame.pack(fill="x", padx=30, pady=(10, 25))

        controls_inner = ctk.CTkFrame(controls_frame, fg_color="transparent")
        controls_inner.pack(fill="x", padx=25, pady=20)

        # Fila de controles
        controls_row = ctk.CTkFrame(controls_inner, fg_color="transparent")
        controls_row.pack(fill="x")

        # --- Controles de música ---
        music_controls = ctk.CTkFrame(controls_row, fg_color="transparent")
        music_controls.pack(side="left")

        self.btn_play_pause = ctk.CTkButton(
            music_controls,
            text="⏸️ Pausar",
            command=self.toggle_music,
            width=110,
            height=40,
            font=("Segoe UI", 13),
            fg_color=self.colors["bg_card_light"],
            hover_color="#2a2a3a",
            border_width=1,
            border_color=self.colors["border"],
        )
        self.btn_play_pause.pack(side="left", padx=(0, 8))

        btn_stop = ctk.CTkButton(
            music_controls,
            text="⏹️ Detener",
            command=self.stop_music,
            width=110,
            height=40,
            font=("Segoe UI", 13),
            fg_color=self.colors["bg_card_light"],
            hover_color="#2a2a3a",
            border_width=1,
            border_color=self.colors["border"],
        )
        btn_stop.pack(side="left", padx=(0, 15))

        # Volumen
        volume_icon = ctk.CTkLabel(
            music_controls,
            text="🔊",
            font=("Segoe UI Emoji", 16),
        )
        volume_icon.pack(side="left", padx=(10, 5))

        self.volume_slider = ctk.CTkSlider(
            music_controls,
            from_=0,
            to=100,
            width=120,
            height=16,
            command=self.on_volume_change,
            button_color=self.colors["accent_cyan"],
            button_hover_color="#1cb5cc",
            progress_color=self.colors["accent_cyan"],
        )
        self.volume_slider.set(50)
        self.volume_slider.pack(side="left", padx=(0, 10))

        # --- Botones principales ---
        main_buttons = ctk.CTkFrame(controls_row, fg_color="transparent")
        main_buttons.pack(side="right")

        btn_report = ctk.CTkButton(
            main_buttons,
            text="📄 Generar PDF",
            command=self.on_generate_report,
            width=150,
            height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color=self.colors["accent_purple"],
            hover_color="#9333ea",
        )
        btn_report.pack(side="left", padx=(0, 10))

        btn_close = ctk.CTkButton(
            main_buttons,
            text="✕ Cerrar",
            command=self.close_window,
            width=100,
            height=40,
            font=("Segoe UI", 13),
            fg_color=self.colors["accent_red"],
            hover_color="#dc2626",
        )
        btn_close.pack(side="left")

        # Status del reporte
        self.report_status_label = ctk.CTkLabel(
            controls_inner,
            text="",
            font=("Segoe UI", 11),
            text_color=self.colors["accent_green"],
        )
        self.report_status_label.pack(pady=(10, 0))

    def _get_emotion_color(self, emotion: str) -> str:
        """Retorna el color según la emoción"""
        color_map = {
            "happy": self.colors["accent_green"],
            "sad": self.colors["accent_blue"],
            "angry": self.colors["accent_red"],
            "surprise": self.colors["accent_yellow"],
            "neutral": self.colors["text_secondary"],
        }
        return color_map.get(emotion, self.colors["accent_cyan"])

    def _get_emotion_emoji(self, emotion: str) -> str:
        """Retorna el emoji según la emoción"""
        emoji_map = {
            "happy": "😊",
            "sad": "😢",
            "angry": "😠",
            "surprise": "😮",
            "neutral": "😐",
        }
        return emoji_map.get(emotion, "🤔")

    def update_frame(self):
        """Lee un frame, detecta emoción, anota y actualiza la UI."""
        if not self.running:
            return

        ret, frame = self.camera.read()
        if not ret or frame is None:
            self.after(50, self.update_frame)
            return

        frame_annotated, top_emotion, score, emotions = \
            self.emotion_recognizer.analyze(frame)

        if top_emotion is not None:
            self.current_emotion = top_emotion
            self.emotion_counts[top_emotion] = (
                self.emotion_counts.get(top_emotion, 0) + 1
            )

            # Actualizar emoción actual con estilo
            emoji = self._get_emotion_emoji(top_emotion)
            color = self._get_emotion_color(top_emotion)
            self.emotion_label.configure(
                text=f"{emoji} {top_emotion.upper()}",
                text_color=color,
            )
            self.confidence_label.configure(
                text=f"Confianza: {score*100:.1f}%"
            )

            # Actualizar contadores
            for emotion, label in self.emotion_counter_labels.items():
                count = self.emotion_counts.get(emotion, 0)
                label.configure(text=str(count))

            # Actualizar música
            self.music_player.update_emotion(top_emotion)
            current_music_emotion = self.music_player.get_current_emotion()
            if current_music_emotion:
                music_desc = self.music_player.emotion_mapper.get_description(current_music_emotion)
                self.music_label.configure(
                    text=f"{current_music_emotion.upper()}\n{music_desc}"
                )

            # Historial
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.emotion_history.append({
                "time": timestamp,
                "emotion": top_emotion,
                "score": float(score),
            })

        # Mostrar video
        frame_rgb = cv2.cvtColor(frame_annotated, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        image = image.resize((640, 420), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image=image)

        self.video_label.configure(image=photo, text="")
        self.video_label.image = photo

        self.after(80, self.update_frame)

    def toggle_music(self):
        """Pausa o reanuda la música"""
        if self.music_player.is_playing:
            self.music_player.pause()
            self.btn_play_pause.configure(text="▶️ Reanudar")
        else:
            self.music_player.resume()
            self.btn_play_pause.configure(text="⏸️ Pausar")

    def stop_music(self):
        """Detiene completamente la música"""
        self.music_player.stop()
        self.btn_play_pause.configure(text="▶️ Reanudar")
        self.music_label.configure(text="Detenida")

    def on_volume_change(self, value):
        """Ajusta el volumen de la música"""
        volume = float(value) / 100.0
        self.music_player.set_volume(volume)

    def on_generate_report(self):
        """Genera el reporte PDF."""
        try:
            pdf_path = generate_emotion_report(
                self.emotion_counts,
                self.emotion_history,
            )
            self.report_status_label.configure(
                text=f"✅ Reporte generado: {pdf_path}",
                text_color=self.colors["accent_green"],
            )
        except ValueError as e:
            self.report_status_label.configure(
                text=str(e),
                text_color=self.colors["accent_red"],
            )
        except Exception as e:
            self.report_status_label.configure(
                text=f"❌ Error: {e}",
                text_color=self.colors["accent_red"],
            )

    def close_window(self):
        """Detiene el loop, libera la cámara y cierra la ventana."""
        self.running = False
        self.music_player.stop()
        self.camera.release()
        self.destroy()