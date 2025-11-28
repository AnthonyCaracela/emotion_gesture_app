from typing import Dict, Optional

from pynput.keyboard import Controller


class KeyboardController:
    """
    Envuelve pynput para mapear gestos -> teclas.
    Solo hace pulsaciones rápidas (press + release).
    """

    def __init__(self, gesture_to_key: Optional[Dict[str, str]] = None):
        self.keyboard = Controller()
        self.gesture_to_key: Dict[str, str] = gesture_to_key or {}

    def set_mapping(self, gesture: str, key: str) -> None:
        """Asigna una tecla (carácter) a un gesto."""
        key = key.strip()
        if key:
            self.gesture_to_key[gesture] = key

    def get_mapping(self, gesture: str) -> Optional[str]:
        """Devuelve la tecla asociada a un gesto, o None si no hay."""
        return self.gesture_to_key.get(gesture)

    def press_for_gesture(self, gesture: str) -> None:
        """
        Si el gesto tiene una tecla asignada, simula una pulsación rápida.
        La tecla se envía a la ventana que tenga el foco en el sistema.
        """
        key = self.get_mapping(gesture)
        if not key:
            return

        # Pulsación rápida: press + release
        self.keyboard.press(key)
        self.keyboard.release(key)
