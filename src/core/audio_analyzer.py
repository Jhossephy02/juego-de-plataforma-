# src/core/audio_analyzer.py - Sistema REAL de análisis musical con Librosa

import pygame
import librosa
import numpy as np
import threading
from scipy import signal

class AudioAnalyzer:
    """Analizador avanzado de audio con Librosa para sincronización perfecta"""
    
    def __init__(self, audio_path):
        print(f"\n{'='*60}")
        print(f"🎵 ANALIZANDO MÚSICA: {audio_path}")
        print(f"{'='*60}")
        
        self.audio_path = audio_path
        self.analyzing = True
        
        # Valores por defecto mientras carga
        self.duration = 180.0
        self.tempo = 120
        self.beat_times = []
        self.beat_frames = []
        self.sr = 22050
        
        # Iniciar análisis en thread
        self.load_thread = threading.Thread(target=self._analyze_audio)
        self.load_thread.daemon = True
        self.load_thread.start()
        
    def _analyze_audio(self):
        """Análisis REAL del audio con Librosa"""
        try:
            print("📊 Cargando audio...")
            
            # Cargar audio con Librosa
            y, sr = librosa.load(self.audio_path, sr=22050, mono=True)
            self.sr = sr
            self.duration = librosa.get_duration(y=y, sr=sr)
            
            print(f"✓ Audio cargado: {self.duration:.1f}s @ {sr}Hz")
            print("🔍 Analizando características musicales...")
            
            # ============================================
            # 1. DETECCIÓN DE TEMPO Y BEATS (MEJORADO)
            # ============================================
            print("   → Detectando tempo y beats...")
            
            # Usar onset_strength para mejor detección
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            
            # Detección de tempo con múltiples algoritmos
            tempo, beats = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=sr,
                units='time'
            )
            
            self.tempo = float(tempo)
            self.beat_times = beats.tolist()
            self.beat_frames = librosa.time_to_frames(beats, sr=sr, hop_length=512).tolist()
            
            # Calcular intervalo promedio entre beats
            if len(self.beat_times) > 1:
                intervals = np.diff(self.beat_times)
                self.avg_beat_interval = float(np.median(intervals))
            else:
                self.avg_beat_interval = 60.0 / self.tempo
            
            print(f"   ✓ Tempo: {self.tempo:.1f} BPM")
            print(f"   ✓ Beats detectados: {len(self.beat_times)}")
            print(f"   ✓ Intervalo promedio: {self.avg_beat_interval:.3f}s")
            
            # ============================================
            # 2. ANÁLISIS DE ENERGÍA (RMS)
            # ============================================
            print("   → Analizando energía RMS...")
            
            rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
            
            # Normalizar RMS
            rms_min, rms_max = np.min(rms), np.max(rms)
            if rms_max > rms_min:
                self.rms_norm = ((rms - rms_min) / (rms_max - rms_min)).tolist()
            else:
                self.rms_norm = [0.5] * len(rms)
            
            # Tiempos correspondientes
            self.times = librosa.frames_to_time(
                np.arange(len(rms)), 
                sr=sr, 
                hop_length=512
            ).tolist()
            
            print(f"   ✓ {len(self.rms_norm)} muestras de energía")
            
            # ============================================
            # 3. CENTROIDE ESPECTRAL (brillo del sonido)
            # ============================================
            print("   → Calculando centroide espectral...")
            
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # Normalizar
            sc_min, sc_max = np.min(spectral_centroids), np.max(spectral_centroids)
            if sc_max > sc_min:
                self.spectral_centroid_norm = (
                    (spectral_centroids - sc_min) / (sc_max - sc_min)
                ).tolist()
            else:
                self.spectral_centroid_norm = [0.5] * len(spectral_centroids)
            
            # ============================================
            # 4. SEGMENTACIÓN (partes de la canción)
            # ============================================
            print("   → Segmentando estructura musical...")
            
            # Obtener segmentos estructurales
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Usar recurrence matrix para encontrar cambios
            rec = librosa.segment.recurrence_matrix(
                mfcc,
                mode='affinity',
                metric='cosine',
                width=3
            )
            
            # Detectar fronteras de segmentos
            segment_boundaries = librosa.segment.agglomerative(
                mfcc, 
                k=8  # Número de segmentos
            )
            
            segment_times = librosa.frames_to_time(segment_boundaries, sr=sr, hop_length=512)
            
            # Crear lista de segmentos con información
            self.segments = []
            for i in range(len(segment_times) - 1):
                start_time = segment_times[i]
                end_time = segment_times[i + 1]
                
                # Calcular energía promedio del segmento
                start_frame = librosa.time_to_frames(start_time, sr=sr, hop_length=512)
                end_frame = librosa.time_to_frames(end_time, sr=sr, hop_length=512)
                
                segment_rms = rms[start_frame:end_frame]
                avg_energy = float(np.mean(segment_rms)) if len(segment_rms) > 0 else 0.5
                
                # Normalizar energía del segmento
                if rms_max > rms_min:
                    avg_energy = (avg_energy - rms_min) / (rms_max - rms_min)
                
                self.segments.append({
                    'start': float(start_time),
                    'end': float(end_time),
                    'duration': float(end_time - start_time),
                    'energy': float(avg_energy)
                })
            
            print(f"   ✓ {len(self.segments)} segmentos detectados")
            
            # ============================================
            # 5. DETECCIÓN DE DROPS Y BUILDS
            # ============================================
            print("   → Detectando drops y builds...")
            
            # Usar onset strength para detectar cambios bruscos
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            
            # Suavizar para detectar tendencias
            window_size = 20
            onset_smoothed = np.convolve(
                onset_env, 
                np.ones(window_size) / window_size, 
                mode='same'
            )
            
            # Detectar picos (drops)
            peaks, properties = signal.find_peaks(
                onset_smoothed,
                height=np.percentile(onset_smoothed, 90),  # Top 10%
                distance=sr // 512 * 8  # Mínimo 8 beats de distancia
            )
            
            self.drops = librosa.frames_to_time(peaks, sr=sr, hop_length=512).tolist()
            
            # Detectar valles antes de picos (builds)
            valleys = []
            for peak in peaks:
                # Buscar valle en ventana antes del pico
                search_start = max(0, peak - sr // 512 * 16)
                search_end = peak
                
                if search_end > search_start:
                    valley_idx = search_start + np.argmin(
                        onset_smoothed[search_start:search_end]
                    )
                    valleys.append(valley_idx)
            
            self.builds = librosa.frames_to_time(
                np.array(valleys), 
                sr=sr, 
                hop_length=512
            ).tolist() if valleys else []
            
            print(f"   ✓ {len(self.drops)} drops detectados")
            print(f"   ✓ {len(self.builds)} builds detectados")
            
            # ============================================
            # RESUMEN FINAL
            # ============================================
            print(f"\n{'='*60}")
            print("✅ ANÁLISIS COMPLETADO")
            print(f"{'='*60}")
            print(f"📊 Estadísticas:")
            print(f"   • Duración: {self.duration:.1f}s")
            print(f"   • Tempo: {self.tempo:.1f} BPM")
            print(f"   • Beats: {len(self.beat_times)}")
            print(f"   • Segmentos: {len(self.segments)}")
            print(f"   • Drops: {len(self.drops)}")
            print(f"   • Builds: {len(self.builds)}")
            print(f"   • Energía promedio: {np.mean(self.rms_norm):.2f}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Error en análisis: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback a valores por defecto
            self._set_defaults()
        
        finally:
            self.analyzing = False
    
    def _set_defaults(self):
        """Valores por defecto si falla el análisis"""
        print("⚠️ Usando valores por defecto...")
        
        self.tempo = 120
        self.duration = 180.0
        
        # Generar beats artificiales
        beats_per_second = self.tempo / 60.0
        self.beat_times = [
            i / beats_per_second 
            for i in range(int(self.duration * beats_per_second))
        ]
        self.beat_frames = list(range(len(self.beat_times)))
        self.avg_beat_interval = 60.0 / self.tempo
        
        # Energía artificial
        num_samples = int(self.duration * 10)
        self.times = [i * (self.duration / num_samples) for i in range(num_samples)]
        self.rms_norm = [0.5 + np.random.uniform(-0.2, 0.2) for _ in range(num_samples)]
        self.spectral_centroid_norm = self.rms_norm.copy()
        
        # Segmentos artificiales
        self.segments = [
            {
                'start': i * (self.duration / 8),
                'end': (i + 1) * (self.duration / 8),
                'duration': self.duration / 8,
                'energy': 0.3 + i * 0.1
            }
            for i in range(8)
        ]
        
        self.drops = [self.duration * 0.25, self.duration * 0.75]
        self.builds = [self.duration * 0.5]
        self.sr = 22050
    
    # ============================================
    # MÉTODOS DE CONSULTA
    # ============================================
    
    def get_energy_at_time(self, time):
        """Obtiene energía RMS en tiempo específico"""
        if not self.times or not self.rms_norm:
            return 0.5
        
        if time < 0:
            return self.rms_norm[0]
        if time >= self.duration:
            return self.rms_norm[-1]
        
        # Interpolación lineal
        idx = np.searchsorted(self.times, time)
        
        if idx == 0:
            return self.rms_norm[0]
        if idx >= len(self.rms_norm):
            return self.rms_norm[-1]
        
        # Interpolar entre frames
        t0, t1 = self.times[idx - 1], self.times[idx]
        v0, v1 = self.rms_norm[idx - 1], self.rms_norm[idx]
        
        ratio = (time - t0) / (t1 - t0) if t1 > t0 else 0
        return v0 + (v1 - v0) * ratio
    
    def get_spectral_brightness_at_time(self, time):
        """Obtiene brillo espectral en tiempo específico"""
        if not self.times or not self.spectral_centroid_norm:
            return 0.5
        
        if time < 0:
            return self.spectral_centroid_norm[0]
        if time >= self.duration:
            return self.spectral_centroid_norm[-1]
        
        idx = np.searchsorted(self.times, time)
        
        if idx == 0:
            return self.spectral_centroid_norm[0]
        if idx >= len(self.spectral_centroid_norm):
            return self.spectral_centroid_norm[-1]
        
        return self.spectral_centroid_norm[idx]
    
    def get_intensity_at_time(self, time):
        """Combina energía y brillo para obtener intensidad general"""
        energy = self.get_energy_at_time(time)
        brightness = self.get_spectral_brightness_at_time(time)
        
        # Combinar (70% energía, 30% brillo)
        intensity = energy * 0.7 + brightness * 0.3
        
        return max(0.0, min(1.0, intensity))
    
    def is_beat(self, time, tolerance=0.1):
        """Verifica si hay un beat cerca del tiempo dado"""
        if not self.beat_times:
            return False
        
        for beat_time in self.beat_times:
            if abs(beat_time - time) < tolerance:
                return True
        
        return False
    
    def get_nearest_beat(self, time):
        """Encuentra el beat más cercano al tiempo dado"""
        if not self.beat_times:
            return None
        
        idx = np.searchsorted(self.beat_times, time)
        
        if idx == 0:
            return self.beat_times[0]
        if idx >= len(self.beat_times):
            return self.beat_times[-1]
        
        # Comparar beat anterior y siguiente
        prev_beat = self.beat_times[idx - 1]
        next_beat = self.beat_times[idx]
        
        if abs(time - prev_beat) < abs(time - next_beat):
            return prev_beat
        else:
            return next_beat
    
    def is_drop(self, time, tolerance=0.5):
        """Verifica si hay un drop cerca"""
        if not self.drops:
            return False
        
        for drop_time in self.drops:
            if abs(drop_time - time) < tolerance:
                return True
        
        return False
    
    def is_build(self, time, tolerance=0.5):
        """Verifica si hay un build cerca"""
        if not self.builds:
            return False
        
        for build_time in self.builds:
            if abs(build_time - time) < tolerance:
                return True
        
        return False
    
    def get_next_beat_time(self, current_time):
        """Obtiene tiempo del siguiente beat"""
        if not self.beat_times:
            return None
        
        for beat_time in self.beat_times:
            if beat_time > current_time:
                return beat_time
        
        return None
    
    def get_difficulty_at_time(self, time):
        """Calcula dificultad basada en características musicales"""
        intensity = self.get_intensity_at_time(time)
        
        # Progreso en la canción (aumenta dificultad con el tiempo)
        progress = min(1.0, time / self.duration) if self.duration > 0 else 0
        
        # Verificar si está en un drop (dificultad máxima)
        in_drop = self.is_drop(time, tolerance=1.0)
        drop_boost = 0.3 if in_drop else 0
        
        # Combinar factores
        difficulty = (intensity * 0.5 + progress * 0.3 + drop_boost)
        
        return max(0.2, min(1.0, difficulty))
    
    def get_segment_at_time(self, time):
        """Obtiene el segmento musical en el tiempo dado"""
        for segment in self.segments:
            if segment['start'] <= time <= segment['end']:
                return segment
        
        return None