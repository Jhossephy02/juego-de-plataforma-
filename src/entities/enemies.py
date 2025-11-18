# src/entities/enemies.py - Sistema completo de enemigos que lanzan proyectiles

import pygame
import math
import random
from src.settings import WIDTH, HEIGHT, RED, PURPLE, GREEN, YELLOW, BLUE

class Projectile(pygame.sprite.Sprite):
    """Proyectil lanzado por enemigos"""
    
    def __init__(self, x, y, direction, speed, projectile_type='fireball'):
        super().__init__()
        
        self.projectile_type = projectile_type
        self.speed = speed
        self.direction = direction  # Vector (x, y) normalizado
        
        # Configuración según tipo
        configs = {
            'fireball': {'size': 16, 'color': (255, 100, 0), 'damage': 1},
            'arrow': {'size': 20, 'color': (150, 150, 150), 'damage': 1},
            'rock': {'size': 18, 'color': (100, 100, 100), 'damage': 1},
            'magic': {'size': 14, 'color': (200, 0, 255), 'damage': 1}
        }
        
        config = configs.get(projectile_type, configs['fireball'])
        self.size = config['size']
        self.color = config['color']
        self.damage = config['damage']
        
        # Crear sprite
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Animación
        self.animation_time = 0
        self.rotation = 0
        
        # Efecto de estela
        self.trail_particles = []
        
        self._update_visual()
    
    def _update_visual(self):
        """Actualiza el aspecto visual del proyectil"""
        self.image.fill((0, 0, 0, 0))
        
        if self.projectile_type == 'fireball':
            self._draw_fireball()
        elif self.projectile_type == 'arrow':
            self._draw_arrow()
        elif self.projectile_type == 'rock':
            self._draw_rock()
        elif self.projectile_type == 'magic':
            self._draw_magic()
    
    def _draw_fireball(self):
        """Dibuja bola de fuego"""
        center = self.size
        
        # Núcleo amarillo
        pygame.draw.circle(self.image, (255, 255, 100), (center, center), self.size // 2)
        
        # Anillo naranja
        pygame.draw.circle(self.image, (255, 150, 0), (center, center), self.size - 2, 3)
        
        # Llamas exteriores
        for i in range(8):
            angle = (self.animation_time * 10 + i * 45) % 360
            rad = math.radians(angle)
            offset = int(math.sin(self.animation_time * 15) * 3)
            fx = center + int((self.size - 3 + offset) * math.cos(rad))
            fy = center + int((self.size - 3 + offset) * math.sin(rad))
            pygame.draw.circle(self.image, (255, 50, 0), (fx, fy), 3)
    
    def _draw_arrow(self):
        """Dibuja flecha"""
        center = self.size
        angle = math.atan2(self.direction[1], self.direction[0])
        
        # Punta de flecha
        tip_x = center + int(self.size * 0.8 * math.cos(angle))
        tip_y = center + int(self.size * 0.8 * math.sin(angle))
        
        # Cola
        tail_x = center - int(self.size * 0.8 * math.cos(angle))
        tail_y = center - int(self.size * 0.8 * math.sin(angle))
        
        # Cuerpo
        pygame.draw.line(self.image, (120, 80, 40), (tail_x, tail_y), (tip_x, tip_y), 4)
        
        # Punta metálica
        pygame.draw.circle(self.image, (180, 180, 180), (tip_x, tip_y), 5)
        pygame.draw.circle(self.image, (220, 220, 220), (tip_x, tip_y), 3)
        
        # Plumas
        perp_angle = angle + math.pi / 2
        feather_x = int(5 * math.cos(perp_angle))
        feather_y = int(5 * math.sin(perp_angle))
        
        pygame.draw.line(self.image, (200, 50, 50), 
                        (tail_x + feather_x, tail_y + feather_y),
                        (tail_x - feather_x, tail_y - feather_y), 3)
    
    def _draw_rock(self):
        """Dibuja roca"""
        center = self.size
        
        # Base gris
        pygame.draw.circle(self.image, (80, 80, 80), (center, center), self.size - 2)
        
        # Textura de piedra (grietas)
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            length = random.randint(5, self.size - 4)
            x1 = center + int((self.size // 2) * math.cos(angle))
            y1 = center + int((self.size // 2) * math.sin(angle))
            x2 = x1 + int(length * math.cos(angle + random.uniform(-0.5, 0.5)))
            y2 = y1 + int(length * math.sin(angle + random.uniform(-0.5, 0.5)))
            pygame.draw.line(self.image, (60, 60, 60), (x1, y1), (x2, y2), 2)
        
        # Highlight
        pygame.draw.circle(self.image, (120, 120, 120), 
                          (center - 3, center - 3), self.size // 3)
    
    def _draw_magic(self):
        """Dibuja proyectil mágico"""
        center = self.size
        
        # Estrella mágica
        points = []
        for i in range(10):
            angle = math.radians(i * 36 + self.rotation)
            radius = self.size if i % 2 == 0 else self.size // 2
            px = center + int(radius * math.cos(angle))
            py = center + int(radius * math.sin(angle))
            points.append((px, py))
        
        # Resplandor
        glow_surf = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 50), 
                          (self.size * 1.5, self.size * 1.5), self.size * 1.5)
        self.image.blit(glow_surf, (-self.size // 2, -self.size // 2))
        
        # Estrella
        pygame.draw.polygon(self.image, self.color, points)
        pygame.draw.polygon(self.image, (255, 255, 255), points, 2)
    
    def update(self, dt):
        """Actualiza el proyectil"""
        self.animation_time += dt
        self.rotation += dt * 360
        
        # Movimiento
        self.rect.x += self.direction[0] * self.speed * dt * 60
        self.rect.y += self.direction[1] * self.speed * dt * 60
        
        # Actualizar visual
        self._update_visual()
        
        # Eliminar si sale de pantalla
        if (self.rect.right < -50 or self.rect.left > WIDTH + 50 or
            self.rect.bottom < -50 or self.rect.top > HEIGHT + 50):
            self.kill()
    
    def draw(self, screen):
        """Dibuja el proyectil"""
        screen.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    """Enemigo base que puede lanzar proyectiles"""
    
    def __init__(self, x, y, enemy_type, speed):
        super().__init__()
        
        self.enemy_type = enemy_type
        self.x = x
        self.y = y
        self.speed = speed
        
        # Configuración según tipo
        self._setup_enemy_config()
        
        # Crear sprite
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Estado
        self.health = self.max_health
        self.shoot_cooldown = 0
        self.animation_time = 0
        self.state = 'idle'  # idle, alert, shooting
        
        # Detección de jugador
        self.player_detected = False
        self.detection_range = 400
        
        self._update_visual()
    
    def _setup_enemy_config(self):
        """Configura propiedades según el tipo"""
        configs = {
            'turret': {
                'width': 50, 'height': 50,
                'color': (100, 100, 100),
                'max_health': 2,
                'shoot_rate': 1.5,  # segundos entre disparos
                'projectile_type': 'fireball',
                'projectile_speed': 8,
                'can_move': False
            },
            'archer': {
                'width': 40, 'height': 60,
                'color': (50, 150, 50),
                'max_health': 1,
                'shoot_rate': 2.0,
                'projectile_type': 'arrow',
                'projectile_speed': 10,
                'can_move': True,
                'move_pattern': 'patrol'
            },
            'mage': {
                'width': 45, 'height': 65,
                'color': (150, 50, 200),
                'max_health': 1,
                'shoot_rate': 1.8,
                'projectile_type': 'magic',
                'projectile_speed': 7,
                'can_move': True,
                'move_pattern': 'float'
            },
            'bomber': {
                'width': 55, 'height': 55,
                'color': (200, 50, 50),
                'max_health': 3,
                'shoot_rate': 2.5,
                'projectile_type': 'rock',
                'projectile_speed': 6,
                'can_move': False,
                'shoots_arc': True
            }
        }
        
        config = configs.get(self.enemy_type, configs['turret'])
        
        self.width = config['width']
        self.height = config['height']
        self.color = config['color']
        self.max_health = config['max_health']
        self.shoot_rate = config['shoot_rate']
        self.projectile_type = config['projectile_type']
        self.projectile_speed = config['projectile_speed']
        self.can_move = config.get('can_move', False)
        self.move_pattern = config.get('move_pattern', None)
        self.shoots_arc = config.get('shoots_arc', False)
    
    def _update_visual(self):
        """Actualiza aspecto visual"""
        self.image.fill((0, 0, 0, 0))
        
        if self.enemy_type == 'turret':
            self._draw_turret()
        elif self.enemy_type == 'archer':
            self._draw_archer()
        elif self.enemy_type == 'mage':
            self._draw_mage()
        elif self.enemy_type == 'bomber':
            self._draw_bomber()
    
    def _draw_turret(self):
        """Dibuja torreta"""
        cx, cy = self.width // 2, self.height // 2
        
        # Base
        pygame.draw.circle(self.image, (80, 80, 80), (cx, cy + 10), 20)
        pygame.draw.circle(self.image, (100, 100, 100), (cx, cy + 10), 18)
        
        # Cuerpo
        pygame.draw.rect(self.image, self.color, (cx - 15, cy - 10, 30, 25), border_radius=5)
        
        # Cañón (apunta hacia donde está el jugador si está alerta)
        cannon_angle = -45 if self.player_detected else 0
        rad = math.radians(cannon_angle)
        cannon_length = 25
        cannon_end_x = cx + int(cannon_length * math.cos(rad))
        cannon_end_y = cy + int(cannon_length * math.sin(rad))
        
        pygame.draw.line(self.image, (60, 60, 60), 
                        (cx, cy), (cannon_end_x, cannon_end_y), 8)
        pygame.draw.line(self.image, (100, 100, 100), 
                        (cx, cy), (cannon_end_x, cannon_end_y), 6)
        
        # Indicador de alerta
        if self.player_detected:
            pygame.draw.circle(self.image, (255, 0, 0), (cx, cy - 20), 5)
    
    def _draw_archer(self):
        """Dibuja arquero"""
        cx, cy = self.width // 2, self.height // 2
        
        # Cuerpo
        pygame.draw.ellipse(self.image, self.color, (cx - 12, cy - 5, 24, 35))
        
        # Cabeza
        pygame.draw.circle(self.image, (255, 220, 180), (cx, cy - 15), 10)
        
        # Ojos
        pygame.draw.circle(self.image, (0, 0, 0), (cx - 4, cy - 17), 2)
        pygame.draw.circle(self.image, (0, 0, 0), (cx + 4, cy - 17), 2)
        
        # Arco
        if self.state == 'shooting':
            # Arco tensado
            pygame.draw.arc(self.image, (100, 50, 0), 
                          (cx + 5, cy - 10, 15, 20), 
                          math.radians(-90), math.radians(90), 3)
            pygame.draw.line(self.image, (200, 200, 200), 
                           (cx + 10, cy - 10), (cx + 10, cy + 10), 2)
        else:
            # Arco relajado
            pygame.draw.arc(self.image, (100, 50, 0), 
                          (cx + 5, cy - 10, 10, 20), 
                          math.radians(-90), math.radians(90), 3)
        
        # Capa
        pygame.draw.polygon(self.image, (40, 120, 40), [
            (cx - 12, cy - 5),
            (cx - 18, cy + 15),
            (cx - 12, cy + 25)
        ])
    
    def _draw_mage(self):
        """Dibuja mago"""
        cx, cy = self.width // 2, self.height // 2
        
        # Túnica
        pygame.draw.polygon(self.image, self.color, [
            (cx, cy - 15),
            (cx - 18, cy + 25),
            (cx + 18, cy + 25)
        ])
        
        # Detalles de túnica
        for i in range(3):
            y = cy + i * 10
            pygame.draw.line(self.image, (200, 100, 255), 
                           (cx - 15 + i * 3, y), (cx + 15 - i * 3, y), 2)
        
        # Cabeza (oculta por capucha)
        pygame.draw.circle(self.image, (100, 50, 100), (cx, cy - 20), 12)
        
        # Ojos brillantes
        glow_color = (255, 100, 255) if self.state == 'shooting' else (150, 50, 150)
        pygame.draw.circle(self.image, glow_color, (cx - 4, cy - 22), 3)
        pygame.draw.circle(self.image, glow_color, (cx + 4, cy - 22), 3)
        
        # Vara mágica
        staff_height = 35
        pygame.draw.line(self.image, (80, 40, 20), 
                        (cx + 15, cy), (cx + 15, cy - staff_height), 4)
        
        # Orbe mágico en la vara
        orb_pulse = 8 + int(math.sin(self.animation_time * 10) * 2)
        pygame.draw.circle(self.image, (200, 100, 255), 
                          (cx + 15, cy - staff_height - 5), orb_pulse)
        pygame.draw.circle(self.image, (255, 200, 255), 
                          (cx + 15, cy - staff_height - 5), orb_pulse - 3)
    
    def _draw_bomber(self):
        """Dibuja bombardero"""
        cx, cy = self.width // 2, self.height // 2
        
        # Cuerpo redondo y grande
        pygame.draw.circle(self.image, self.color, (cx, cy), self.width // 2 - 3)
        pygame.draw.circle(self.image, (255, 100, 100), (cx, cy), self.width // 2 - 3, 3)
        
        # Cara
        pygame.draw.circle(self.image, (0, 0, 0), (cx - 8, cy - 5), 4)
        pygame.draw.circle(self.image, (0, 0, 0), (cx + 8, cy - 5), 4)
        
        # Boca
        if self.state == 'shooting':
            pygame.draw.circle(self.image, (0, 0, 0), (cx, cy + 5), 8)
        else:
            pygame.draw.arc(self.image, (0, 0, 0), 
                          (cx - 8, cy, 16, 12), 
                          0, math.pi, 3)
        
        # Mecha en la cabeza
        fuse_flicker = int(math.sin(self.animation_time * 20) * 3)
        pygame.draw.line(self.image, (100, 50, 0), 
                        (cx, cy - 25), (cx, cy - 25 - 10 + fuse_flicker), 3)
        
        # Chispa
        if self.player_detected:
            spark_x = cx + random.randint(-2, 2)
            spark_y = cy - 35 + fuse_flicker + random.randint(-2, 2)
            pygame.draw.circle(self.image, (255, 200, 0), (spark_x, spark_y), 3)
    
    def detect_player(self, player_x, player_y):
        """Detecta si el jugador está en rango"""
        distance = math.sqrt((player_x - self.rect.centerx)**2 + 
                            (player_y - self.rect.centery)**2)
        
        self.player_detected = distance < self.detection_range
        
        if self.player_detected:
            self.state = 'alert'
        else:
            self.state = 'idle'
        
        return self.player_detected
    
    def shoot(self, target_x, target_y):
        """Dispara un proyectil hacia el objetivo"""
        if self.shoot_cooldown > 0:
            return None
        
        # Calcular dirección
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return None
        
        direction = (dx / distance, dy / distance)
        
        # Disparar en arco si es bombardero
        if self.shoots_arc:
            direction = (direction[0], direction[1] - 0.5)
            # Renormalizar
            length = math.sqrt(direction[0]**2 + direction[1]**2)
            direction = (direction[0] / length, direction[1] / length)
        
        # Crear proyectil
        projectile = Projectile(
            self.rect.centerx,
            self.rect.centery,
            direction,
            self.projectile_speed,
            self.projectile_type
        )
        
        # Reiniciar cooldown
        self.shoot_cooldown = self.shoot_rate
        self.state = 'shooting'
        
        return projectile
    
    def update(self, dt, player_x, player_y):
        """Actualiza el enemigo"""
        self.animation_time += dt
        
        # Actualizar cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        
        # Movimiento
        if self.can_move and self.move_pattern:
            self._update_movement(dt)
        
        # Movimiento base (scroll)
        self.x -= self.speed * dt * 60
        self.rect.x = int(self.x)
        
        # Detectar jugador
        self.detect_player(player_x, player_y)
        
        # Volver a idle después de disparar
        if self.state == 'shooting' and self.shoot_cooldown < self.shoot_rate - 0.3:
            self.state = 'alert' if self.player_detected else 'idle'
        
        # Actualizar visual
        self._update_visual()
        
        # Eliminar si sale de pantalla
        if self.x < -200:
            self.kill()
            return None
        
        # Disparar si está en rango
        if self.player_detected and self.shoot_cooldown <= 0:
            return self.shoot(player_x, player_y)
        
        return None
    
    def _update_movement(self, dt):
        """Actualiza movimiento según patrón"""
        if self.move_pattern == 'float':
            # Movimiento flotante vertical
            self.y += math.sin(self.animation_time * 3) * 2
            self.rect.y = int(self.y)
        
        elif self.move_pattern == 'patrol':
            # Patrulla vertical
            patrol_range = 50
            self.y += math.sin(self.animation_time * 2) * patrol_range * dt
            self.rect.y = int(self.y)
    
    def take_damage(self, damage=1):
        """Recibe daño"""
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False
    
    def draw(self, screen):
        """Dibuja el enemigo"""
        screen.blit(self.image, self.rect)
        
        # Barra de vida si está herido
        if self.health < self.max_health:
            bar_width = self.width
            bar_height = 4
            bar_x = self.rect.x
            bar_y = self.rect.y - 10
            
            # Fondo
            pygame.draw.rect(screen, (100, 0, 0), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Vida actual
            health_width = int(bar_width * (self.health / self.max_health))
            pygame.draw.rect(screen, (0, 255, 0), 
                           (bar_x, bar_y, health_width, bar_height))


class EnemyManager:
    """Gestor de enemigos sincronizado con la música"""
    
    def __init__(self, audio_analyzer, ground_y):
        self.audio_analyzer = audio_analyzer
        self.ground_y = ground_y
        
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        
        self.spawn_timer = 0
        self.next_spawn_time = 2.0
        
        self.difficulty_mult = 1.0
    
    def spawn_enemy(self, enemy_type, x=None, y=None):
        """Genera un enemigo"""
        if x is None:
            x = WIDTH + 50
        
        if y is None:
            # Posición aleatoria en el aire
            y = random.randint(self.ground_y - 300, self.ground_y - 100)
        
        enemy = Enemy(x, y, enemy_type, 3)
        self.enemies.add(enemy)
        
        return enemy
    
    def update(self, dt, current_time, player_x, player_y):
        """Actualiza todos los enemigos"""
        self.spawn_timer += dt
        
        # Ajustar dificultad con la música
        if self.audio_analyzer:
            intensity = self.audio_analyzer.get_intensity_at_time(current_time)
            self.difficulty_mult = 0.8 + (intensity * 0.6)
        
        # Spawneo de enemigos
        if self.spawn_timer >= self.next_spawn_time:
            self._spawn_random_enemy()
            self.spawn_timer = 0
        
        # Actualizar enemigos
        for enemy in self.enemies:
            projectile = enemy.update(dt, player_x, player_y)
            if projectile:
                self.projectiles.add(projectile)
        
        # Actualizar proyectiles
        for projectile in self.projectiles:
            projectile.update(dt)
    
    def _spawn_random_enemy(self):
        """Genera enemigo aleatorio"""
        enemy_types = ['turret', 'archer', 'mage', 'bomber']
        weights = [3, 2, 2, 1]  # Más torretas, menos bombarderos
        
        enemy_type = random.choices(enemy_types, weights=weights)[0]
        
        # Posición según tipo
        if enemy_type == 'turret':
            y = self.ground_y - 60
        else:
            y = random.randint(self.ground_y - 250, self.ground_y - 100)
        
        self.spawn_enemy(enemy_type, y=y)
        
        # Calcular siguiente spawn
        base_time = 3.0 / self.difficulty_mult
        self.next_spawn_time = random.uniform(base_time * 0.8, base_time * 1.2)
    
    def check_collision(self, player_rect):
        """Verifica colisión de proyectiles con jugador"""
        padded_rect = player_rect.inflate(-10, -10)
        
        for projectile in self.projectiles:
            if padded_rect.colliderect(projectile.rect):
                projectile.kill()
                return projectile.damage
        
        return 0
    
    def check_player_attack(self, attack_rect):
        """Verifica si el jugador golpea enemigos"""
        hit_enemies = []
        
        for enemy in self.enemies:
            if attack_rect.colliderect(enemy.rect):
                if enemy.take_damage():
                    hit_enemies.append(enemy)
        
        return hit_enemies
    
    def draw(self, screen):
        """Dibuja todos los enemigos y proyectiles"""
        for enemy in self.enemies:
            enemy.draw(screen)
        
        for projectile in self.projectiles:
            projectile.draw(screen)
    
    def clear(self):
        """Limpia todos los enemigos"""
        self.enemies.empty()
        self.projectiles.empty()