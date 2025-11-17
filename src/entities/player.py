# src/entities/player.py - Jugador con doble salto y mejoras

import pygame
from src.settings import (GRAVITY, PLAYER_SPEED, PLAYER_JUMP, PLAYER_DOUBLE_JUMP,
                          PLAYER_DIR, RED, WHITE)
import os

class Player(pygame.sprite.Sprite):
    """Jugador con mecánicas mejoradas"""
    
    def __init__(self, pos):
        super().__init__()
        
        # Cargar sprite
        try:
            sprite_path = os.path.join(PLAYER_DIR, 'idle', 'Idle.png')
            self.image = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
        except:
            # Sprite por defecto si no existe
            self.image = pygame.Surface((50, 50))
            self.image.fill(RED)
            print("⚠️ Sprite del jugador no encontrado, usando placeholder")
        
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
        
        # Animación
        self.flash_timer = 0
    
    def update(self, keys, ground_y):
        """Actualiza el jugador"""
        # Movimiento horizontal (opcional, deshabilitado por ahora)
        # self.vel.x = 0
        # if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        #     self.vel.x = -self.speed
        # if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        #     self.vel.x = self.speed
        
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
        if self.rect.right > 1280:  # WIDTH
            self.rect.right = 1280
        
        # Actualizar invulnerabilidad
        if self.invulnerable:
            self.invuln_timer += 1/60  # Aproximado
            if self.invuln_timer >= self.invuln_duration:
                self.invulnerable = False
                self.invuln_timer = 0
            
            self.flash_timer += 0.1
    
    def take_damage(self):
        """Recibe daño y activa invulnerabilidad"""
        self.invulnerable = True
        self.invuln_timer = 0
        
        # Pequeño impulso hacia arriba
        if self.on_ground:
            self.vel.y = PLAYER_JUMP * 0.5
    
    def draw(self, screen):
        """Dibuja el jugador con efecto de parpadeo si es invulnerable"""
        if self.invulnerable:
            # Parpadeo
            if int(self.flash_timer * 10) % 2 == 0:
                # Crear copia semi-transparente
                temp_image = self.image.copy()
                temp_image.set_alpha(128)
                screen.blit(temp_image, self.rect)
            else:
                screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image, self.rect)