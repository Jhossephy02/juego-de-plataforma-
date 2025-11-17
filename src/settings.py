# src/settings.py - Configuración profesional del juego

import os

# Ventana
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = 'Rayman Full Shinobi - Music Runner'

# Física
GRAVITY = 0.6
PLAYER_SPEED = 7
PLAYER_JUMP = -15
PLAYER_DOUBLE_JUMP = -12

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
MUSIC_DIR = os.path.join(ASSETS_DIR, 'music')
PLAYER_DIR = os.path.join(ASSETS_DIR, 'player')
WORLD_DIR = os.path.join(ASSETS_DIR, 'world')

# Configuración de música
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.flac']
DEFAULT_MUSIC = 'default.mp3'

# Configuración de generación de obstáculos
OBSTACLE_CONFIG = {
    'min_distance': 200,  # Distancia mínima entre obstáculos
    'max_distance': 600,  # Distancia máxima entre obstáculos
    'spawn_distance': WIDTH + 100,  # Distancia de spawn fuera de pantalla
    'despawn_distance': -100,  # Distancia para eliminar obstáculos
    'base_speed': 5,  # Velocidad base de obstáculos
}

# Tipos de obstáculos
OBSTACLE_TYPES = {
    'spike': {
        'width': 40,
        'height': 60,
        'color': RED,
        'score': 10,
    },
    'box': {
        'width': 50,
        'height': 50,
        'color': (139, 69, 19),
        'score': 15,
    },
    'flying': {
        'width': 45,
        'height': 45,
        'color': PURPLE,
        'score': 20,
        'fly_height': 200,  # Altura de vuelo
    },
}

# Configuración de análisis de audio
AUDIO_ANALYSIS = {
    'beat_threshold': 0.3,  # Umbral para detectar beats
    'energy_threshold': 0.5,  # Umbral de energía
    'hop_length': 512,  # Tamaño de ventana para análisis
    'tempo_range': (60, 200),  # Rango de tempo válido
}

# Configuración de dificultad basada en música
DIFFICULTY_LEVELS = {
    'easy': {
        'speed_mult': 0.8,
        'obstacle_freq': 0.7,
        'score_mult': 1.0,
    },
    'normal': {
        'speed_mult': 1.0,
        'obstacle_freq': 1.0,
        'score_mult': 1.2,
    },
    'hard': {
        'speed_mult': 1.3,
        'obstacle_freq': 1.3,
        'score_mult': 1.5,
    },
    'insane': {
        'speed_mult': 1.6,
        'obstacle_freq': 1.6,
        'score_mult': 2.0,
    },
}

# UI
UI_CONFIG = {
    'score_pos': (20, 20),
    'health_pos': (WIDTH - 200, 20),
    'combo_pos': (WIDTH // 2 - 50, 50),
    'font_size': 32,
    'font_name': 'arial',
}