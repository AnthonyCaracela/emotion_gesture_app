"""
Controlador de Teclado - Gestos a Teclas
Soporta teclas especiales como space, up, down, etc.
"""

from typing import Dict, Optional
from pynput.keyboard import Controller, Key


class KeyboardController:
    """
    Envuelve pynput para mapear gestos -> teclas.
    Solo hace pulsaciones rápidas (press + release).
    
    Soporta teclas especiales:
    - space, up, down, left, right
    - enter, esc, tab, backspace
    - shift, ctrl, alt
    """

    # Mapeo de nombres de teclas especiales
    SPECIAL_KEYS = {
        'space': Key.space,
        'up': Key.up,
        'down': Key.down,
        'left': Key.left,
        'right': Key.right,
        'enter': Key.enter,
        'return': Key.enter,
        'esc': Key.esc,
        'escape': Key.esc,
        'tab': Key.tab,
        'backspace': Key.backspace,
        'delete': Key.delete,
        'shift': Key.shift,
        'ctrl': Key.ctrl,
        'alt': Key.alt,
        'home': Key.home,
        'end': Key.end,
        'pageup': Key.page_up,
        'pagedown': Key.page_down,
        'f1': Key.f1,
        'f2': Key.f2,
        'f3': Key.f3,
        'f4': Key.f4,
        'f5': Key.f5,
    }

    def __init__(self, gesture_to_key: Optional[Dict[str, str]] = None):
        self.keyboard = Controller()
        self.gesture_to_key: Dict[str, str] = gesture_to_key or {}

    def set_mapping(self, gesture: str, key: str) -> None:
        """Asigna una tecla (carácter o especial) a un gesto."""
        key = key.strip().lower()
        if key:
            self.gesture_to_key[gesture] = key

    def get_mapping(self, gesture: str) -> Optional[str]:
        """Devuelve la tecla asociada a un gesto, o None si no hay."""
        return self.gesture_to_key.get(gesture)

    def _resolve_key(self, key_name: str):
        """
        Convierte el nombre de la tecla al formato de pynput.
        - Si es una tecla especial (space, up, etc), retorna Key.xxx
        - Si es un caracter normal (a, b, 1, etc), retorna el caracter
        """
        key_lower = key_name.lower().strip()
        
        # Verificar si es una tecla especial
        if key_lower in self.SPECIAL_KEYS:
            return self.SPECIAL_KEYS[key_lower]
        
        # Si es un solo caracter, retornarlo tal cual
        if len(key_name) == 1:
            return key_name
        
        # Si no se reconoce, intentar como caracter
        return key_name[0] if key_name else None

    def press_for_gesture(self, gesture: str) -> None:
        """
        Si el gesto tiene una tecla asignada, simula una pulsación rápida.
        La tecla se envía a la ventana que tenga el foco en el sistema.
        """
        key_name = self.get_mapping(gesture)
        if not key_name:
            return

        # Resolver la tecla (especial o normal)
        key = self._resolve_key(key_name)
        if key is None:
            return

        # Pulsación rápida: press + release
        try:
            self.keyboard.press(key)
            self.keyboard.release(key)
        except Exception as e:
            print(f"⚠️ Error al presionar tecla '{key_name}': {e}")