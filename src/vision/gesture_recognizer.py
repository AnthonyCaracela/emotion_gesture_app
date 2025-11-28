from typing import List
from mediapipe.framework.formats import landmark_pb2


class GestureRecognizer:
    """
    Clasifica gestos de mano simples usando MediaPipe Hands.

    Gestos soportados:
      - OPEN_HAND: todos los dedos (excepto pulgar) extendidos
      - FIST: todos los dedos recogidos
      - PEACE: índice y medio extendidos
      - INDEX: solo índice extendido
      - UNKNOWN: cualquier otra cosa
    """

    # Índices estándar de MediaPipe Hands
    FINGER_TIPS = [4, 8, 12, 16, 20]   # [pulgar, índice, medio, anular, meñique]
    FINGER_PIPS = [3, 6, 10, 14, 18]

    def classify(self, hand_landmarks: List[landmark_pb2.NormalizedLandmark]) -> str:
        if len(hand_landmarks) != 21:
            return "UNKNOWN"

        finger_states = []

        # Ignoramos pulgar (índice 0 de estas listas) y usamos solo
        # índice, medio, anular, meñique
        for tip_idx, pip_idx in zip(self.FINGER_TIPS[1:], self.FINGER_PIPS[1:]):
            tip = hand_landmarks[tip_idx]
            pip = hand_landmarks[pip_idx]

            # Si la punta está más arriba (y menor) => dedo extendido
            is_extended = tip.y < pip.y
            finger_states.append(is_extended)

        # finger_states = [index, middle, ring, pinky]
        index_ext, middle_ext, ring_ext, pinky_ext = finger_states

        # Mano abierta (4 dedos extendidos)
        if index_ext and middle_ext and ring_ext and pinky_ext:
            return "OPEN_HAND"

        # Puño cerrado (ningún dedo extendido)
        if not index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return "FIST"

        # Solo índice levantado
        if index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return "INDEX"

        # Símbolo de paz (índice + medio)
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            return "PEACE"

        return "UNKNOWN"
