"""
Mapeo de emociones a archivos de música
"""

import os


class EmotionMapper:
    """
    Mapea emociones detectadas a archivos de música correspondientes
    """
    
    def __init__(self, assets_path="src/music/assets"):
        self.assets_path = assets_path
        
        # Mapeo: emoción → archivo de música
        self.emotion_music_map = {
            "happy": "happy.mp3",
            "sad": "sad.mp3",
            "angry": "angry.mp3",
            "surprise": "surprise.mp3",
            "neutral": "neutral.mp3"
        }
        
        # Descripciones (para mostrar al usuario)
        self.descriptions = {
            "happy": "Música alegre y energética",
            "sad": "Piano melancólico reconfortante",
            "angry": "Flauta relajante para calmar",
            "surprise": "Música energética y sorprendente",
            "neutral": "Música ambiental de fondo"
        }
    
    def get_music_path(self, emotion):
        """
        Obtiene la ruta completa del archivo de música para una emoción
        
        Args:
            emotion: Nombre de la emoción
            
        Returns:
            str: Ruta completa al archivo de música, o None si no existe
        """
        if emotion not in self.emotion_music_map:
            return None
        
        filename = self.emotion_music_map[emotion]
        filepath = os.path.join(self.assets_path, filename)
        
        # Verificar que el archivo existe
        if os.path.exists(filepath):
            return filepath
        else:
            print(f"⚠️ Archivo no encontrado: {filepath}")
            return None
    
    def get_description(self, emotion):
        """Obtiene la descripción de la música para una emoción"""
        return self.descriptions.get(emotion, "Música de fondo")
    
    def set_custom_music(self, emotion, filepath):
        """
        Permite al usuario personalizar la música para una emoción
        
        Args:
            emotion: Emoción a personalizar
            filepath: Ruta al nuevo archivo de música
        """
        if os.path.exists(filepath):
            filename = os.path.basename(filepath)
            self.emotion_music_map[emotion] = filename
            print(f"✅ Música personalizada para {emotion}: {filename}")
        else:
            print(f"❌ Archivo no existe: {filepath}")