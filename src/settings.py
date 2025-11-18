# src/settings.py - Configuración MEJORADA con física optimizada

import os

# ============================================
# VENTANA
# ============================================
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = 'Rayman Full Shinobi - Music Runner'

# ============================================
# FÍSICA MEJORADA
# ============================================
# Gravedad más fuerte para mejor control
GRAVITY = 0.7

# Velocidad del jugador
PLAYER_SPEED = 7

# Saltos más potentes y responsivos
PLAYER_JUMP = -17  # Aumentado de -15 a -17
PLAYER_DOUBLE_JUMP = -14  # Aumentado de -12 a -14

# Coyote time: frames extras para saltar después de caer
COYOTE_TIME = 0.15  # 150ms

# Jump buffer: frames que se recuerda el input de salto
JUMP_BUFFER_TIME = 0.1  # 100ms

# ============================================
# COLORES
# ============================================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
ORANGE = (255, 150, 0)
CYAN = (0, 255, 255)

# ============================================
# RUTAS
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
MUSIC_DIR = os.path.join(ASSETS_DIR, 'music')
PLAYER_DIR = os.path.join(ASSETS_DIR, 'player')
WORLD_DIR = os.path.join(ASSETS_DIR, 'world')

# ============================================
# CONFIGURACIÓN DE MÚSICA
# ============================================
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.flac']
DEFAULT_MUSIC = 'default.mp3'

# ============================================
# CONFIGURACIÓN DE OBSTÁCULOS MEJORADA
# ============================================
OBSTACLE_CONFIG = {
    'min_distance': 300,  # Aumentado para más tiempo de reacción
    'max_distance': 700,
    'spawn_distance': WIDTH + 100,
    'despawn_distance': -200,
    'base_speed': 6,  # Ajustado para mejor balance
}

# ============================================
# TIPOS DE OBSTÁCULOS BALANCEADOS
# ============================================
OBSTACLE_TYPES = {
    'spike': {
        'width': 45,  # Ligeramente más grandes para mejor visibilidad
        'height': 65,
        'color': RED,
        'score': 10,
    },
    'box': {
        'width': 55,
        'height': 55,
        'color': (139, 69, 19),
        'score': 15,
    },
    'flying': {
        'width': 50,
        'height': 50,
        'color': PURPLE,
        'score': 20,
        'fly_height': 180,  # Reducido para más predecible
    },
}

# ============================================
# CONFIGURACIÓN DE ANÁLISIS DE AUDIO
# ============================================
AUDIO_ANALYSIS = {
    'beat_threshold': 0.3,
    'energy_threshold': 0.5,
    'hop_length': 512,
    'tempo_range': (60, 200),
    # Configuración de sincronización
    'sync_tolerance': 0.1,  # 100ms de tolerancia para beats
    'beat_spawn_probability': 0.7,  # 70% de beats spawn obstáculos
    'intensity_spawn_boost': 0.3,  # Boost basado en intensidad
}

# ============================================
# DIFICULTAD
# ============================================
DIFFICULTY_LEVELS = {
    'easy': {
        'speed_mult': 0.7,
        'obstacle_freq': 0.6,
        'score_mult': 1.0,
        'description': 'Ideal para principiantes',
    },
    'normal': {
        'speed_mult': 1.0,
        'obstacle_freq': 1.0,
        'score_mult': 1.2,
        'description': 'Experiencia balanceada',
    },
    'hard': {
        'speed_mult': 1.3,
        'obstacle_freq': 1.3,
        'score_mult': 1.5,
        'description': 'Para jugadores experimentados',
    },
    'insane': {
        'speed_mult': 1.6,
        'obstacle_freq': 1.6,
        'score_mult': 2.0,
        'description': '¡Solo para los mejores!',
    },
}

# ============================================
# UI
# ============================================
UI_CONFIG = {
    'score_pos': (20, 20),
    'health_pos': (WIDTH - 200, 20),
    'combo_pos': (WIDTH // 2 - 50, 50),
    'font_size': 32,
    'font_name': 'arial',
    
    # Feedback visual
    'damage_flash_duration': 0.2,
    'combo_fade_time': 2.0,
    'perfect_dodge_distance': 50,  # Píxeles para esquiva perfecta
}

# ============================================
# POWER-UPS
# ============================================
POWERUP_CONFIG = {
    'shield': {
        'duration': 5.0,
        'color': (100, 200, 255),
        'spawn_chance': 0.3,
    },
    'invincible': {
        'duration': 5.0,
        'color': (255, 100, 255),
        'spawn_chance': 0.2,
    },
    'slow': {
        'duration': 3.0,
        'color': (255, 200, 100),
        'spawn_chance': 0.15,
    },
}

# ============================================
# DEBUG
# ============================================
DEBUG_MODE = False  # Cambia a True para ver hitboxes
SHOW_FPS = False
SHOW_BEAT_MARKERS = True  # Mostrar indicadores de beat