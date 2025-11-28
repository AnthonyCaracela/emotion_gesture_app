import cv2

def main():
    # 0 = cámara por defecto
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer el frame")
            break

        # Mostramos el frame en una ventana
        cv2.imshow("Prueba de camara", frame)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
