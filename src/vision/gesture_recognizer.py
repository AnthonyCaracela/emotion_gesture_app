from typing import List
from mediapipe.framework.formats import landmark_pb2
import math


class GestureRecognizer:
    """
    Clasifica gestos de mano simples usando MediaPipe Hands.

    Gestos soportados:
      - OPEN_HAND: todos los dedos extendidos (incluido pulgar)
      - FIST: todos los dedos recogidos (incluido pulgar)
      - PEACE: índice y medio extendidos, resto doblados
      - INDEX: solo índice extendido
      - LIKE: solo pulgar extendido (👍)
      - UNKNOWN: cualquier otra cosa
    """

    # Índices estándar de MediaPipe Hands
    FINGER_TIPS = [4, 8, 12, 16, 20]   # [pulgar, índice, medio, anular, meñique]
    FINGER_PIPS = [3, 6, 10, 14, 18]

    @staticmethod
    def _dist(a: landmark_pb2.NormalizedLandmark,
              b: landmark_pb2.NormalizedLandmark) -> float:
        """Distancia euclidiana en coordenadas normalizadas (x, y)."""
        return math.hypot(a.x - b.x, a.y - b.y)

    def _thumb_extended(self, lm: List[landmark_pb2.NormalizedLandmark]) -> bool:
        """
        Determina si el pulgar está extendido usando distancias desde la muñeca.

        Idea:
          - Si la punta del pulgar (tip) está claramente más lejos de la muñeca
            que la articulación intermedia (IP), consideramos que está extendido.
        """
        wrist = lm[0]
        thumb_ip = lm[self.FINGER_PIPS[0]]   # 3
        thumb_tip = lm[self.FINGER_TIPS[0]]  # 4

        d_tip = self._dist(thumb_tip, wrist)
        d_ip = self._dist(thumb_ip, wrist)

        # Umbral: si la punta está ~0.03 más lejos que la IP, lo consideramos extendido.
        # 0.03 = 3% de la altura/ancho de la imagen aprox. (ajustable si hace falta)
        return d_tip > d_ip + 0.03

    def classify(self, hand_landmarks: List[landmark_pb2.NormalizedLandmark]) -> str:
        if len(hand_landmarks) != 21:
            return "UNKNOWN"

        lm = hand_landmarks

        # ----- Estado del pulgar (orientación-independiente) -----
        thumb_extended = self._thumb_extended(lm)

        # ----- Estado de los demás dedos (índice, medio, anular, meñique) -----
        finger_states = []  # [index, middle, ring, pinky]

        for tip_idx, pip_idx in zip(self.FINGER_TIPS[1:], self.FINGER_PIPS[1:]):
            tip = lm[tip_idx]
            pip = lm[pip_idx]
            # y menor => más arriba en la imagen => más extendido hacia arriba.
            # En la práctica, la mayoría de gestos los haces "más o menos verticales",
            # así que esto funciona bastante bien.
            is_extended = tip.y < pip.y
            finger_states.append(is_extended)

        index_ext, middle_ext, ring_ext, pinky_ext = finger_states

        # ================= LÓGICA DE CLASIFICACIÓN =================

        # 1) OPEN_HAND: los 5 dedos extendidos
        if thumb_extended and index_ext and middle_ext and ring_ext and pinky_ext:
            return "OPEN_HAND"

        # 2) LIKE (👍): SOLO pulgar extendido
        if thumb_extended and not index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return "LIKE"

        # 3) FIST: ningún dedo extendido (incluido pulgar)
        if not thumb_extended and not index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return "FIST"

        # 4) INDEX: solo índice extendido
        if not thumb_extended and index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return "INDEX"

        # 5) PEACE: índice y medio extendidos, resto doblados
        if (
            not thumb_extended
            and index_ext
            and middle_ext
            and not ring_ext
            and not pinky_ext
        ):
            return "PEACE"

        # Cualquier otra combinación
        return "UNKNOWN"
