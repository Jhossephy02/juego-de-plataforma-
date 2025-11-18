# src/core/audio_cache.py - Sistema de caché para análisis de audio

import os
import json
import hashlib
import pickle
from pathlib import Path

class AudioCache:
    """Sistema de caché para evitar re-analizar el mismo audio"""
    
    def __init__(self, cache_dir='data/cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_hash(self, filepath):
        """Genera hash único del archivo"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_cache_path(self, audio_path):
        """Obtiene ruta del archivo de caché"""
        file_hash = self._get_file_hash(audio_path)
        return self.cache_dir / f"{file_hash}.cache"
    
    def has_cache(self, audio_path):
        """Verifica si existe caché para este audio"""
        cache_path = self.get_cache_path(audio_path)
        return cache_path.exists()
    
    def load_cache(self, audio_path):
        """Carga datos del caché"""
        cache_path = self.get_cache_path(audio_path)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando caché: {e}")
            return None
    
    def save_cache(self, audio_path, analyzer_data):
        """Guarda datos al caché"""
        cache_path = self.get_cache_path(audio_path)
        
        try:
            # Preparar datos serializables
            cache_data = {
                'tempo': analyzer_data.tempo,
                'beat_times': analyzer_data.beat_times.tolist(),
                'duration': analyzer_data.duration,
                'segments': analyzer_data.segments,
                'drops': analyzer_data.drops,
                'builds': analyzer_data.builds,
                'avg_beat_interval': analyzer_data.avg_beat_interval
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            print(f"💾 Análisis guardado en caché")
            return True
        except Exception as e:
            print(f"⚠️ Error guardando caché: {e}")
            return False
    
    def clear_cache(self):
        """Limpia todo el caché"""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        print("🗑️ Caché limpiado")


# Modificar audio_analyzer.py para usar caché:
# 
# from src.core.audio_cache import AudioCache
# 
# class AudioAnalyzer:
#     def __init__(self, audio_path):
#         self.cache = AudioCache()
#         
#         # Intentar cargar desde caché
#         if self.cache.has_cache(audio_path):
#             print("📦 Cargando análisis desde caché...")
#             cached_data = self.cache.load_cache(audio_path)
#             if cached_data:
#                 self._load_from_cache(cached_data)
#                 return
#         
#         # Si no hay caché, analizar normalmente
#         print(f"🎵 Analizando: {audio_path}")
#         # ... resto del código ...
#         
#         # Guardar en caché
#         self.cache.save_cache(audio_path, self)