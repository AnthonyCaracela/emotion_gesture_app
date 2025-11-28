import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

from vision.camera import Camera
from vision.emotion_recognizer import EmotionRecognizer
from reports.emotion_report import generate_emotion_report


class EmotionsWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Detector de emociones")
        self.geometry("900x800")

        # Ventana modal (bloquea la principal mientras está abierta)
        self.grab_set()

        # --- Estado interno ---
        self.camera = Camera(index=0)
        self.emotion_recognizer = EmotionRecognizer()
        self.running = False

        # Última emoción y conteo de emociones (por frames)
        self.current_emotion: str | None = None
        self.emotion_counts: dict[str, int] = {}

        # --- Widgets ---
        title = ctk.CTkLabel(
            self,
            text="Detector de emociones",
            font=("Arial", 22),
        )
        title.pack(pady=10)

        # Label para el video
        self.video_label = ctk.CTkLabel(self, text="Iniciando cámara...")
        self.video_label.pack(pady=10)

        # Label para mostrar la emoción actual
        self.emotion_label = ctk.CTkLabel(
            self,
            text="Emoción: ---",
            font=("Arial", 18),
        )
        self.emotion_label.pack(pady=5)

        # Label para mostrar estadísticas
        self.stats_label = ctk.CTkLabel(
            self,
            text="Estadísticas (frames): ---",
            font=("Arial", 14),
            justify="left",
        )
        self.stats_label.pack(pady=5)

        # Mensaje de estado del reporte
        self.report_status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 12),
        )
        self.report_status_label.pack(pady=5)

        # Botón para generar reporte PDF
        btn_report = ctk.CTkButton(
            self,
            text="Generar reporte PDF",
            command=self.on_generate_report,
        )
        btn_report.pack(pady=5)

        # Botón cerrar
        btn_close = ctk.CTkButton(self, text="Cerrar", command=self.close_window)
        btn_close.pack(pady=10)

        # Manejar cierre con la X
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Intentar abrir cámara
        if self.camera.open():
            self.running = True
            self.update_frame()
        else:
            self.video_label.configure(text="No se pudo abrir la cámara")

    def _format_stats_text(self) -> str:
        """Construye el texto de estadísticas a partir del diccionario."""
        if not self.emotion_counts:
            return "Estadísticas (frames): ---"

        # Ordenamos de mayor a menor conteo
        items = sorted(
            self.emotion_counts.items(),
            key=lambda kv: kv[1],
            reverse=True,
        )
        parts = [f"{name}: {count}" for name, count in items]
        return "Estadísticas (frames): " + "   ".join(parts)

    def update_frame(self):
        """Lee un frame, detecta emoción, anota y actualiza la UI."""
        if not self.running:
            return

        ret, frame = self.camera.read()
        if not ret or frame is None:
            self.after(50, self.update_frame)
            return

        # Analizar emoción
        frame_annotated, top_emotion, score, emotions = \
            self.emotion_recognizer.analyze(frame)

        # Actualizar emoción actual y conteo
        if top_emotion is not None:
            self.current_emotion = top_emotion
            self.emotion_counts[top_emotion] = (
                self.emotion_counts.get(top_emotion, 0) + 1
            )
            emotion_text = f"Emoción: {top_emotion} ({score:.2f})"
        else:
            emotion_text = "Emoción: ---"

        self.emotion_label.configure(text=emotion_text)
        self.stats_label.configure(text=self._format_stats_text())

        # Convertir frame anotado a RGB para mostrarlo en Tkinter
        frame_rgb = cv2.cvtColor(frame_annotated, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        image = image.resize((800, 500), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image=image)

        self.video_label.configure(image=photo, text="")
        self.video_label.image = photo

        # Volver a llamar a esta función
        self.after(80, self.update_frame)  # ~12 FPS

    def on_generate_report(self):
        """Genera el reporte PDF usando los conteos de emociones actuales."""
        try:
            pdf_path = generate_emotion_report(self.emotion_counts, output_dir="reports")
            self.report_status_label.configure(
                text=f"Reporte generado en: {pdf_path}"
            )
        except ValueError as e:
            # No hay datos suficientes todavía
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

