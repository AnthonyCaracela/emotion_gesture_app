import cv2
import mediapipe as mp


class HandTracker:
    """
    Encapsula MediaPipe Hands para detectar manos y dibujar landmarks.
    """

    def __init__(
        self,
        max_num_hands: int = 1,
        detection_confidence: float = 0.5,
        tracking_confidence: float = 0.5,
    ):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def process(self, frame_bgr):
        """
        Procesa un frame BGR de OpenCV.
        Devuelve:
          - frame_annotated_bgr: frame con landmarks dibujados
          - landmarks_list: lista de listas de landmarks (cada uno con x, y, z normalizados)
        """
        if frame_bgr is None:
            return frame_bgr, []

        # Convertimos BGR -> RGB para MediaPipe
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False

        results = self.hands.process(frame_rgb)

        frame_bgr.flags.writeable = True
        frame_annotated = frame_bgr.copy()

        landmarks_list = []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dibujar landmarks sobre la imagen
                self.mp_drawing.draw_landmarks(
                    frame_annotated,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style(),
                )

                # Guardar la lista de landmarks (x, y, z normalizados 0–1)
                landmarks_list.append(hand_landmarks.landmark)

        return frame_annotated, landmarks_list
