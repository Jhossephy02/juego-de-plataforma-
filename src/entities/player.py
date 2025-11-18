# src/entities/player.py - Jugador con sprites procedurales mejorados

import pygame
import math
from src.settings import (GRAVITY, PLAYER_SPEED, PLAYER_JUMP, PLAYER_DOUBLE_JUMP,
                          RED, WHITE, BLUE, YELLOW, PURPLE)
import os

class Player(pygame.sprite.Sprite):
    """Jugador con gráficos procedurales mejorados"""
    
    def __init__(self, pos):
        super().__init__()
        
        # Dimensiones
        self.width = 50
        self.height = 60
        
        # Crear sprite procedural
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        
        # Física
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.on_ground = False
        self.can_double_jump = True
        
        # Estado
        self.invulnerable = False
        self.invuln_timer = 0
        self.invuln_duration = 1.5
        
        # Power-ups
        self.shield_active = False
        self.shield_timer = 0
        self.shield_duration = 5.0
        
        self.invincible_active = False
        self.invincible_timer = 0
        self.invincible_duration = 5.0
        
        # Animación
        self.flash_timer = 0
        self.animation_time = 0
        self.facing_right = True
        
        # Dibujar sprite inicial
        self._update_sprite()
    
    def _update_sprite(self):
        """Actualiza el sprite del personaje"""
        self.image.fill((0, 0, 0, 0))
        
        # Calcular animación de correr
        bounce = abs(math.sin(self.animation_time * 10)) * 3
        
        # Estado: en el aire o en el suelo
        if not self.on_ground:
            self._draw_jumping()
        else:
            self._draw_running(bounce)
    
    def _draw_running(self, bounce):
        """Dibuja el personaje corriendo"""
        cx, cy = self.width // 2, self.height // 2
        
        # CUERPO - Óvalo principal (azul brillante)
        body_color = (50, 150, 255)
        pygame.draw.ellipse(self.image, body_color, 
                           (cx - 15, cy - 20 + bounce, 30, 40))
        pygame.draw.ellipse(self.image, WHITE, 
                           (cx - 15, cy - 20 + bounce, 30, 40), 2)
        
        # BRAZOS - Líneas gruesas animadas
        arm_angle = math.sin(self.animation_time * 15) * 20
        
        # Brazo izquierdo
        arm_start = (cx - 12, cy + bounce)
        arm_end = (cx - 12 + math.sin(math.radians(arm_angle + 45)) * 15,
                   cy + bounce + math.cos(math.radians(arm_angle + 45)) * 15)
        pygame.draw.line(self.image, body_color, arm_start, arm_end, 6)
        pygame.draw.circle(self.image, body_color, (int(arm_end[0]), int(arm_end[1])), 4)
        
        # Brazo derecho
        arm_start = (cx + 12, cy + bounce)
        arm_end = (cx + 12 + math.sin(math.radians(-arm_angle + 45)) * 15,
                   cy + bounce + math.cos(math.radians(-arm_angle + 45)) * 15)
        pygame.draw.line(self.image, body_color, arm_start, arm_end, 6)
        pygame.draw.circle(self.image, body_color, (int(arm_end[0]), int(arm_end[1])), 4)
        
        # PIERNAS - Animadas
        leg_angle = math.sin(self.animation_time * 15) * 30
        
        # Pierna izquierda
        leg_start = (cx - 6, cy + 15 + bounce)
        leg_end = (cx - 6 + math.sin(math.radians(leg_angle)) * 12,
                   cy + 30 + bounce)
        pygame.draw.line(self.image, body_color, leg_start, leg_end, 7)
        pygame.draw.circle(self.image, body_color, (int(leg_end[0]), int(leg_end[1])), 5)
        
        # Pierna derecha
        leg_start = (cx + 6, cy + 15 + bounce)
        leg_end = (cx + 6 + math.sin(math.radians(-leg_angle)) * 12,
                   cy + 30 + bounce)
        pygame.draw.line(self.image, body_color, leg_start, leg_end, 7)
        pygame.draw.circle(self.image, body_color, (int(leg_end[0]), int(leg_end[1])), 5)
        
        # CABEZA - Círculo con cara
        head_y = cy - 25 + bounce
        pygame.draw.circle(self.image, (255, 220, 180), (cx, int(head_y)), 12)
        pygame.draw.circle(self.image, WHITE, (cx, int(head_y)), 12, 2)
        
        # Ojos
        pygame.draw.circle(self.image, BLACK := (0, 0, 0), (cx - 4, int(head_y - 2)), 2)
        pygame.draw.circle(self.image, BLACK, (cx + 4, int(head_y - 2)), 2)
        
        # Boca sonriente
        mouth_rect = pygame.Rect(cx - 5, int(head_y + 2), 10, 5)
        pygame.draw.arc(self.image, BLACK, mouth_rect, 0, math.pi, 2)
        
        # PELO/GORRO - Triángulo azul
        hair_points = [
            (cx - 10, int(head_y - 12)),
            (cx, int(head_y - 18)),
            (cx + 10, int(head_y - 12))
        ]
        pygame.draw.polygon(self.image, (30, 100, 200), hair_points)
        pygame.draw.polygon(self.image, WHITE, hair_points, 2)
    
    def _draw_jumping(self):
        """Dibuja el personaje saltando"""
        cx, cy = self.width // 2, self.height // 2
        
        body_color = (50, 150, 255)
        
        # CUERPO - Ligeramente inclinado
        pygame.draw.ellipse(self.image, body_color, 
                           (cx - 15, cy - 20, 30, 40))
        pygame.draw.ellipse(self.image, WHITE, 
                           (cx - 15, cy - 20, 30, 40), 2)
        
        # BRAZOS - Extendidos hacia arriba
        # Brazo izquierdo
        arm_start = (cx - 10, cy - 5)
        arm_end = (cx - 18, cy - 25)
        pygame.draw.line(self.image, body_color, arm_start, arm_end, 6)
        pygame.draw.circle(self.image, body_color, arm_end, 4)
        
        # Brazo derecho
        arm_start = (cx + 10, cy - 5)
        arm_end = (cx + 18, cy - 25)
        pygame.draw.line(self.image, body_color, arm_start, arm_end, 6)
        pygame.draw.circle(self.image, body_color, arm_end, 4)
        
        # PIERNAS - Juntas
        leg_start = (cx - 6, cy + 15)
        leg_end = (cx - 6, cy + 30)
        pygame.draw.line(self.image, body_color, leg_start, leg_end, 7)
        pygame.draw.circle(self.image, body_color, leg_end, 5)
        
        leg_start = (cx + 6, cy + 15)
        leg_end = (cx + 6, cy + 30)
        pygame.draw.line(self.image, body_color, leg_start, leg_end, 7)
        pygame.draw.circle(self.image, body_color, leg_end, 5)
        
        # CABEZA
        head_y = cy - 25
        pygame.draw.circle(self.image, (255, 220, 180), (cx, head_y), 12)
        pygame.draw.circle(self.image, WHITE, (cx, head_y), 12, 2)
        
        # Ojos (sorprendidos)
        pygame.draw.circle(self.image, (0, 0, 0), (cx - 4, head_y - 2), 3)
        pygame.draw.circle(self.image, (0, 0, 0), (cx + 4, head_y - 2), 3)
        
        # Boca (O)
        pygame.draw.circle(self.image, (0, 0, 0), (cx, head_y + 4), 3, 1)
        
        # PELO
        hair_points = [
            (cx - 10, head_y - 12),
            (cx, head_y - 20),
            (cx + 10, head_y - 12)
        ]
        pygame.draw.polygon(self.image, (30, 100, 200), hair_points)
        pygame.draw.polygon(self.image, WHITE, hair_points, 2)
    
    def update(self, keys, ground_y, dt):
        """Actualiza el jugador"""
        self.animation_time += dt
        
        # Salto y doble salto
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.on_ground:
                self.vel.y = PLAYER_JUMP
                self.on_ground = False
                self.can_double_jump = True
            elif self.can_double_jump:
                self.vel.y = PLAYER_DOUBLE_JUMP
                self.can_double_jump = False
        
        # Gravedad
        self.vel.y += GRAVITY
        
        # Aplicar velocidad
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        
        # Colisión con suelo
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel.y = 0
            self.on_ground = True
            self.can_double_jump = True
        
        # Mantener en pantalla
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 1280:
            self.rect.right = 1280
        
        # Actualizar invulnerabilidad
        if self.invulnerable:
            self.invuln_timer += dt
            if self.invuln_timer >= self.invuln_duration:
                self.invulnerable = False
                self.invuln_timer = 0
            
            self.flash_timer += 0.1
        
        # Actualizar power-ups
        if self.shield_active:
            self.shield_timer += dt
            if self.shield_timer >= self.shield_duration:
                self.shield_active = False
                self.shield_timer = 0
        
        if self.invincible_active:
            self.invincible_timer += dt
            if self.invincible_timer >= self.invincible_duration:
                self.invincible_active = False
                self.invincible_timer = 0
        
        # Actualizar sprite
        self._update_sprite()
    
    def take_damage(self):
        """Recibe daño y activa invulnerabilidad"""
        if self.invulnerable or self.invincible_active:
            return False
        
        self.invulnerable = True
        self.invuln_timer = 0
        
        # Pequeño impulso hacia arriba
        if self.on_ground:
            self.vel.y = PLAYER_JUMP * 0.5
        
        return True
    
    def activate_powerup(self, powerup_type):
        """Activa un power-up"""
        if powerup_type == 'shield':
            self.shield_active = True
            self.shield_timer = 0
        elif powerup_type == 'invincible':
            self.invincible_active = True
            self.invincible_timer = 0
        elif powerup_type == 'slow':
            pass  # Manejado por el juego
    
    def draw(self, screen):
        """Dibuja el jugador con efectos"""
        # Efecto de parpadeo si es invulnerable
        if self.invulnerable and int(self.flash_timer * 10) % 2 == 0:
            temp_image = self.image.copy()
            temp_image.set_alpha(128)
            screen.blit(temp_image, self.rect)
        else:
            screen.blit(self.image, self.rect)
        
        # Efecto de escudo
        if self.shield_active:
            shield_radius = 40
            shield_surf = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            
            # Pulso animado
            pulse = abs(math.sin(pygame.time.get_ticks() / 200)) * 0.3 + 0.7
            alpha = int(120 * pulse)
            
            # Círculo de escudo con efecto hexagonal
            for i in range(6):
                angle = (pygame.time.get_ticks() / 20 + i * 60) % 360
                x1 = shield_radius + int(shield_radius * math.cos(math.radians(angle)))
                y1 = shield_radius + int(shield_radius * math.sin(math.radians(angle)))
                x2 = shield_radius + int(shield_radius * math.cos(math.radians(angle + 60)))
                y2 = shield_radius + int(shield_radius * math.sin(math.radians(angle + 60)))
                pygame.draw.line(shield_surf, (100, 200, 255, alpha), (x1, y1), (x2, y2), 3)
            
            screen.blit(shield_surf, 
                       (self.rect.centerx - shield_radius, 
                        self.rect.centery - shield_radius))
        
        # Efecto de invencibilidad
        if self.invincible_active:
            for i in range(3):
                star_size = 8
                angle = (pygame.time.get_ticks() / 10 + i * 120) % 360
                distance = 35
                x = int(self.rect.centerx + distance * math.cos(math.radians(angle)))
                y = int(self.rect.centery + distance * math.sin(math.radians(angle)))
                
                # Estrella de 5 puntas
                self._draw_star(screen, x, y, star_size, YELLOW)
    
    def _draw_star(self, screen, x, y, size, color):
        """Dibuja una estrella de 5 puntas"""
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            radius = size if i % 2 == 0 else size // 2
            px = x + int(radius * math.cos(angle))
            py = y + int(radius * math.sin(angle))
            points.append((px, py))
        
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, WHITE, points, 1)