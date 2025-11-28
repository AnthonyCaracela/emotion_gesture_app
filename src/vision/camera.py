import cv2


class Camera:
    """Encapsula el manejo de la cámara con OpenCV."""

    def __init__(self, index: int = 0):
        """
        index: índice de la cámara (0 = cámara web por defecto).
        """
        self.index = index
        self.cap = None

    def open(self) -> bool:
        """Abre la cámara si no está abierta. Devuelve True si se abrió bien."""
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.index)

        return self.cap.isOpened()

    def read(self):
        """
        Devuelve (ret, frame) como cv2.VideoCapture.read().
        ret = True/False, frame = imagen BGR o None.
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None

        return self.cap.read()

    def release(self):
        """Libera la cámara si está abierta."""
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            self.cap = None
