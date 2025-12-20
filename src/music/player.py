"""
Reproductor de música basado en emociones con estabilización
"""

import pygame
import time
from collections import Counter
from typing import Optional
from .emotion_mapper import EmotionMapper


class MusicPlayer:
    """
    Reproductor de música que cambia según la emoción detectada.
    Incluye sistema de estabilización para evitar cambios bruscos.
    """
    
    def __init__(self, assets_path="src/music/assets"):
        # Inicializar pygame mixer
        pygame.mixer.init()
        
        # Mapper de emociones
        self.emotion_mapper = EmotionMapper(assets_path)
        
        # Estado actual
        self.current_stable_emotion = None
        self.current_music_path = None
        self.is_playing = False
        
        # Sistema de estabilización
        self.emotion_history = []
        self.BUFFER_SIZE = 60  # Últimas 60 detecciones (~20 segundos a 3 FPS)
        self.MIN_PERCENTAGE = 0.6  # 60% para considerar estable
        self.MIN_SAMPLES = 30  # Mínimo 30 muestras antes de decidir
        
        # Control de volumen
        self.volume = 0.5  # 50% por defecto
        pygame.mixer.music.set_volume(self.volume)
        
        # Control de fade
        self.FADE_DURATION_MS = 2000  # 2 segundos
        
        print("🎵 MusicPlayer inicializado")
        print(f"📊 Buffer: {self.BUFFER_SIZE} detecciones")
        print(f"📈 Umbral de cambio: {self.MIN_PERCENTAGE*100}%")
    
    def update_emotion(self, detected_emotion: str):
        """
        Actualiza el historial de emociones y decide si cambiar la música.
        
        Args:
            detected_emotion: Emoción detectada en el frame actual
        """
        if detected_emotion is None:
            return
        
        # Agregar a historial
        self.emotion_history.append(detected_emotion)
        
        # Mantener solo las últimas N detecciones
        if len(self.emotion_history) > self.BUFFER_SIZE:
            self.emotion_history.pop(0)
        
        # Calcular emoción dominante solo si tenemos suficientes muestras
        if len(self.emotion_history) >= self.MIN_SAMPLES:
            dominant_emotion = self._get_dominant_emotion()
            
            # Cambiar música solo si la emoción dominante cambió
            if dominant_emotion != self.current_stable_emotion:
                self._change_music(dominant_emotion)
    
    def _get_dominant_emotion(self) -> Optional[str]:
        """
        Calcula la emoción dominante en el historial.
        
        Returns:
            str: Emoción dominante, o None si no hay suficientes datos
        """
        if len(self.emotion_history) < self.MIN_SAMPLES:
            return None
        
        # Contar frecuencias
        emotion_counts = Counter(self.emotion_history)
        
        # Obtener la más frecuente
        dominant, count = emotion_counts.most_common(1)[0]
        percentage = count / len(self.emotion_history)
        
        # Solo aceptar si supera el umbral
        if percentage >= self.MIN_PERCENTAGE:
            return dominant
        else:
            # Si ninguna emoción es dominante, mantener la actual
            return self.current_stable_emotion
    
    def _change_music(self, new_emotion: str):
        """
        Cambia la música a la correspondiente a la nueva emoción.
        Incluye fade out/in para transición suave.
        
        Args:
            new_emotion: Nueva emoción a reproducir
        """
        # Obtener ruta del archivo de música
        music_path = self.emotion_mapper.get_music_path(new_emotion)
        
        if music_path is None:
            print(f"⚠️ No hay música disponible para: {new_emotion}")
            return
        
        # Si ya está sonando esta música, no hacer nada
        if music_path == self.current_music_path and self.is_playing:
            return
        
        print(f"🎵 Cambiando música: {self.current_stable_emotion} → {new_emotion}")
        print(f"📁 Archivo: {music_path}")
        print(f"📝 {self.emotion_mapper.get_description(new_emotion)}")
        
        # Fade out de la música actual
        if self.is_playing:
            pygame.mixer.music.fadeout(self.FADE_DURATION_MS)
            time.sleep(self.FADE_DURATION_MS / 1000.0)
        
        # Cargar nueva música
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1, fade_ms=self.FADE_DURATION_MS)  # Loop infinito con fade in
            
            self.current_music_path = music_path
            self.current_stable_emotion = new_emotion
            self.is_playing = True
            
            print(f"✅ Reproduciendo: {new_emotion}")
            
        except Exception as e:
            print(f"❌ Error al reproducir música: {e}")
    
    def play(self):
        """Inicia la reproducción de música"""
        if self.current_music_path and not self.is_playing:
            pygame.mixer.music.play(-1)
            self.is_playing = True
            print("▶️ Música iniciada")
    
    def pause(self):
        """Pausa la reproducción"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            print("⏸️ Música pausada")
    
    def resume(self):
        """Reanuda la reproducción"""
        if not self.is_playing:
            pygame.mixer.music.unpause()
            self.is_playing = True
            print("▶️ Música reanudada")
    
    def stop(self):
        """Detiene completamente la reproducción"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_music_path = None
        self.current_stable_emotion = None
        self.emotion_history.clear()
        print("⏹️ Música detenida")
    
    def set_volume(self, volume: float):
        """
        Ajusta el volumen de reproducción.
        
        Args:
            volume: Volumen entre 0.0 y 1.0
        """
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        print(f"🔊 Volumen: {self.volume*100:.0f}%")
    
    def get_current_emotion(self) -> Optional[str]:
        """Obtiene la emoción actual estable"""
        return self.current_stable_emotion
    
    def get_emotion_stats(self) -> dict:
        """
        Obtiene estadísticas del historial de emociones.
        
        Returns:
            dict: Conteo de cada emoción en el historial
        """
        if not self.emotion_history:
            return {}
        
        counts = Counter(self.emotion_history)
        total = len(self.emotion_history)
        
        return {
            emotion: {
                "count": count,
                "percentage": (count / total) * 100
            }
            for emotion, count in counts.items()
        }