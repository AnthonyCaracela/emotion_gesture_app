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
        self._center_window(900, 720)
        self.resizable(True, True)  # ✅ se puede redimensionar

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

        # ====== LAYOUT GENERAL ======
        root_frame = ctk.CTkFrame(self, corner_radius=15)
        root_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Título y subtítulo (fijos arriba)
        title = ctk.CTkLabel(
            root_frame,
            text="Detector de gestos",
            font=("Arial", 24, "bold"),
        )
        title.pack(pady=(10, 5))

        subtitle = ctk.CTkLabel(
            root_frame,
            text="Reconocimiento de gestos de mano y control de teclado",
            font=("Arial", 13),
        )
        subtitle.pack(pady=(0, 10))

        # ==== CONTENIDO SCROLLABLE (video + mapeos) ====
        scroll_frame = ctk.CTkScrollableFrame(
            root_frame,
            corner_radius=15,
            label_text="",  # sin título
        )
        scroll_frame.pack(expand=True, fill="both", padx=5, pady=5)

        # Frame para video
        video_frame = ctk.CTkFrame(scroll_frame, corner_radius=15)
        video_frame.pack(pady=10)
        self.video_label = ctk.CTkLabel(video_frame, text="Iniciando cámara...")
        self.video_label.pack(padx=10, pady=10)

        # Label para mostrar el gesto detectado
        self.gesture_label = ctk.CTkLabel(
            scroll_frame,
            text="Gesto: ---",
            font=("Arial", 18),
        )
        self.gesture_label.pack(pady=10)

        # Panel de configuración de teclas
        config_frame = ctk.CTkFrame(scroll_frame)
        config_frame.pack(pady=10, fill="x", padx=10)

        switch = ctk.CTkSwitch(
            config_frame,
            text="Activar control de teclado",
            variable=self.control_enabled,
        )
        switch.pack(pady=10, anchor="w", padx=10)

        self.mapping_entries: dict[str, ctk.CTkEntry] = {}

        def add_mapping_row(parent, gesture_name: str, label_text: str, default_key: str):
            row = ctk.CTkFrame(parent)
            row.pack(pady=3, fill="x", padx=10)
            lbl = ctk.CTkLabel(row, text=f"{label_text} → tecla:")
            lbl.pack(side="left", padx=5)
            entry = ctk.CTkEntry(row, width=60)
            entry.pack(side="left", padx=5)
            entry.insert(0, default_key)
            self.mapping_entries[gesture_name] = entry

        # OPEN_HAND (🖐)
        add_mapping_row(config_frame, "OPEN_HAND", "OPEN_HAND (🖐)", "d")

        # FIST (✊)
        add_mapping_row(config_frame, "FIST", "FIST (✊)", "a")

        # PEACE (✌)
        add_mapping_row(config_frame, "PEACE", "PEACE (✌)", "w")

        # INDEX (☝)
        add_mapping_row(config_frame, "INDEX", "INDEX (☝)", "s")

        # LIKE (👍)
        add_mapping_row(config_frame, "LIKE", "LIKE (👍)", "l")

        # Botón para aplicar el mapeo
        btn_apply = ctk.CTkButton(
            config_frame,
            text="Aplicar mapeo",
            command=self.apply_mapping,
        )
        btn_apply.pack(pady=10, padx=10, anchor="w")

        # ==== BOTÓN CERRAR (fijo abajo, fuera del scroll) ====
        buttons_frame = ctk.CTkFrame(root_frame, fg_color="transparent")
        buttons_frame.pack(pady=(5, 0))

        btn_close = ctk.CTkButton(buttons_frame, text="Cerrar", command=self.close_window)
        btn_close.pack(pady=5)

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Inicializamos mapeo con los valores por defecto
        self.apply_mapping()

        # Intentar abrir cámara
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

        # Mostrar frame en la UI
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
