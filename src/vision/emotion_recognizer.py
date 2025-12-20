"""
Detector de emociones usando FER (Facial Expression Recognition)
Optimizado para video en tiempo real
Precisión: ~85-97%

Contribución de Gustavo al proyecto de Arquitectura de Computadoras
"""

import cv2
import numpy as np
from typing import Any, Dict, Optional, Tuple
from fer.fer import FER
import warnings
import os

# Suprimir warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore')


class EmotionRecognizer:
    """
    Detector de emociones usando FER con MTCNN.
    
    FER está optimizado para video en tiempo real, a diferencia de DeepFace
    que está diseñado para fotos estáticas.
    
    Emociones detectadas:
    - angry, disgust, fear, happy, sad, surprise, neutral
    
    Mapeadas a 5 categorías del proyecto:
    - happy, sad, angry, surprise, neutral
    """

    # Mapeo de emociones FER → Proyecto
    EMOTION_MAP = {
        "happy": "happy",
        "sad": "sad", 
        "angry": "angry",
        "surprise": "surprise",
        "neutral": "neutral",
        "fear": "sad",
        "disgust": "angry"
    }

    def __init__(self):
        """Inicializa el detector FER con MTCNN"""
        print("🔄 Cargando modelo FER + MTCNN...")
        try:
            self.detector = FER(mtcnn=True)
            print("✅ EmotionRecognizer con FER inicializado")
            print("   Precisión: ~85-97% | Velocidad: Tiempo real")
        except Exception as e:
            print(f"⚠️ Error inicializando FER: {e}")
            self.detector = None

    def analyze(self, frame_bgr) -> Tuple[Any, Optional[str], float, Dict[str, float]]:
        """
        Analiza emociones en un frame usando FER
        
        Args:
            frame_bgr: Frame en formato BGR (OpenCV)
            
        Returns:
            Tuple con:
            - frame_annotated: Frame con anotaciones dibujadas
            - top_emotion: Emoción dominante (o None si no detecta)
            - confidence: Confianza de la predicción (0-1)
            - emotions: Dict con todas las emociones y sus scores normalizados
        """
        if frame_bgr is None or self.detector is None:
            return frame_bgr, None, 0.0, {}

        try:
            # Detectar emociones con FER
            results = self.detector.detect_emotions(frame_bgr)
            
            if not results or len(results) == 0:
                return frame_bgr, None, 0.0, {}
            
            # Tomar primera cara detectada
            result = results[0]
            
            # Obtener emociones (vienen en escala 0-1)
            raw_emotions = result.get('emotions', {})
            
            if not raw_emotions:
                return frame_bgr, None, 0.0, {}
            
            # Consolidar emociones al formato del proyecto (5 emociones)
            emotions_consolidated = {
                "happy": 0.0,
                "sad": 0.0,
                "angry": 0.0,
                "surprise": 0.0,
                "neutral": 0.0
            }
            
            # Sumar emociones mapeadas
            for fer_emo, project_emo in self.EMOTION_MAP.items():
                if fer_emo in raw_emotions:
                    emotions_consolidated[project_emo] += raw_emotions[fer_emo]
            
            # Normalizar a 0-1
            total = sum(emotions_consolidated.values())
            if total > 0:
                emotions_normalized = {
                    k: v / total for k, v in emotions_consolidated.items()
                }
            else:
                emotions_normalized = emotions_consolidated
            
            # Obtener emoción dominante
            top_emotion = max(emotions_normalized, key=emotions_normalized.get)
            confidence = emotions_normalized[top_emotion]
            
            # Obtener bounding box de la cara
            box = result.get('box', [0, 0, 0, 0])
            x, y, w, h = box
            
            # Dibujar resultados
            frame_annotated = self._draw_results(
                frame_bgr.copy(), 
                top_emotion, 
                confidence,
                x, y, w, h,
                emotions_normalized
            )
            
            return frame_annotated, top_emotion, confidence, emotions_normalized
            
        except Exception as e:
            # En caso de error, retornar frame sin modificar
            # print(f"⚠️ Error en análisis: {e}")  # Descomentar para debug
            return frame_bgr, None, 0.0, {}

    def _draw_results(self, frame, emotion: str, confidence: float, 
                      x: int, y: int, w: int, h: int,
                      all_emotions: Dict[str, float]):
        """
        Dibuja los resultados en el frame
        """
        # Colores según emoción (BGR)
        color_map = {
            "happy": (0, 255, 0),      # Verde
            "sad": (255, 0, 0),        # Azul
            "angry": (0, 0, 255),      # Rojo
            "surprise": (0, 255, 255), # Amarillo
            "neutral": (200, 200, 200) # Gris
        }
        
        color = color_map.get(emotion, (255, 255, 255))
        
        if w > 0 and h > 0:
            # Rectángulo alrededor de la cara
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Etiqueta con emoción y porcentaje
            label = f"{emotion.upper()} {confidence*100:.1f}%"
            
            # Fondo para texto
            (text_w, text_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )
            
            cv2.rectangle(
                frame,
                (x, y - text_h - 15),
                (x + text_w + 10, y),
                color,
                -1
            )
            
            # Texto
            cv2.putText(
                frame,
                label,
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 0),
                2,
            )
            
            # Barra de confianza
            bar_width = int(w * confidence)
            cv2.rectangle(
                frame,
                (x, y + h + 5),
                (x + bar_width, y + h + 15),
                color,
                -1
            )
            cv2.rectangle(
                frame,
                (x, y + h + 5),
                (x + w, y + h + 15),
                color,
                1
            )
        
        return frame