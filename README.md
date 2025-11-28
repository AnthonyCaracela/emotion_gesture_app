# Emotion & Gesture App

Aplicación de escritorio en Python que detecta **emociones faciales** y **gestos de mano** en tiempo real usando la cámara web.

## Características principales

- Detector de **emociones básicas** (happy, neutral, surprised, sad, angry) usando MediaPipe Face Mesh.
- Detector de **gestos de mano**:
  - Mano abierta 🖐
  - Puño ✊
  - Símbolo de paz ✌
  - Dedo índice levantado ☝
- Mapeo de gestos a teclas configurable (ejemplo: mover en un juego).
- Generación de **reporte PDF** con:
  - Resumen del análisis.
  - Gráfica de la probabilidad de las emociones en el tiempo.
  - Tabla de eventos destacados (cambios importantes de emoción).

## Requisitos

- Python 3.12 (o compatible con las versiones de las librerías).
- Windows 10/11.
- Cámara web funcional.

Las dependencias se encuentran en `requirements.txt` e incluyen, entre otras:

- `opencv-python`
- `mediapipe`
- `customtkinter`
- `pynput`
- `matplotlib`
- `fpdf2`

## Instalación

```bash
# 1. Clonar el repositorio (cuando ya esté en GitHub)
git clone https://github.com/AnthonyCaracela/emotion_gesture_app.git
cd emotion_gesture_app

# 2. Crear y activar entorno virtual (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt
