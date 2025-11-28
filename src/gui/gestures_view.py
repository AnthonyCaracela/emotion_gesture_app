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

        self.title("Detector de gestos")
        self.geometry("900x800")

        self.grab_set()  # ventana modal

        # --- Estado interno ---
        self.camera = Camera(index=0)
        self.hand_tracker = HandTracker(max_num_hands=1)
        self.gesture_recognizer = GestureRecognizer()
        self.keyboard_controller = KeyboardController()
        self.running = False

        # Para evitar mandar la tecla en cada frame
        self.last_sent_gesture: str | None = None

        # Variable para activar/desactivar control de teclado
        self.control_enabled = ctk.BooleanVar(value=False)

        # --- Widgets ---
        title = ctk.CTkLabel(
            self,
            text="Detector de gestos",
            font=("Arial", 22),
        )
        title.pack(pady=10)

        # Label para el video
        self.video_label = ctk.CTkLabel(self, text="Iniciando cámara...")
        self.video_label.pack(pady=10)

        # Label para mostrar el gesto detectado
        self.gesture_label = ctk.CTkLabel(
            self,
            text="Gesto: ---",
            font=("Arial", 18),
        )
        self.gesture_label.pack(pady=10)

        # --- Panel de configuración de teclas ---
        config_frame = ctk.CTkFrame(self)
        config_frame.pack(pady=10, fill="x", padx=20)

        switch = ctk.CTkSwitch(
            config_frame,
            text="Activar control de teclado",
            variable=self.control_enabled,
        )
        switch.pack(pady=10, anchor="w", padx=10)

        self.mapping_entries: dict[str, ctk.CTkEntry] = {}

        # Helper para crear filas
        def add_mapping_row(parent, gesture_name: str, label_text: str, default_key: str):
            row = ctk.CTkFrame(parent)
            row.pack(pady=5, fill="x", padx=10)
            lbl = ctk.CTkLabel(row, text=f"{label_text} → tecla:")
            lbl.pack(side="left", padx=5)
            entry = ctk.CTkEntry(row, width=60)
            entry.pack(side="left", padx=5)
            entry.insert(0, default_key)
            self.mapping_entries[gesture_name] = entry

        # OPEN_HAND
        add_mapping_row(config_frame, "OPEN_HAND", "OPEN_HAND", "d")  # ej: derecha

        # FIST
        add_mapping_row(config_frame, "FIST", "FIST", "a")  # ej: izquierda

        # PEACE (dos dedos)
        add_mapping_row(config_frame, "PEACE", "PEACE (✌)", "w")  # ej: arriba

        # INDEX (un dedo)
        add_mapping_row(config_frame, "INDEX", "INDEX (☝)", "s")  # ej: abajo

        # Botón para aplicar el mapeo
        btn_apply = ctk.CTkButton(
            config_frame,
            text="Aplicar mapeo",
            command=self.apply_mapping,
        )
        btn_apply.pack(pady=10, padx=10, anchor="w")

        # Botón cerrar
        btn_close = ctk.CTkButton(self, text="Cerrar", command=self.close_window)
        btn_close.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Inicializamos mapeo con los valores por defecto
        self.apply_mapping()

        # Intentar abrir cámara
        if self.camera.open():
            self.running = True
            self.update_frame()
        else:
            self.video_label.configure(text="No se pudo abrir la cámara")

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

        # Procesar con MediaPipe Hands
        frame_annotated, landmarks_list = self.hand_tracker.process(frame)

        gesture = "UNKNOWN"
        if landmarks_list:
            hand_landmarks = landmarks_list[0]
            gesture = self.gesture_recognizer.classify(hand_landmarks)

        display_text = f"Gesto: {gesture}"

        if self.control_enabled.get():
            if gesture != "UNKNOWN":
                mapped_key = self.keyboard_controller.get_mapping(gesture)

                # Solo mandamos tecla si el gesto cambió
                if gesture != self.last_sent_gesture and mapped_key:
                    self.keyboard_controller.press_for_gesture(gesture)
                    self.last_sent_gesture = gesture

                if mapped_key:
                    display_text += f"  (tecla: {mapped_key})"
            else:
                self.last_sent_gesture = None
        else:
            self.last_sent_gesture = None

        self.gesture_label.configure(text=display_text)

        # Convertimos el frame anotado a RGB para mostrarlo en Tkinter
        frame_rgb = cv2.cvtColor(frame_annotated, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        image = image.resize((800, 500), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image=image)

        self.video_label.configure(image=photo, text="")
        self.video_label.image = photo

        self.after(30, self.update_frame)

    def close_window(self):
        """Detiene el loop, libera cámara y cierra ventana."""
        self.running = False
        self.camera.release()
        self.destroy()
