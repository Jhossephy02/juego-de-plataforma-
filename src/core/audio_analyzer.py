# src/core/audio_analyzer.py - Sistema avanzado de análisis musical
import librosa
import numpy as np
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

class AudioAnalyzer:
    """Analiza archivos de audio para generar obstáculos sincronizados"""
    
    def __init__(self, audio_path):
        print(f"🎵 Analizando: {audio_path}")
        
        # Cargar audio
        self.y, self.sr = librosa.load(audio_path, sr=22050, mono=True)
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)
        
        print(f"⏱️  Duración: {self.duration:.1f}s")
        
        # Análisis de tempo y beats
        self._analyze_tempo()
        
        # Análisis de energía espectral
        self._analyze_energy()
        
        # Análisis de segmentos musicales
        self._analyze_segments()
        
        # Detección de cambios bruscos (drops, crescendos)
        self._analyze_dynamics()
        
        print(f"✅ Análisis completado!")
        print(f"   🥁 Tempo: {self.tempo:.0f} BPM")
        print(f"   🎼 Beats detectados: {len(self.beat_times)}")
        print(f"   📊 Segmentos: {len(self.segments)}")
    
    def _analyze_tempo(self):
        """Analiza tempo y beats"""
        # Detección de tempo
        tempo, beat_frames = librosa.beat.beat_track(
            y=self.y, 
            sr=self.sr,
            hop_length=512
        )
        
        self.tempo = tempo
        self.beat_frames = beat_frames
        self.beat_times = librosa.frames_to_time(
            beat_frames, 
            sr=self.sr, 
            hop_length=512
        )
        
        # Calcular intervalos entre beats
        self.beat_intervals = np.diff(self.beat_times)
        self.avg_beat_interval = np.mean(self.beat_intervals)
    
    def _analyze_energy(self):
        """Analiza la energía espectral a lo largo del tiempo"""
        # RMS Energy
        self.rms = librosa.feature.rms(y=self.y, hop_length=512)[0]
        
        # Spectral Centroid (brillo del sonido)
        self.spectral_centroid = librosa.feature.spectral_centroid(
            y=self.y, 
            sr=self.sr, 
            hop_length=512
        )[0]
        
        # Zero Crossing Rate (percusividad)
        self.zcr = librosa.feature.zero_crossing_rate(
            y=self.y, 
            hop_length=512
        )[0]
        
        # Normalizar
        self.rms_norm = (self.rms - np.min(self.rms)) / (np.max(self.rms) - np.min(self.rms) + 1e-8)
        self.spectral_centroid_norm = (self.spectral_centroid - np.min(self.spectral_centroid)) / \
                                       (np.max(self.spectral_centroid) - np.min(self.spectral_centroid) + 1e-8)
        
        # Convertir frames a tiempo
        self.times = librosa.frames_to_time(
            np.arange(len(self.rms)), 
            sr=self.sr, 
            hop_length=512
        )
    
    def _analyze_segments(self):
        """Segmenta la canción en partes con características similares"""
        # Chromagram para detección de cambios armónicos
        chroma = librosa.feature.chroma_cqt(y=self.y, sr=self.sr)
        
        # Detección de segmentos
        boundaries = librosa.segment.agglomerative(chroma, k=8)
        boundary_times = librosa.frames_to_time(boundaries, sr=self.sr)
        
        # Crear segmentos con información de energía promedio
        self.segments = []
        for i in range(len(boundary_times) - 1):
            start_time = boundary_times[i]
            end_time = boundary_times[i + 1]
            
            # Calcular energía promedio del segmento
            start_idx = int(start_time * self.sr / 512)
            end_idx = int(end_time * self.sr / 512)
            
            avg_energy = np.mean(self.rms_norm[start_idx:end_idx])
            
            self.segments.append({
                'start': start_time,
                'end': end_time,
                'energy': avg_energy,
                'duration': end_time - start_time
            })
    
    def _analyze_dynamics(self):
        """Detecta cambios dinámicos importantes (drops, builds)"""
        # Calcular diferencias en energía
        energy_diff = np.diff(self.rms_norm)
        
        # Suavizar
        energy_diff_smooth = signal.savgol_filter(
            energy_diff, 
            window_length=min(51, len(energy_diff) // 2 * 2 + 1), 
            polyorder=3
        )
        
        # Detectar picos (drops/builds)
        threshold = np.std(energy_diff_smooth) * 2
        peaks, _ = signal.find_peaks(np.abs(energy_diff_smooth), height=threshold)
        
        self.dynamic_changes = librosa.frames_to_time(peaks, sr=self.sr, hop_length=512)
        
        # Clasificar como drop o build
        self.drops = []
        self.builds = []
        
        for peak in peaks:
            if peak < len(energy_diff_smooth):
                if energy_diff_smooth[peak] > 0:
                    self.builds.append(librosa.frames_to_time(peak, sr=self.sr, hop_length=512))
                else:
                    self.drops.append(librosa.frames_to_time(peak, sr=self.sr, hop_length=512))
    
    def get_energy_at_time(self, time):
        """Obtiene la energía en un momento específico"""
        idx = int(time * self.sr / 512)
        if 0 <= idx < len(self.rms_norm):
            return self.rms_norm[idx]
        return 0.5
    
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
        
        return np.clip(intensity, 0, 1)
    
    def is_beat(self, time, tolerance=0.05):
        """Verifica si hay un beat cerca del tiempo dado"""
        return any(abs(beat_time - time) < tolerance for beat_time in self.beat_times)
    
    def is_drop(self, time, tolerance=0.2):
        """Verifica si hay un drop cerca del tiempo dado"""
        return any(abs(drop_time - time) < tolerance for drop_time in self.drops)
    
    def is_build(self, time, tolerance=0.2):
        """Verifica si hay un build cerca del tiempo dado"""
        return any(abs(build_time - time) < tolerance for build_time in self.builds)
    
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
        
        return np.clip(difficulty, 0.2, 1.0)
    