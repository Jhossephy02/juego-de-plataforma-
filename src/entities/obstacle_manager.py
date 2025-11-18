# src/entities/obstacle_manager.py - Sistema mejorado con sincronización musical perfecta

import pygame
import random
import math
from src.settings import (WIDTH, HEIGHT, OBSTACLE_CONFIG, OBSTACLE_TYPES, 
                          RED, PURPLE, YELLOW, GREEN, BLUE, WHITE)

class Obstacle(pygame.sprite.Sprite):
    """Obstáculo mejorado"""
    
    def __init__(self, x, y, obstacle_type, speed, sync_beat=False, beat_strength=0.5):
        super().__init__()
        
        self.type = obstacle_type
        config = OBSTACLE_TYPES[obstacle_type]
        
        # Dimensiones
        self.width = config['width']
        self.height = config['height']
        self.color = config['color']
        self.score = config['score']
        
        # Posición y movimiento
        self.x = x
        self.y = y
        self.speed = speed
        
        # Sincronización musical
        self.sync_beat = sync_beat
        self.beat_strength = beat_strength  # Qué tan fuerte es el beat (0-1)
        self.pulse_time = 0
        self.glow_intensity = 0
        self.animation_time = 0
        
        # Para voladores
        if obstacle_type == 'flying':
            self.fly_height = config['fly_height']
            self.fly_time = random.uniform(0, math.pi * 2)
            self.fly_speed = random.uniform(2, 4)
        
        # Crear superficie
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        # Hitbox más generosa (80% del sprite)
        hitbox_shrink = 0.2
        self.hitbox = self.rect.inflate(
            -int(self.width * hitbox_shrink),
            -int(self.height * hitbox_shrink)
        )
        
        self.update_visual()
    
    def update_visual(self):
        """Actualiza visual del obstáculo"""
        self.image.fill((0, 0, 0, 0))
        
        # Escala por pulso de beat
        scale = 1.0
        if self.sync_beat and self.pulse_time > 0:
            scale = 1.0 + (self.pulse_time * 0.2 * self.beat_strength)
            self.pulse_time -= 0.05
        
        w = int(self.width * scale)
        h = int(self.height * scale)
        
        # Dibujar según tipo
        if self.type == 'spike':
            self._draw_spike_improved(w, h)
        elif self.type == 'box':
            self._draw_box_improved(w, h)
        elif self.type == 'flying':
            self._draw_flying_improved(w, h)
        
        # Resplandor si está sincronizado
        if self.sync_beat and self.glow_intensity > 0:
            glow_surf = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
            glow_color = (*self.color, int(self.glow_intensity * 150))
            pygame.draw.rect(glow_surf, glow_color, (10, 10, w, h), border_radius=5)
            self.image.blit(glow_surf, (-10, -10))
            self.glow_intensity -= 0.05
    
    def _draw_spike_improved(self, w, h):
        """Dibuja espiga mejorada"""
        points = [(w // 2, 5), (w - 5, h - 5), (5, h - 5)]
        
        # Sombra
        shadow_points = [(p[0] + 2, p[1] + 2) for p in points]
        pygame.draw.polygon(self.image, (100, 0, 0), shadow_points)
        
        # Cuerpo principal
        pygame.draw.polygon(self.image, self.color, points)
        
        # Highlight
        highlight_points = [(w // 2, 8), (w // 2 + 5, h // 2), (w // 2, h // 2)]
        pygame.draw.polygon(self.image, (255, 150, 150), highlight_points)
        
        # Borde
        pygame.draw.polygon(self.image, (200, 0, 0), points, 3)
    
    def _draw_box_improved(self, w, h):
        """Dibuja caja mejorada"""
        main_rect = (5, 5, w - 10, h - 10)
        
        # Sombra
        shadow_rect = (7, 7, w - 10, h - 10)
        pygame.draw.rect(self.image, (80, 40, 10), shadow_rect, border_radius=5)
        
        # Cuerpo
        pygame.draw.rect(self.image, self.color, main_rect, border_radius=5)
        
        # Efecto 3D - tapa
        top_points = [(5, 5), (w - 5, 5), (w - 8, 8), (8, 8)]
        pygame.draw.polygon(self.image, (180, 120, 60), top_points)
        
        # Efecto 3D - lado
        right_points = [(w - 5, 5), (w - 5, h - 5), (w - 8, h - 8), (w - 8, 8)]
        pygame.draw.polygon(self.image, (100, 60, 20), right_points)
        
        # Tablas de madera
        plank_y = 15
        while plank_y < h - 15:
            pygame.draw.line(self.image, (100, 50, 20), 
                           (10, plank_y), (w - 10, plank_y), 2)
            plank_y += 15
        
        # Clavos
        for nail_x in [12, w - 12]:
            for nail_y in [12, h // 2, h - 12]:
                pygame.draw.circle(self.image, (60, 60, 60), (nail_x, nail_y), 3)
                pygame.draw.circle(self.image, (100, 100, 100), (nail_x, nail_y), 2)
        
        # Borde
        pygame.draw.rect(self.image, (100, 50, 20), main_rect, 3, border_radius=5)
    
    def _draw_flying_improved(self, w, h):
        """Dibuja enemigo volador"""
        center = (w // 2, h // 2)
        float_offset = int(math.sin(self.animation_time * 3) * 3)
        
        # Cuerpo principal (fantasma)
        pygame.draw.circle(self.image, self.color, 
                          (center[0], center[1] + float_offset), 
                          min(w, h) // 2 - 3)
        
        # Brazos flotantes
        pygame.draw.circle(self.image, self.color, 
                          (center[0] - 8, center[1] + float_offset - 5), 
                          min(w, h) // 3)
        pygame.draw.circle(self.image, self.color, 
                          (center[0] + 8, center[1] + float_offset - 5), 
                          min(w, h) // 3)
        
        # Cola ondulante
        wave_points = []
        for i in range(8):
            x = 5 + (w - 10) * i / 7
            y = center[1] + float_offset + 12 + math.sin(i + self.animation_time * 5) * 3
            wave_points.append((int(x), int(y)))
        
        wave_points.append((w - 5, center[1] + float_offset))
        wave_points.append((5, center[1] + float_offset))
        pygame.draw.polygon(self.image, self.color, wave_points)
        
        # Ojos
        eye_y = center[1] + float_offset - 5
        pygame.draw.ellipse(self.image, WHITE, (center[0] - 12, eye_y - 5, 8, 10))
        pygame.draw.circle(self.image, (0, 0, 0), (center[0] - 8, eye_y), 3)
        pygame.draw.ellipse(self.image, WHITE, (center[0] + 4, eye_y - 5, 8, 10))
        pygame.draw.circle(self.image, (0, 0, 0), (center[0] + 8, eye_y), 3)
        
        # Cejas
        pygame.draw.line(self.image, (0, 0, 0), 
                        (center[0] - 15, eye_y - 8), 
                        (center[0] - 5, eye_y - 6), 3)
        pygame.draw.line(self.image, (0, 0, 0), 
                        (center[0] + 5, eye_y - 6), 
                        (center[0] + 15, eye_y - 8), 3)
        
        # Boca
        mouth_y = center[1] + float_offset + 5
        mouth_points = [
            (center[0] - 10, mouth_y),
            (center[0] - 5, mouth_y + 5),
            (center[0], mouth_y),
            (center[0] + 5, mouth_y + 5),
            (center[0] + 10, mouth_y)
        ]
        pygame.draw.lines(self.image, (0, 0, 0), False, mouth_points, 3)
        
        # Borde brillante
        pygame.draw.circle(self.image, WHITE, 
                          (center[0], center[1] + float_offset), 
                          min(w, h) // 2 - 3, 2)
        
        # Resplandor
        glow_radius = min(w, h) // 2 + 5
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_color = (*self.color, 50)
        pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
        self.image.blit(glow_surf, 
                       (center[0] - glow_radius, center[1] + float_offset - glow_radius))
    
    def trigger_beat_pulse(self):
        """Activa efecto de beat"""
        self.pulse_time = 1.0
        self.glow_intensity = 1.0
    
    def update(self, dt):
        """Actualiza obstáculo"""
        self.animation_time += dt
        self.x -= self.speed * dt * 60
        self.rect.x = int(self.x)
        
        # Actualizar hitbox
        self.hitbox.x = self.rect.x + int(self.width * 0.1)
        
        # Movimiento de voladores
        if self.type == 'flying':
            self.fly_time += dt * self.fly_speed
            offset_y = math.sin(self.fly_time) * 30
            self.rect.y = int(self.y + offset_y)
            self.hitbox.y = self.rect.y + int(self.height * 0.1)
        else:
            self.rect.y = int(self.y)
            self.hitbox.y = self.rect.y + int(self.height * 0.1)
        
        self.update_visual()
        
        # Eliminar si sale de pantalla
        if self.x < -200:
            self.kill()
    
    def draw(self, screen, debug=False):
        """Dibuja obstáculo"""
        screen.blit(self.image, self.rect)
        
        # Debug: mostrar hitbox
        if debug:
            pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)
    
    def get_score(self):
        """Puntuación por esquivar"""
        bonus = 10 if self.sync_beat else 0
        return self.score + bonus


class PowerUp(pygame.sprite.Sprite):
    """Power-up mejorado"""
    
    def __init__(self, x, y, powerup_type, speed):
        super().__init__()
        
        self.type = powerup_type
        self.x = x
        self.y = y
        self.speed = speed
        
        self.size = 35
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Hitbox más generosa
        self.hitbox = self.rect.inflate(-10, -10)
        
        self.rotation = 0
        self.pulse = 0
        
        if powerup_type == 'shield':
            self.color = (100, 200, 255)
            self.symbol = 'shield'
        elif powerup_type == 'slow':
            self.color = (255, 200, 100)
            self.symbol = 'clock'
        elif powerup_type == 'invincible':
            self.color = (255, 100, 255)
            self.symbol = 'star'
    
    def update(self, dt):
        """Actualiza power-up"""
        self.x -= self.speed * dt * 60
        self.rect.x = int(self.x)
        self.hitbox.x = self.rect.x + 5
        
        self.rotation += dt * 180
        self.pulse += dt * 5
        
        self.image.fill((0, 0, 0, 0))
        
        scale = 1.0 + math.sin(self.pulse) * 0.2
        size = int(self.size * scale)
        
        # Resplandor
        for i in range(3):
            alpha = 100 - (i * 30)
            radius = size + (i * 5)
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            color = (*self.color, alpha)
            pygame.draw.circle(surf, color, (radius, radius), radius)
            self.image.blit(surf, (self.size - radius, self.size - radius))
        
        # Cuerpo
        pygame.draw.circle(self.image, self.color, (self.size, self.size), size)
        pygame.draw.circle(self.image, WHITE, (self.size, self.size), size, 3)
        
        # Símbolo
        if self.symbol == 'shield':
            self._draw_shield_symbol(size)
        elif self.symbol == 'clock':
            self._draw_clock_symbol(size)
        elif self.symbol == 'star':
            self._draw_star_symbol(size)
        
        if self.x < -100:
            self.kill()
    
    def _draw_shield_symbol(self, size):
        """Dibuja escudo"""
        cx, cy = self.size, self.size
        shield_size = size - 8
        
        points = [
            (cx, cy - shield_size),
            (cx + shield_size // 2, cy - shield_size // 2),
            (cx + shield_size // 2, cy + shield_size // 3),
            (cx, cy + shield_size),
            (cx - shield_size // 2, cy + shield_size // 3),
            (cx - shield_size // 2, cy - shield_size // 2)
        ]
        
        pygame.draw.polygon(self.image, WHITE, points)
        pygame.draw.polygon(self.image, self.color, points, 3)
    
    def _draw_clock_symbol(self, size):
        """Dibuja reloj"""
        cx, cy = self.size, self.size
        clock_radius = size - 8
        
        pygame.draw.circle(self.image, WHITE, (cx, cy), clock_radius, 3)
        pygame.draw.line(self.image, WHITE, (cx, cy), (cx, cy - clock_radius + 5), 4)
        pygame.draw.line(self.image, WHITE, (cx, cy), (cx + clock_radius // 2, cy), 3)
    
    def _draw_star_symbol(self, size):
        """Dibuja estrella"""
        cx, cy = self.size, self.size
        star_size = size - 5
        
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90 + self.rotation)
            radius = star_size if i % 2 == 0 else star_size // 2
            px = cx + int(radius * math.cos(angle))
            py = cy + int(radius * math.sin(angle))
            points.append((px, py))
        
        pygame.draw.polygon(self.image, WHITE, points)
        pygame.draw.polygon(self.image, self.color, points, 3)
    
    def draw(self, screen):
        """Dibuja power-up"""
        screen.blit(self.image, self.rect)


class ObstacleManager:
    """
    Gestor MEJORADO de obstáculos con sincronización musical perfecta
    """
    
    def __init__(self, audio_analyzer, ground_y):
        self.audio_analyzer = audio_analyzer
        self.ground_y = ground_y
        
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Sistema de pre-spawn basado en beats
        self.upcoming_obstacles = []
        self.spawn_window = 3.0  # Ventana de tiempo para pre-generar (segundos)
        self.last_processed_time = 0
        
        self.base_speed = OBSTACLE_CONFIG['base_speed']
        self.difficulty_mult = 1.0
        
        # Estadísticas
        self.obstacles_spawned = 0
        self.beat_sync_count = 0
        
        # Preparar obstáculos iniciales
        self._prepare_obstacles_ahead(0)
        
        print(f"🎮 Obstacle Manager inicializado")
        print(f"   • Speed base: {self.base_speed}")
        print(f"   • Obstáculos preparados: {len(self.upcoming_obstacles)}")
    
    def _prepare_obstacles_ahead(self, current_time):
        """
        Pre-genera obstáculos basados en los beats de la música
        """
        if not self.audio_analyzer or not self.audio_analyzer.beat_times:
            return
        
        # Rango de tiempo a procesar
        start_time = self.last_processed_time
        end_time = current_time + self.spawn_window
        
        # Obtener beats en este rango
        beats_in_range = [
            b for b in self.audio_analyzer.beat_times 
            if start_time <= b <= end_time
        ]
        
        for beat_time in beats_in_range:
            # Decidir si spawner obstáculo en este beat
            intensity = self.audio_analyzer.get_intensity_at_time(beat_time)
            
            # Probabilidad basada en intensidad
            spawn_chance = 0.3 + (intensity * 0.5)  # 30% - 80%
            
            if random.random() < spawn_chance:
                # Calcular cuándo debe aparecer en pantalla
                # (considerando que los obstáculos se mueven hacia el jugador)
                travel_distance = WIDTH + 100  # Desde fuera de pantalla hasta el jugador
                speed = self.base_speed * (0.8 + intensity * 0.4)
                travel_time = travel_distance / (speed * 60)  # 60 = fps
                
                spawn_time = beat_time - travel_time
                
                # Solo agregar si aún no ha pasado
                if spawn_time > current_time - 0.1:
                    # Tipo de obstáculo basado en intensidad
                    obstacle_type = self._choose_obstacle_type_by_intensity(intensity)
                    
                    # Verificar si es un beat fuerte (para sincronización visual)
                    nearest_beat = self.audio_analyzer.get_nearest_beat(beat_time)
                    is_strong_beat = abs(nearest_beat - beat_time) < 0.05 if nearest_beat else False
                    
                    self.upcoming_obstacles.append({
                        'spawn_time': spawn_time,
                        'type': obstacle_type,
                        'speed': speed,
                        'sync_beat': True,
                        'beat_strength': intensity,
                        'is_strong_beat': is_strong_beat
                    })
        
        self.last_processed_time = end_time
    
    def _choose_obstacle_type_by_intensity(self, intensity):
        """Elige tipo de obstáculo basado en intensidad"""
        if intensity > 0.75:
            # Alta intensidad: más enemigos voladores
            return random.choices(
                ['spike', 'box', 'flying'],
                weights=[1, 1, 4]
            )[0]
        elif intensity > 0.5:
            # Media intensidad: balanceado
            return random.choices(
                ['spike', 'box', 'flying'],
                weights=[2, 2, 2]
            )[0]
        else:
            # Baja intensidad: más sencillos
            return random.choices(
                ['spike', 'box', 'flying'],
                weights=[3, 2, 1]
            )[0]
    
    def update(self, dt, current_time):
        """Actualiza obstáculos y spawn"""
        
        # Preparar más obstáculos si es necesario
        if current_time > self.last_processed_time - 1.0:
            self._prepare_obstacles_ahead(current_time)
        
        # Actualizar dificultad
        if self.audio_analyzer:
            self.difficulty_mult = self.audio_analyzer.get_difficulty_at_time(current_time)
        
        # Detectar beats para efectos
        if self.audio_analyzer and self.audio_analyzer.is_beat(current_time, 0.05):
            self._trigger_beat_effects()
        
        # Spawn de obstáculos programados
        for obstacle_data in self.upcoming_obstacles[:]:
            if current_time >= obstacle_data['spawn_time']:
                self._spawn_obstacle_from_data(obstacle_data)
                self.upcoming_obstacles.remove(obstacle_data)
        
        # Spawn ocasional de power-ups
        if random.random() < 0.005:  # 0.5% por frame
            self._spawn_powerup(self.base_speed * self.difficulty_mult)
        
        # Actualizar todos los obstáculos
        for obstacle in self.obstacles:
            obstacle.update(dt)
        
        for powerup in self.powerups:
            powerup.update(dt)
    
    def _spawn_obstacle_from_data(self, data):
        """Genera obstáculo desde datos pre-calculados"""
        x = WIDTH + 50
        
        obstacle_type = data['type']
        if obstacle_type == 'flying':
            y = self.ground_y - OBSTACLE_TYPES['flying']['fly_height']
        else:
            y = self.ground_y - OBSTACLE_TYPES[obstacle_type]['height']
        
        obstacle = Obstacle(
            x, y,
            obstacle_type,
            data['speed'],
            data['sync_beat'],
            data['beat_strength']
        )
        
        self.obstacles.add(obstacle)
        self.obstacles_spawned += 1
        
        if data['sync_beat']:
            self.beat_sync_count += 1
    
    def _trigger_beat_effects(self):
        """Activa efectos en obstáculos cuando hay beat"""
        for obstacle in self.obstacles:
            if obstacle.sync_beat:
                obstacle.trigger_beat_pulse()
    
    def _spawn_powerup(self, speed):
        """Genera power-up"""
        x = WIDTH + 100
        y = self.ground_y - random.randint(100, 250)
        powerup_type = random.choice(['shield', 'slow', 'invincible'])
        powerup = PowerUp(x, y, powerup_type, speed)
        self.powerups.add(powerup)
    
    def check_collision(self, player_rect):
        """Verifica colisión con obstáculos usando hitbox mejorada"""
        # Hitbox del jugador más pequeña (más generosa)
        player_hitbox = player_rect.inflate(-15, -20)
        
        for obstacle in self.obstacles:
            if player_hitbox.colliderect(obstacle.hitbox):
                return obstacle
        return None
    
    def check_powerup_collision(self, player_rect):
        """Verifica colisión con power-ups"""
        for powerup in self.powerups:
            if player_rect.colliderect(powerup.hitbox):
                powerup_type = powerup.type
                powerup.kill()
                return powerup_type
        return None
    
    def draw(self, screen, debug=False):
        """Dibuja obstáculos"""
        for obstacle in self.obstacles:
            obstacle.draw(screen, debug)
        for powerup in self.powerups:
            powerup.draw(screen)
    
    def clear(self):
        """Limpia todos los obstáculos"""
        self.obstacles.empty()
        self.powerups.empty()
        self.upcoming_obstacles.clear()
        self.last_processed_time = 0