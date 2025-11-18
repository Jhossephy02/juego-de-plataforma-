# src/entities/obstacle_manager.py - Sistema completo con imports corregidos

import pygame  # ← IMPORTANTE: Este import faltaba
import random
import math
from src.settings import (WIDTH, HEIGHT, OBSTACLE_CONFIG, OBSTACLE_TYPES, 
                          RED, PURPLE, YELLOW, GREEN, BLUE, WHITE)

class Obstacle(pygame.sprite.Sprite):
    """Obstáculo con gráficos mejorados"""
    
    def __init__(self, x, y, obstacle_type, speed, sync_beat=False):
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
        
        # Efectos visuales
        self.sync_beat = sync_beat
        self.pulse_time = 0
        self.glow_intensity = 0
        self.animation_time = 0
        
        # Para obstáculos voladores
        if obstacle_type == 'flying':
            self.fly_height = config['fly_height']
            self.fly_time = random.uniform(0, math.pi * 2)
            self.fly_speed = random.uniform(2, 4)
        
        # Crear superficie
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        self.update_visual()
    
    def update_visual(self):
        """Actualiza el aspecto visual del obstáculo"""
        self.image.fill((0, 0, 0, 0))
        
        # Efecto de pulso si está sincronizado con beat
        scale = 1.0
        if self.sync_beat and self.pulse_time > 0:
            scale = 1.0 + (self.pulse_time * 0.3)
            self.pulse_time -= 0.05
        
        # Calcular tamaño con escala
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
            glow_color = (*self.color, int(self.glow_intensity * 100))
            pygame.draw.rect(glow_surf, glow_color, (10, 10, w, h), border_radius=5)
            self.image.blit(glow_surf, (-10, -10))
            self.glow_intensity -= 0.05
    
    def _draw_spike_improved(self, w, h):
        """Dibuja espiga mejorada con efecto 3D"""
        points = [
            (w // 2, 5),
            (w - 5, h - 5),
            (5, h - 5)
        ]
        
        shadow_points = [(p[0] + 2, p[1] + 2) for p in points]
        pygame.draw.polygon(self.image, (100, 0, 0), shadow_points)
        pygame.draw.polygon(self.image, self.color, points)
        
        highlight_points = [
            (w // 2, 8),
            (w // 2 + 5, h // 2),
            (w // 2, h // 2)
        ]
        pygame.draw.polygon(self.image, (255, 150, 150), highlight_points)
        pygame.draw.polygon(self.image, (200, 0, 0), points, 3)
        
        for i in range(3):
            start_x = 10 + i * (w - 20) // 3
            pygame.draw.line(self.image, (150, 0, 0), 
                           (start_x, h - 8), (w // 2, 10), 2)
    
    def _draw_box_improved(self, w, h):
        """Dibuja caja mejorada estilo 3D"""
        main_rect = (5, 5, w - 10, h - 10)
        shadow_rect = (7, 7, w - 10, h - 10)
        pygame.draw.rect(self.image, (80, 40, 10), shadow_rect, border_radius=5)
        pygame.draw.rect(self.image, self.color, main_rect, border_radius=5)
        
        top_points = [(5, 5), (w - 5, 5), (w - 8, 8), (8, 8)]
        pygame.draw.polygon(self.image, (180, 120, 60), top_points)
        
        right_points = [(w - 5, 5), (w - 5, h - 5), (w - 8, h - 8), (w - 8, 8)]
        pygame.draw.polygon(self.image, (100, 60, 20), right_points)
        
        plank_y = 15
        while plank_y < h - 15:
            pygame.draw.line(self.image, (100, 50, 20), 
                           (10, plank_y), (w - 10, plank_y), 2)
            plank_y += 15
        
        for nail_x in [12, w - 12]:
            for nail_y in [12, h // 2, h - 12]:
                pygame.draw.circle(self.image, (60, 60, 60), (nail_x, nail_y), 3)
                pygame.draw.circle(self.image, (100, 100, 100), (nail_x, nail_y), 2)
        
        pygame.draw.rect(self.image, (100, 50, 20), main_rect, 3, border_radius=5)
    
    def _draw_flying_improved(self, w, h):
        """Dibuja enemigo volador mejorado - estilo fantasma/nube"""
        center = (w // 2, h // 2)
        float_offset = int(math.sin(self.animation_time * 3) * 3)
        
        pygame.draw.circle(self.image, self.color, 
                          (center[0], center[1] + float_offset), 
                          min(w, h) // 2 - 3)
        pygame.draw.circle(self.image, self.color, 
                          (center[0] - 8, center[1] + float_offset - 5), 
                          min(w, h) // 3)
        pygame.draw.circle(self.image, self.color, 
                          (center[0] + 8, center[1] + float_offset - 5), 
                          min(w, h) // 3)
        
        wave_points = []
        for i in range(8):
            x = 5 + (w - 10) * i / 7
            y = center[1] + float_offset + 12 + math.sin(i + self.animation_time * 5) * 3
            wave_points.append((int(x), int(y)))
        
        wave_points.append((w - 5, center[1] + float_offset))
        wave_points.append((5, center[1] + float_offset))
        pygame.draw.polygon(self.image, self.color, wave_points)
        
        eye_y = center[1] + float_offset - 5
        pygame.draw.ellipse(self.image, WHITE, (center[0] - 12, eye_y - 5, 8, 10))
        pygame.draw.circle(self.image, (0, 0, 0), (center[0] - 8, eye_y), 3)
        pygame.draw.ellipse(self.image, WHITE, (center[0] + 4, eye_y - 5, 8, 10))
        pygame.draw.circle(self.image, (0, 0, 0), (center[0] + 8, eye_y), 3)
        
        pygame.draw.line(self.image, (0, 0, 0), 
                        (center[0] - 15, eye_y - 8), 
                        (center[0] - 5, eye_y - 6), 3)
        pygame.draw.line(self.image, (0, 0, 0), 
                        (center[0] + 5, eye_y - 6), 
                        (center[0] + 15, eye_y - 8), 3)
        
        mouth_y = center[1] + float_offset + 5
        mouth_points = [
            (center[0] - 10, mouth_y),
            (center[0] - 5, mouth_y + 5),
            (center[0], mouth_y),
            (center[0] + 5, mouth_y + 5),
            (center[0] + 10, mouth_y)
        ]
        pygame.draw.lines(self.image, (0, 0, 0), False, mouth_points, 3)
        pygame.draw.circle(self.image, WHITE, 
                          (center[0], center[1] + float_offset), 
                          min(w, h) // 2 - 3, 2)
        
        glow_radius = min(w, h) // 2 + 5
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_color = (*self.color, 50)
        pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
        self.image.blit(glow_surf, 
                       (center[0] - glow_radius, center[1] + float_offset - glow_radius))
    
    def trigger_beat_pulse(self):
        """Activa efecto visual de beat"""
        self.pulse_time = 1.0
        self.glow_intensity = 1.0
    
    def update(self, dt):
        """Actualiza el obstáculo"""
        self.animation_time += dt
        self.x -= self.speed * dt * 60
        self.rect.x = int(self.x)
        
        if self.type == 'flying':
            self.fly_time += dt * self.fly_speed
            offset_y = math.sin(self.fly_time) * 30
            self.rect.y = int(self.y + offset_y)
        else:
            self.rect.y = int(self.y)
        
        self.update_visual()
        
        if self.x < -200:
            self.kill()
    
    def draw(self, screen):
        """Dibuja el obstáculo"""
        screen.blit(self.image, self.rect)
    
    def get_score(self):
        """Retorna puntuación al esquivar"""
        bonus = 10 if self.sync_beat else 0
        return self.score + bonus


class PowerUp(pygame.sprite.Sprite):
    """Power-up mejorado con gráficos procedurales"""
    
    def __init__(self, x, y, powerup_type, speed):
        super().__init__()
        
        self.type = powerup_type
        self.x = x
        self.y = y
        self.speed = speed
        
        self.size = 35
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
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
        """Actualiza el power-up"""
        self.x -= self.speed * dt * 60
        self.rect.x = int(self.x)
        
        self.rotation += dt * 180
        self.pulse += dt * 5
        
        self.image.fill((0, 0, 0, 0))
        
        scale = 1.0 + math.sin(self.pulse) * 0.2
        size = int(self.size * scale)
        
        for i in range(3):
            alpha = 100 - (i * 30)
            radius = size + (i * 5)
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            color = (*self.color, alpha)
            pygame.draw.circle(surf, color, (radius, radius), radius)
            self.image.blit(surf, (self.size - radius, self.size - radius))
        
        pygame.draw.circle(self.image, self.color, (self.size, self.size), size)
        pygame.draw.circle(self.image, WHITE, (self.size, self.size), size, 3)
        
        if self.symbol == 'shield':
            self._draw_shield_symbol(size)
        elif self.symbol == 'clock':
            self._draw_clock_symbol(size)
        elif self.symbol == 'star':
            self._draw_star_symbol(size)
        
        if self.x < -100:
            self.kill()
    
    def _draw_shield_symbol(self, size):
        """Dibuja símbolo de escudo"""
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
        """Dibuja símbolo de reloj"""
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
        """Dibuja el power-up"""
        screen.blit(self.image, self.rect)


class ObstacleManager:
    """Gestor mejorado de obstáculos sincronizados con música"""
    
    def __init__(self, audio_analyzer, ground_y):
        self.audio_analyzer = audio_analyzer
        self.ground_y = ground_y
        
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        self.spawn_timer = 0
        self.next_spawn_time = 0
        self.last_beat_time = 0
        
        self.base_speed = OBSTACLE_CONFIG['base_speed']
        self.difficulty_mult = 1.0
        
        self.obstacles_spawned = 0
        self.beat_sync_count = 0
    
    def update(self, dt, current_time):
        """Actualiza todos los obstáculos"""
        self.spawn_timer += dt
        
        if self.audio_analyzer:
            intensity = self.audio_analyzer.get_intensity_at_time(current_time)
            self.difficulty_mult = 0.8 + (intensity * 0.6)
            
            if self.audio_analyzer.is_beat(current_time, 0.05):
                if current_time - self.last_beat_time > 0.1:
                    self._trigger_beat_effects()
                    self.last_beat_time = current_time
        
        if self.spawn_timer >= self.next_spawn_time:
            self._spawn_obstacle(current_time)
            self.spawn_timer = 0
        
        for obstacle in self.obstacles:
            obstacle.update(dt)
        
        for powerup in self.powerups:
            powerup.update(dt)
    
    def _trigger_beat_effects(self):
        """Activa efectos en obstáculos existentes cuando hay beat"""
        for obstacle in self.obstacles:
            if obstacle.sync_beat:
                obstacle.trigger_beat_pulse()
    
    def _spawn_obstacle(self, current_time):
        """Genera un nuevo obstáculo"""
        speed = self.base_speed * self.difficulty_mult
        
        sync_beat = False
        if self.audio_analyzer:
            next_beat = self.audio_analyzer.get_next_beat_time(current_time)
            if next_beat and abs(next_beat - current_time) < 0.5:
                sync_beat = random.random() < 0.7
                if sync_beat:
                    self.beat_sync_count += 1
        
        obstacle_type = self._choose_obstacle_type(current_time)
        x = WIDTH + 50
        
        if obstacle_type == 'flying':
            y = self.ground_y - OBSTACLE_TYPES['flying']['fly_height']
        else:
            y = self.ground_y - OBSTACLE_TYPES[obstacle_type]['height']
        
        obstacle = Obstacle(x, y, obstacle_type, speed, sync_beat)
        self.obstacles.add(obstacle)
        self.obstacles_spawned += 1
        
        if random.random() < 0.15:
            self._spawn_powerup(speed)
        
        self._calculate_next_spawn(current_time)
    
    def _choose_obstacle_type(self, current_time):
        """Elige tipo de obstáculo basado en la música"""
        if not self.audio_analyzer:
            return random.choice(list(OBSTACLE_TYPES.keys()))
        
        intensity = self.audio_analyzer.get_intensity_at_time(current_time)
        
        if intensity > 0.7:
            return random.choices(['spike', 'box', 'flying'], weights=[1, 1, 3])[0]
        elif intensity > 0.4:
            return random.choices(['spike', 'box', 'flying'], weights=[2, 2, 1])[0]
        else:
            return random.choices(['spike', 'box', 'flying'], weights=[3, 2, 1])[0]
    
    def _spawn_powerup(self, speed):
        """Genera un power-up"""
        x = WIDTH + 100
        y = self.ground_y - random.randint(100, 250)
        powerup_type = random.choice(['shield', 'slow', 'invincible'])
        powerup = PowerUp(x, y, powerup_type, speed)
        self.powerups.add(powerup)
    
    def _calculate_next_spawn(self, current_time):
        """Calcula el tiempo hasta el próximo obstáculo"""
        if self.audio_analyzer:
            avg_interval = self.audio_analyzer.avg_beat_interval
            intensity = self.audio_analyzer.get_intensity_at_time(current_time)
            min_time = avg_interval * 0.5 * (1.2 - intensity * 0.5)
            max_time = avg_interval * 1.2 * (1.5 - intensity * 0.5)
            self.next_spawn_time = random.uniform(min_time, max_time)
        else:
            self.next_spawn_time = random.uniform(1.0, 2.5)
        
        self.next_spawn_time = max(0.3, min(3.0, self.next_spawn_time))
    
    def check_collision(self, player_rect):
        """Verifica colisión con obstáculos"""
        padded_rect = player_rect.inflate(-10, -10)
        for obstacle in self.obstacles:
            if padded_rect.colliderect(obstacle.rect):
                return obstacle
        return None
    
    def check_powerup_collision(self, player_rect):
        """Verifica colisión con power-ups"""
        for powerup in self.powerups:
            if player_rect.colliderect(powerup.rect):
                powerup_type = powerup.type
                powerup.kill()
                return powerup_type
        return None
    
    def draw(self, screen):
        """Dibuja todos los obstáculos y power-ups"""
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        for powerup in self.powerups:
            powerup.draw(screen)
    
    def clear(self):
        """Limpia todos los obstáculos"""
        self.obstacles.empty()
        self.powerups.empty()