# src/effects/particles.py - Sistema de partículas para efectos visuales

import pygame
import random
import math

class Particle:
    """Partícula individual"""
    
    def __init__(self, x, y, color, velocity, lifetime, size):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x, self.vel_y = velocity
        self.lifetime = lifetime
        self.age = 0
        self.size = size
        self.initial_size = size
    
    def update(self, dt):
        """Actualiza la partícula"""
        self.x += self.vel_x * dt * 60
        self.y += self.vel_y * dt * 60
        self.vel_y += 0.3  # Gravedad
        self.age += dt
        
        # Reducir tamaño con el tiempo
        progress = self.age / self.lifetime
        self.size = self.initial_size * (1 - progress)
        
        return self.age < self.lifetime
    
    def draw(self, screen):
        """Dibuja la partícula"""
        if self.size > 0:
            # Calcular alpha basado en edad
            alpha = int(255 * (1 - self.age / self.lifetime))
            
            surf = pygame.Surface((int(self.size * 2), int(self.size * 2)))
            surf.set_colorkey((0, 0, 0))
            surf.set_alpha(alpha)
            
            pygame.draw.circle(
                surf,
                self.color,
                (int(self.size), int(self.size)),
                int(self.size)
            )
            
            screen.blit(surf, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    """Sistema de gestión de partículas"""
    
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, count, color, spread=360, speed_range=(2, 8), 
             lifetime_range=(0.5, 1.5), size_range=(3, 8)):
        """Emite partículas"""
        for _ in range(count):
            angle = random.uniform(0, spread) * math.pi / 180
            speed = random.uniform(*speed_range)
            
            velocity = (
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )
            
            lifetime = random.uniform(*lifetime_range)
            size = random.randint(*size_range)
            
            # Variación de color
            color_var = tuple(
                max(0, min(255, c + random.randint(-30, 30)))
                for c in color
            )
            
            particle = Particle(x, y, color_var, velocity, lifetime, size)
            self.particles.append(particle)
    
    def emit_explosion(self, x, y, color):
        """Explosión de partículas"""
        self.emit(
            x, y,
            count=20,
            color=color,
            spread=360,
            speed_range=(5, 15),
            lifetime_range=(0.3, 0.8),
            size_range=(4, 10)
        )
    
    def emit_trail(self, x, y, color):
        """Estela de partículas"""
        self.emit(
            x, y,
            count=3,
            color=color,
            spread=180,
            speed_range=(1, 3),
            lifetime_range=(0.3, 0.6),
            size_range=(2, 5)
        )
    
    def emit_sparkle(self, x, y):
        """Destello brillante"""
        colors = [
            (255, 255, 100),
            (255, 200, 100),
            (255, 255, 200)
        ]
        
        for color in colors:
            self.emit(
                x, y,
                count=5,
                color=color,
                spread=360,
                speed_range=(2, 6),
                lifetime_range=(0.4, 0.8),
                size_range=(3, 7)
            )
    
    def emit_powerup_collect(self, x, y):
        """Efecto de recolección de power-up"""
        self.emit(
            x, y,
            count=30,
            color=(255, 255, 0),
            spread=360,
            speed_range=(3, 12),
            lifetime_range=(0.5, 1.2),
            size_range=(4, 8)
        )
    
    def update(self, dt):
        """Actualiza todas las partículas"""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, screen):
        """Dibuja todas las partículas"""
        for particle in self.particles:
            particle.draw(screen)
    
    def clear(self):
        """Limpia todas las partículas"""
        self.particles.clear()

class BeatPulse:
    """Pulso visual para indicar el beat de la música"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = 100
        self.alpha = 255
        self.active = False
    
    def trigger(self):
        """Activa el pulso"""
        self.radius = 0
        self.alpha = 255
        self.active = True
    
    def update(self, dt):
        """Actualiza el pulso"""
        if self.active:
            self.radius += dt * 300
            self.alpha = int(255 * (1 - self.radius / self.max_radius))
            
            if self.radius >= self.max_radius:
                self.active = False
    
    def draw(self, screen):
        """Dibuja el pulso"""
        if self.active and self.alpha > 0:
            surf = pygame.Surface((self.max_radius * 2, self.max_radius * 2))
            surf.set_colorkey((0, 0, 0))
            surf.set_alpha(self.alpha)
            
            pygame.draw.circle(
                surf,
                (100, 200, 255),
                (self.max_radius, self.max_radius),
                int(self.radius),
                3
            )
            
            screen.blit(
                surf,
                (self.x - self.max_radius, self.y - self.max_radius)
            )