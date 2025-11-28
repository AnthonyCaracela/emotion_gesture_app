import cv2
import numpy as np
import mediapipe as mp
from typing import Any, Dict, Optional, Tuple


class EmotionRecognizer:
    """
    Detector de emociones simplificado usando únicamente MediaPipe Face Mesh.

    Emociones: happy, neutral, surprised, sad, angry.
    La lógica se basa en:
      - Apertura de la boca (mouth_ratio).
      - Curvatura de la boca (mouth_curve: esquinas arriba/abajo).
    """

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # Umbrales más sensibles (SONRISA y SORPRESA menos exageradas)
        self.TH_SURPRISED = 0.30      # antes 0.36 -> ahora detecta sorpresa con menos apertura
        self.TH_HAPPY = 0.15          # antes 0.18 -> sonrisa más fácil
        self.TH_SAD_CLOSED = 0.10     # boca muy cerrada
        self.TH_CURVE_HAPPY = -0.005  # antes -0.01 -> basta una curvita ligera hacia arriba
        self.TH_CURVE_SAD = 0.015     # antes 0.02 -> tristeza con menos caída

    def _landmark_point(self, landmark, width: int, height: int) -> Tuple[int, int]:
        """Convierte un landmark normalizado a coordenadas de pixel."""
        return int(landmark.x * width), int(landmark.y * height)

    def analyze(
        self, frame_bgr
    ) -> Tuple[Any, Optional[str], float, Dict[str, float]]:
        """
        Analiza un frame BGR y devuelve:
          (frame_annotated, top_emotion, score, emotions_dict)
        """
        if frame_bgr is None:
            return frame_bgr, None, 0.0, {}

        h, w, _ = frame_bgr.shape

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        if not results.multi_face_landmarks:
            return frame_bgr, None, 0.0, {}

        face_landmarks = results.multi_face_landmarks[0].landmark

        # Puntos clave de boca
        try:
            lm = face_landmarks
            x_left, y_left = self._landmark_point(lm[61], w, h)     # comisura izq.
            x_right, y_right = self._landmark_point(lm[291], w, h)  # comisura der.
            x_top, y_top = self._landmark_point(lm[13], w, h)       # labio sup. centro
            x_bottom, y_bottom = self._landmark_point(lm[14], w, h) # labio inf. centro
        except IndexError:
            return frame_bgr, None, 0.0, {}

        mouth_width = np.linalg.norm(np.array([x_right - x_left, y_right - y_left]))
        mouth_height = np.linalg.norm(np.array([x_bottom - x_top, y_bottom - y_top]))

        if mouth_width < 1:
            return frame_bgr, None, 0.0, {}

        mouth_ratio = float(mouth_height / mouth_width)

        # Curvatura de la boca (esquinas vs labio superior)
        avg_corners_y = (y_left + y_right) / 2.0
        mouth_curve = (avg_corners_y - y_top) / mouth_width  # normalizado por ancho

        emotions: Dict[str, float] = {
            "happy": 0.0,
            "neutral": 0.0,
            "surprised": 0.0,
            "sad": 0.0,
            "angry": 0.0,
        }

        # --- Reglas heurísticas ---
        if mouth_ratio > self.TH_SURPRISED:
            top_emotion = "surprised"
        else:
            if mouth_ratio > self.TH_HAPPY:
                # Boca moderadamente abierta -> feliz / triste / neutral según curva
                if mouth_curve <= self.TH_CURVE_HAPPY:
                    top_emotion = "happy"
                elif mouth_curve >= self.TH_CURVE_SAD:
                    top_emotion = "sad"
                else:
                    top_emotion = "neutral"
            else:
                # Boca más cerrada
                if mouth_ratio < self.TH_SAD_CLOSED and mouth_curve >= self.TH_CURVE_SAD + 0.005:
                    # Esquinas hacia abajo y boca cerrada -> triste
                    top_emotion = "sad"
                elif mouth_ratio < self.TH_SAD_CLOSED and abs(mouth_curve) < 0.012:
                    # Boca cerrada y casi recta -> enojo
                    top_emotion = "angry"
                else:
                    top_emotion = "neutral"

        emotions[top_emotion] = 1.0
        score = mouth_ratio  # seguimos usando la apertura como "score"

        xs = [int(l.x * w) for l in face_landmarks]
        ys = [int(l.y * h) for l in face_landmarks]
        x_min, x_max = max(min(xs), 0), min(max(xs), w - 1)
        y_min, y_max = max(min(ys), 0), min(max(ys), h - 1)

        frame_annotated = frame_bgr.copy()
        cv2.rectangle(frame_annotated, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

        label = f"{top_emotion} {score:.2f}"
        cv2.putText(
            frame_annotated,
            label,
            (x_min, max(y_min - 10, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

        return frame_annotated, top_emotion, score, emotions
