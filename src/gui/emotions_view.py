import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from datetime import datetime

from vision.camera import Camera
from vision.emotion_recognizer import EmotionRecognizer
from reports.emotion_report import generate_emotion_report


class EmotionsWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Detector de emociones")
        self._center_window(900, 780)
        self.resizable(True, True)  # ✅ se puede mover y redimensionar

        # Ventana modal
        self.grab_set()

        # --- Estado interno ---
        self.camera = Camera(index=0)
        self.emotion_recognizer = EmotionRecognizer()
        self.running = False

        self.current_emotion: str | None = None
        self.emotion_counts: dict[str, int] = {}
        self.emotion_history: list[dict] = []

        # --- Layout principal ---
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            main_frame,
            text="Detector de emociones",
            font=("Arial", 24, "bold"),
        )
        title.pack(pady=(10, 5))

        subtitle = ctk.CTkLabel(
            main_frame,
            text="Analisis en tiempo real de expresiones faciales",
            font=("Arial", 13),
        )
        subtitle.pack(pady=(0, 10))

        # Frame para video
        video_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        video_frame.pack(pady=10)
        self.video_label = ctk.CTkLabel(video_frame, text="Iniciando cámara...")
        self.video_label.pack(padx=10, pady=10)

        # Información de emoción y estadísticas
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=10, padx=10)

        self.emotion_label = ctk.CTkLabel(
            info_frame,
            text="Emocion: ---",
            font=("Arial", 18),
        )
        self.emotion_label.pack(anchor="w")

        self.stats_label = ctk.CTkLabel(
            info_frame,
            text="Estadisticas (frames): ---",
            font=("Arial", 14),
            justify="left",
        )
        self.stats_label.pack(anchor="w", pady=(4, 0))

        # Mensaje de estado del reporte
        self.report_status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=("Arial", 12),
        )
        self.report_status_label.pack(pady=(5, 0))

        # Botones inferiores
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)

        btn_report = ctk.CTkButton(
            buttons_frame,
            text="Generar reporte PDF",
            command=self.on_generate_report,
            width=180,
        )
        btn_report.pack(side="left", padx=10)

        btn_close = ctk.CTkButton(
            buttons_frame,
            text="Cerrar",
            command=self.close_window,
            width=120,
        )
        btn_close.pack(side="left", padx=10)

        # Cerrar con la X
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Iniciar cámara
        if self.camera.open():
            self.running = True
            self.update_frame()
        else:
            self.video_label.configure(text="No se pudo abrir la cámara")

    def _center_window(self, width: int, height: int):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 3
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _format_stats_text(self) -> str:
        """Construye el texto de estadísticas a partir del diccionario."""
        if not self.emotion_counts:
            return "Estadisticas (frames): ---"

        items = sorted(
            self.emotion_counts.items(),
            key=lambda kv: kv[1],
            reverse=True,
        )
        parts = [f"{name}: {count}" for name, count in items]
        return "Estadisticas (frames): " + "   ".join(parts)

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
            emotion_text = f"Emocion: {top_emotion} ({score:.2f})"

            timestamp = datetime.now().strftime("%H:%M:%S")
            self.emotion_history.append(
                {
                    "time": timestamp,
                    "emotion": top_emotion,
                    "score": float(score),
                }
            )
        else:
            emotion_text = "Emocion: ---"

        self.emotion_label.configure(text=emotion_text)
        self.stats_label.configure(text=self._format_stats_text())

        frame_rgb = cv2.cvtColor(frame_annotated, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        image = image.resize((800, 500), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image=image)

        self.video_label.configure(image=photo, text="")
        self.video_label.image = photo

        self.after(80, self.update_frame)

    def on_generate_report(self):
        """Genera el reporte PDF usando los conteos e historial de emociones."""
        try:
            pdf_path = generate_emotion_report(
                self.emotion_counts,
                self.emotion_history,
            )
            self.report_status_label.configure(
                text=f"Reporte generado en: {pdf_path}"
            )
        except ValueError as e:
            self.report_status_label.configure(text=str(e))
        except Exception as e:
            self.report_status_label.configure(
                text=f"Error al generar el reporte: {e}"
            )

    def close_window(self):
        """Detiene el loop, libera la cámara y cierra la ventana."""
        self.running = False
        self.camera.release()
        self.destroy()
