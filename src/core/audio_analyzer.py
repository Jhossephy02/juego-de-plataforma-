# src/core/audio_analyzer.py - Versión SOLO con Pygame (sin librosa)

import pygame
import os

class AudioAnalyzer:
    """Analizador de audio simplificado usando solo pygame"""
    
    def __init__(self, audio_path):
        print(f"🎵 Analizando: {audio_path}")
        
        try:
            # Cargar audio con pygame
            sound = pygame.mixer.Sound(audio_path)
            
            # Obtener duración en segundos
            self.duration = sound.get_length()
            
            print(f"⏱️  Duración: {self.duration:.1f}s")
            
            # Generar análisis basado en BPM estándar
            self._generate_simple_analysis()
            
            print(f"✅ Análisis completado!")
            print(f"   🥁 Tempo: {self.tempo} BPM")
            print(f"   🎼 Beats estimados: {len(self.beat_times)}")
            print(f"   📊 Segmentos: {len(self.segments)}")
            
        except Exception as e:
            print(f"❌ Error cargando audio: {e}")
            print(f"   Usando valores por defecto...")
            self._set_defaults()
    
    def _set_defaults(self):
        """Establece valores por defecto"""
        self.duration = 180.0
        self.tempo = 120
        self._generate_simple_analysis()
    
    def _generate_simple_analysis(self):
        """Genera análisis musical simplificado"""
        # Tempo estándar (BPM)
        self.tempo = 120
        
        # Calcular beats basado en BPM
        beats_per_second = self.tempo / 60.0
        num_beats = int(self.duration * beats_per_second)
        
        # Generar tiempos de beats uniformemente distribuidos
        self.beat_times = []
        beat_interval = 60.0 / self.tempo
        
        current_time = 0
        while current_time < self.duration:
            self.beat_times.append(current_time)
            current_time += beat_interval
        
        self.avg_beat_interval = beat_interval
        self.beat_intervals = [beat_interval] * len(self.beat_times)
        
        # Generar energía simulada (aumenta gradualmente)
        num_samples = int(self.duration * 10)  # 10 muestras/segundo
        self.times = [i * (self.duration / num_samples) for i in range(num_samples)]
        
        # Energía que aumenta con el tiempo y tiene variaciones
        import math
        self.rms_norm = []
        for t in self.times:
            # Base que aumenta con el tiempo
            base = 0.3 + (t / self.duration) * 0.4
            # Variación sinusoidal
            variation = 0.2 * math.sin(t * 2)
            energy = base + variation
            self.rms_norm.append(max(0.2, min(1.0, energy)))
        
        # Normalización espectral (similar a la energía)
        self.spectral_centroid_norm = self.rms_norm.copy()
        
        # Segmentos (dividir canción en 8 partes)
        num_segments = 8
        self.segments = []
        segment_duration = self.duration / num_segments
        
        for i in range(num_segments):
            start = i * segment_duration
            end = (i + 1) * segment_duration
            # Energía aumenta con el segmento
            energy = 0.3 + (i / num_segments) * 0.5
            
            self.segments.append({
                'start': start,
                'end': end,
                'energy': energy,
                'duration': segment_duration
            })
        
        # Drops (cambios bruscos) - en cuartos de la canción
        self.drops = [
            self.duration * 0.25,
            self.duration * 0.75
        ]
        
        # Builds (crescendos) - en la mitad
        self.builds = [
            self.duration * 0.5
        ]
        
        # Frames (compatibilidad)
        self.beat_frames = list(range(len(self.beat_times)))
        
        # Sample rate (estándar)
        self.sr = 22050
    
    def get_energy_at_time(self, time):
        """Obtiene la energía en un momento específico"""
        if time < 0 or time > self.duration:
            return 0.5
        
        # Encontrar índice más cercano
        idx = int((time / self.duration) * len(self.rms_norm))
        idx = max(0, min(idx, len(self.rms_norm) - 1))
        
        return self.rms_norm[idx]
    
    def get_intensity_at_time(self, time):
        """Obtiene un valor de intensidad combinado (0-1)"""
        energy = self.get_energy_at_time(time)
        
        # Buscar el segmento actual
        current_segment_energy = 0.5
        for segment in self.segments:
            if segment['start'] <= time <= segment['end']:
                current_segment_energy = segment['energy']
                break
        
        # Combinar energía instantánea con promedio del segmento
        intensity = (energy * 0.7 + current_segment_energy * 0.3)
        
        return max(0.0, min(1.0, intensity))
    
    def is_beat(self, time, tolerance=0.1):
        """Verifica si hay un beat cerca del tiempo dado"""
        for beat_time in self.beat_times:
            if abs(beat_time - time) < tolerance:
                return True
        return False
    
    def is_drop(self, time, tolerance=0.3):
        """Verifica si hay un drop cerca del tiempo dado"""
        for drop_time in self.drops:
            if abs(drop_time - time) < tolerance:
                return True
        return False
    
    def is_build(self, time, tolerance=0.3):
        """Verifica si hay un build cerca del tiempo dado"""
        for build_time in self.builds:
            if abs(build_time - time) < tolerance:
                return True
        return False
    
    def get_next_beat_time(self, current_time):
        """Obtiene el tiempo del siguiente beat"""
        for beat_time in self.beat_times:
            if beat_time > current_time:
                return beat_time
        return None
    
    def get_difficulty_at_time(self, time):
        """Calcula la dificultad sugerida basada en la música"""
        intensity = self.get_intensity_at_time(time)
        
        # Ajustar según el progreso de la canción
        progress = time / self.duration
        
        # La dificultad aumenta con el tiempo y la intensidad
        difficulty = (intensity * 0.7 + progress * 0.3)
        
        return max(0.2, min(1.0, difficulty))