# src/entities/obstacle_manager.py - Sistema mejorado de obstáculos sincronizados

import pygame
import random
import math
from src.settings import (WIDTH, HEIGHT, OBSTACLE_CONFIG, OBSTACLE_TYPES, 
                          RED, PURPLE, YELLOW, GREEN, BLUE)

class Obstacle(pygame.sprite.Sprite):
    """Obstáculo individual con mejoras visuales"""
    
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
            self._draw_spike(w, h)
        elif self.type == 'box':
            self._draw_box(w, h)
        elif self.type == 'flying':
            self._draw_flying(w, h)
        
        # Resplandor si está sincronizado
        if self.sync_beat and self.glow_intensity > 0:
            glow_surf = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
            glow_color = (*self.color, int(self.glow_intensity * 100))
            pygame.draw.rect(glow_surf, glow_color, (10, 10, w, h), border_radius=5)
            self.image.blit(glow_surf, (-10, -10))
            self.glow_intensity -= 0.05
    
    def _draw_spike(self, w, h):
        """Dibuja espiga"""
        # Triángulo puntiagudo
        points = [
            (w // 2, 5),  # Punta
            (w - 5, h - 5),  # Base derecha
            (5, h - 5)  # Base izquierda
        ]
        pygame.draw.polygon(self.image, self.color, points)
        pygame.draw.polygon(self.image, (255, 100, 100), points, 3)
    
    def _draw_box(self, w, h):
        """Dibuja caja"""
        # Caja con textura
        pygame.draw.rect(self.image, self.color, (5, 5, w - 10, h - 10), border_radius=5)
        pygame.draw.rect(self.image, (180, 90, 30), (5, 5, w - 10, h - 10), 3, border_radius=5)
        
        # Detalles de madera
        pygame.draw.line(self.image, (100, 50, 20), (10, h // 2), (w - 10, h // 2), 2)
        pygame.draw.line(self.image, (100, 50, 20), (w // 2, 10), (w // 2, h - 10), 2)
    
    def _draw_flying(self, w, h):
        """Dibuja enemigo volador"""
        # Círculo con alas
        center = (w // 2, h // 2)
        pygame.draw.circle(self.image, self.color, center, min(w, h) // 2 - 5)
        pygame.draw.circle(self.image, (255, 255, 255), center, min(w, h) // 2 - 5, 3)
        
        # Ojos
        eye_offset = w // 6
        pygame.draw.circle(self.image, (255, 255, 255), (center[0] - eye_offset, center[1] - 5), 5)
        pygame.draw.circle(self.image, (255, 255, 255), (center[0] + eye_offset, center[1] - 5), 5)
        pygame.draw.circle(self.image, (0, 0, 0), (center[0] - eye_offset, center[1] - 5), 3)
        pygame.draw.circle(self.image, (0, 0, 0), (center[0] + eye_offset, center[1] - 5), 3)
    
    def trigger_beat_pulse(self):
        """Activa efecto visual de beat"""
        self.pulse_time = 1.0
        self.glow_intensity = 1.0
    
    def update(self, dt):
        """Actualiza el obstáculo"""
        # Mover
        self.x -= self.speed * dt * 60
        self.rect.x = int(self.x)
        
        # Movimiento vertical para voladores
        if self.type == 'flying':
            self.fly_time += dt * self.fly_speed
            offset_y = math.sin(self.fly_time) * 30
            self.rect.y = int(self.y + offset_y)
        else:
            self.rect.y = int(self.y)
        
        # Actualizar visual
        self.update_visual()
        
        # Eliminar si sale de pantalla
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
    """Power-up coleccionable"""
    
    def __init__(self, x, y, powerup_type, speed):
        super().__init__()
        
        self.type = powerup_type
        self.x = x
        self.y = y
        self.speed = speed
        
        # Visual
        self.size = 35
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Animación
        self.rotation = 0
        self.pulse = 0
        
        # Color según tipo
        if powerup_type == 'shield':
            self.color = (100, 200, 255)
            self.icon = '🛡️'
        elif powerup_type == 'slow':
            self.color = (255, 200, 100)
            self.icon = '⏱️'
        elif powerup_type == 'invincible':
            self.color = (255, 100, 255)
            self.icon = '⭐'
    
    def update(self, dt):
        """Actualiza el power-up"""
        # Mover
        self.x -= self.speed * dt * 60
        self.rect.x = int(self.x)
        
        # Animación
        self.rotation += dt * 180
        self.pulse += dt * 5
        
        # Actualizar visual
        self.image.fill((0, 0, 0, 0))
        
        # Pulso
        scale = 1.0 + math.sin(self.pulse) * 0.2
        size = int(self.size * scale)
        
        # Círculo brillante
        for i in range(3):
            alpha = 100 - (i * 30)
            radius = size + (i * 5)
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            color = (*self.color, alpha)
            pygame.draw.circle(surf, color, (radius, radius), radius)
            self.image.blit(surf, (self.size - radius, self.size - radius))
        
        # Centro sólido
        pygame.draw.circle(self.image, self.color, (self.size, self.size), size)
        pygame.draw.circle(self.image, (255, 255, 255), (self.size, self.size), size, 3)
        
        # Eliminar si sale de pantalla
        if self.x < -100:
            self.kill()
    
    def draw(self, screen):
        """Dibuja el power-up"""
        screen.blit(self.image, self.rect)

class ObstacleManager:
    """Gestor mejorado de obstáculos sincronizados con música"""
    
    def __init__(self, audio_analyzer, ground_y):
        self.audio_analyzer = audio_analyzer
        self.ground_y = ground_y
        
        # Grupos de sprites
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Control de generación
        self.spawn_timer = 0
        self.next_spawn_time = 0
        self.last_beat_time = 0
        
        # Dificultad dinámica
        self.base_speed = OBSTACLE_CONFIG['base_speed']
        self.difficulty_mult = 1.0
        
        # Estadísticas
        self.obstacles_spawned = 0
        self.beat_sync_count = 0
    
    def update(self, dt, current_time):
        """Actualiza todos los obstáculos"""
        self.spawn_timer += dt
        
        # Actualizar dificultad basada en la música
        if self.audio_analyzer:
            intensity = self.audio_analyzer.get_intensity_at_time(current_time)
            self.difficulty_mult = 0.8 + (intensity * 0.6)
            
            # Detectar beats para efectos visuales
            if self.audio_analyzer.is_beat(current_time, 0.05):
                if current_time - self.last_beat_time > 0.1:
                    self._trigger_beat_effects()
                    self.last_beat_time = current_time
        
        # Generar obstáculos
        if self.spawn_timer >= self.next_spawn_time:
            self._spawn_obstacle(current_time)
            self.spawn_timer = 0
        
        # Actualizar sprites
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
        # Calcular velocidad
        speed = self.base_speed * self.difficulty_mult
        
        # Decidir si sincronizar con beat
        sync_beat = False
        if self.audio_analyzer:
            # 70% de chance si hay beat cercano
            next_beat = self.audio_analyzer.get_next_beat_time(current_time)
            if next_beat and abs(next_beat - current_time) < 0.5:
                sync_beat = random.random() < 0.7
                if sync_beat:
                    self.beat_sync_count += 1
        
        # Seleccionar tipo de obstáculo basado en intensidad
        obstacle_type = self._choose_obstacle_type(current_time)
        
        # Calcular posición
        x = WIDTH + 50
        
        if obstacle_type == 'flying':
            y = self.ground_y - OBSTACLE_TYPES['flying']['fly_height']
        else:
            y = self.ground_y - OBSTACLE_TYPES[obstacle_type]['height']
        
        # Crear obstáculo
        obstacle = Obstacle(x, y, obstacle_type, speed, sync_beat)
        self.obstacles.add(obstacle)
        self.obstacles_spawned += 1
        
        # Ocasionalmente generar power-up
        if random.random() < 0.15:  # 15% chance
            self._spawn_powerup(speed)
        
        # Calcular siguiente tiempo de spawn
        self._calculate_next_spawn(current_time)
    
    def _choose_obstacle_type(self, current_time):
        """Elige tipo de obstáculo basado en la música"""
        if not self.audio_analyzer:
            return random.choice(list(OBSTACLE_TYPES.keys()))
        
        intensity = self.audio_analyzer.get_intensity_at_time(current_time)
        
        # Más intensidad = más obstáculos difíciles
        if intensity > 0.7:
            # Alta intensidad: más enemigos voladores
            return random.choices(
                ['spike', 'box', 'flying'],
                weights=[1, 1, 3]
            )[0]
        elif intensity > 0.4:
            # Intensidad media: variedad
            return random.choices(
                ['spike', 'box', 'flying'],
                weights=[2, 2, 1]
            )[0]
        else:
            # Baja intensidad: más simple
            return random.choices(
                ['spike', 'box', 'flying'],
                weights=[3, 2, 1]
            )[0]
    
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
            # Usar tempo de la música
            avg_interval = self.audio_analyzer.avg_beat_interval
            
            # Variar según intensidad
            intensity = self.audio_analyzer.get_intensity_at_time(current_time)
            
            # Más intensidad = obstáculos más frecuentes
            min_time = avg_interval * 0.5 * (1.2 - intensity * 0.5)
            max_time = avg_interval * 1.2 * (1.5 - intensity * 0.5)
            
            self.next_spawn_time = random.uniform(min_time, max_time)
        else:
            # Generación aleatoria sin música
            self.next_spawn_time = random.uniform(1.0, 2.5)
        
        # Limitar para evitar spawns muy rápidos o lentos
        self.next_spawn_time = max(0.3, min(3.0, self.next_spawn_time))
    
    def check_collision(self, player_rect):
        """Verifica colisión con obstáculos"""
        # Hacer hitbox del jugador un poco más pequeña para mejor gameplay
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