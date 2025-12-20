"""
Reconocedor de Gestos Mejorado v2
Mejor diferenciación entre FIST y LIKE
"""

from typing import List
from mediapipe.framework.formats import landmark_pb2
import math


class GestureRecognizer:
    """
    Clasifica gestos de mano usando MediaPipe Hands.
    
    Versión 2: Mejor diferenciación FIST vs LIKE

    Gestos soportados:
      - OPEN_HAND: todos los dedos extendidos (🖐️)
      - FIST: todos los dedos recogidos (✊)
      - PEACE: índice y medio extendidos (✌️)
      - INDEX: solo índice extendido (☝️)
      - LIKE: pulgar MUY extendido hacia arriba, resto cerrado (👍)
      - UNKNOWN: cualquier otra cosa
    """

    # Índices estándar de MediaPipe Hands
    FINGER_TIPS = [4, 8, 12, 16, 20]   # [pulgar, índice, medio, anular, meñique]
    FINGER_PIPS = [3, 6, 10, 14, 18]
    FINGER_MCPS = [2, 5, 9, 13, 17]    # Nudillos

    @staticmethod
    def _dist(a, b) -> float:
        """Distancia euclidiana en coordenadas normalizadas (x, y)."""
        return math.hypot(a.x - b.x, a.y - b.y)

    def _thumb_clearly_extended(self, lm) -> bool:
        """
        Detecta si el pulgar está CLARAMENTE extendido (para LIKE).
        Requiere que el pulgar esté significativamente separado.
        """
        wrist = lm[0]
        thumb_tip = lm[4]
        thumb_ip = lm[3]
        thumb_mcp = lm[2]
        index_mcp = lm[5]
        middle_mcp = lm[9]
        
        # Distancias
        d_tip_wrist = self._dist(thumb_tip, wrist)
        d_ip_wrist = self._dist(thumb_ip, wrist)
        d_mcp_wrist = self._dist(thumb_mcp, wrist)
        
        # Para LIKE: el pulgar debe estar MUY extendido
        # La punta debe estar significativamente más lejos que la IP
        clearly_extended = d_tip_wrist > d_ip_wrist + 0.06  # Umbral más alto
        
        # Además, verificar que el pulgar apunta hacia ARRIBA
        # (no solo hacia el lado como en un puño natural)
        thumb_points_up = thumb_tip.y < thumb_mcp.y - 0.05
        
        # O que está muy separado horizontalmente (pulgar lateral)
        thumb_very_separated = abs(thumb_tip.x - index_mcp.x) > 0.12
        
        return clearly_extended and (thumb_points_up or thumb_very_separated)

    def _thumb_relaxed(self, lm) -> bool:
        """
        Detecta si el pulgar está en posición relajada/neutral (como en un puño).
        """
        wrist = lm[0]
        thumb_tip = lm[4]
        thumb_ip = lm[3]
        thumb_mcp = lm[2]
        index_mcp = lm[5]
        
        # Distancias
        d_tip_wrist = self._dist(thumb_tip, wrist)
        d_ip_wrist = self._dist(thumb_ip, wrist)
        
        # Pulgar relajado: punta NO está mucho más lejos que IP
        not_extended = d_tip_wrist < d_ip_wrist + 0.05
        
        # O el pulgar está cerca del índice (posición de puño)
        d_tip_index = self._dist(thumb_tip, index_mcp)
        near_index = d_tip_index < 0.10
        
        return not_extended or near_index

    def _thumb_extended_for_open(self, lm) -> bool:
        """
        Detecta pulgar extendido para OPEN_HAND (menos estricto que LIKE).
        """
        wrist = lm[0]
        thumb_tip = lm[4]
        thumb_ip = lm[3]
        
        d_tip_wrist = self._dist(thumb_tip, wrist)
        d_ip_wrist = self._dist(thumb_ip, wrist)
        
        return d_tip_wrist > d_ip_wrist + 0.03

    def _finger_extended(self, lm, finger_idx: int) -> bool:
        """
        Detecta si un dedo (no pulgar) está extendido.
        finger_idx: 1=índice, 2=medio, 3=anular, 4=meñique
        """
        tip = lm[self.FINGER_TIPS[finger_idx]]
        pip = lm[self.FINGER_PIPS[finger_idx]]
        mcp = lm[self.FINGER_MCPS[finger_idx]]
        
        # Dedo extendido: punta más arriba que PIP
        return tip.y < pip.y - 0.02

    def _finger_curled(self, lm, finger_idx: int) -> bool:
        """
        Detecta si un dedo está cerrado.
        Más tolerante para detectar puños.
        """
        tip = lm[self.FINGER_TIPS[finger_idx]]
        pip = lm[self.FINGER_PIPS[finger_idx]]
        mcp = lm[self.FINGER_MCPS[finger_idx]]
        wrist = lm[0]
        
        # Dedo cerrado: punta debajo o cerca del PIP
        tip_below_pip = tip.y > pip.y - 0.02
        
        # También: punta cerca de la palma
        d_tip_wrist = self._dist(tip, wrist)
        d_mcp_wrist = self._dist(mcp, wrist)
        tip_near_palm = d_tip_wrist < d_mcp_wrist + 0.06
        
        return tip_below_pip or tip_near_palm

    def classify(self, hand_landmarks) -> str:
        if len(hand_landmarks) != 21:
            return "UNKNOWN"

        lm = hand_landmarks

        # ----- Estado de los dedos -----
        index_ext = self._finger_extended(lm, 1)
        middle_ext = self._finger_extended(lm, 2)
        ring_ext = self._finger_extended(lm, 3)
        pinky_ext = self._finger_extended(lm, 4)
        
        index_curled = self._finger_curled(lm, 1)
        middle_curled = self._finger_curled(lm, 2)
        ring_curled = self._finger_curled(lm, 3)
        pinky_curled = self._finger_curled(lm, 4)
        
        all_fingers_extended = index_ext and middle_ext and ring_ext and pinky_ext
        all_fingers_curled = index_curled and middle_curled and ring_curled and pinky_curled
        no_fingers_extended = not index_ext and not middle_ext and not ring_ext and not pinky_ext

        # ----- Estado del pulgar -----
        thumb_clearly_up = self._thumb_clearly_extended(lm)  # Para LIKE
        thumb_relaxed = self._thumb_relaxed(lm)              # Para FIST
        thumb_extended = self._thumb_extended_for_open(lm)   # Para OPEN_HAND

        # ================= LÓGICA DE CLASIFICACIÓN =================
        # IMPORTANTE: El orden importa! Más específico primero.

        # 1) OPEN_HAND (🖐️): todos los dedos extendidos incluyendo pulgar
        if thumb_extended and all_fingers_extended:
            return "OPEN_HAND"

        # 2) FIST (✊): todos cerrados, pulgar relajado/no extendido claramente
        #    PRIORIDAD sobre LIKE para evitar falsos positivos
        if no_fingers_extended and thumb_relaxed and not thumb_clearly_up:
            return "FIST"
        
        # 3) LIKE (👍): pulgar CLARAMENTE extendido hacia arriba, resto cerrado
        if thumb_clearly_up and all_fingers_curled:
            return "LIKE"

        # 4) INDEX (☝️): solo índice extendido
        if index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return "INDEX"

        # 5) PEACE (✌️): índice y medio extendidos
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            return "PEACE"

        # 6) Segundo intento FIST: si todos los dedos están cerrados
        if all_fingers_curled and not thumb_clearly_up:
            return "FIST"

        return "UNKNOWN"