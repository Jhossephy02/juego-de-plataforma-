# src/effects/particles.py - Sistema de partículas mejorado

import pygame
import random
import math

class Particle:
    """Partícula individual mejorada"""
    
    def __init__(self, x, y, color, velocity, lifetime, size, particle_type='circle'):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x, self.vel_y = velocity
        self.lifetime = lifetime
        self.age = 0
        self.size = size
        self.initial_size = size
        self.particle_type = particle_type
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
    
    def update(self, dt):
        """Actualiza la partícula"""
        self.x += self.vel_x * dt * 60
        self.y += self.vel_y * dt * 60
        self.vel_y += 0.3  # Gravedad
        self.vel_x *= 0.98  # Fricción del aire
        self.age += dt
        self.rotation += self.rotation_speed
        
        # Reducir tamaño con el tiempo
        progress = self.age / self.lifetime
        self.size = self.initial_size * (1 - progress)
        
        return self.age < self.lifetime
    
    def draw(self, screen):
        """Dibuja la partícula con diferentes formas"""
        if self.size <= 0:
            return
        
        # Calcular alpha basado en edad
        alpha = int(255 * (1 - self.age / self.lifetime))
        
        if self.particle_type == 'circle':
            self._draw_circle(screen, alpha)
        elif self.particle_type == 'square':
            self._draw_square(screen, alpha)
        elif self.particle_type == 'star':
            self._draw_star(screen, alpha)
        elif self.particle_type == 'spark':
            self._draw_spark(screen, alpha)
    
    def _draw_circle(self, screen, alpha):
        """Dibuja partícula circular"""
        surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(
            surf,
            (*self.color, alpha),
            (int(self.size), int(self.size)),
            int(self.size)
        )
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))
    
    def _draw_square(self, screen, alpha):
        """Dibuja partícula cuadrada"""
        surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        
        # Rotar el cuadrado
        square_surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.rect(
            square_surf,
            (*self.color, alpha),
            (0, 0, int(self.size * 2), int(self.size * 2))
        )
        
        rotated = pygame.transform.rotate(square_surf, self.rotation)
        rect = rotated.get_rect(center=(int(self.size), int(self.size)))
        surf.blit(rotated, rect)
        
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))
    
    def _draw_star(self, screen, alpha):
        """Dibuja partícula en forma de estrella"""
        points = []
        for i in range(10):
            angle = math.radians(i * 36 + self.rotation)
            radius = self.size if i % 2 == 0 else self.size / 2
            px = self.x + radius * math.cos(angle)
            py = self.y + radius * math.sin(angle)
            points.append((int(px), int(py)))
        
        surf = pygame.Surface((int(self.size * 3), int(self.size * 3)), pygame.SRCALPHA)
        offset_points = [(p[0] - int(self.x - self.size * 1.5), 
                         p[1] - int(self.y - self.size * 1.5)) for p in points]
        
        pygame.draw.polygon(surf, (*self.color, alpha), offset_points)
        screen.blit(surf, (int(self.x - self.size * 1.5), int(self.y - self.size * 1.5)))
    
    def _draw_spark(self, screen, alpha):
        """Dibuja partícula tipo chispa (línea)"""
        length = self.size * 2
        angle = math.atan2(self.vel_y, self.vel_x)
        
        end_x = self.x + length * math.cos(angle)
        end_y = self.y + length * math.sin(angle)
        
        # Dibujar línea con degradado
        for i in range(3):
            thickness = max(1, int(self.size - i))
            current_alpha = alpha - (i * 50)
            if current_alpha > 0:
                surf = pygame.Surface((abs(int(end_x - self.x)) + thickness * 2, 
                                      abs(int(end_y - self.y)) + thickness * 2), pygame.SRCALPHA)
                start = (thickness, thickness) if self.x < end_x else (abs(int(end_x - self.x)) + thickness, thickness)
                end = (abs(int(end_x - self.x)) + thickness, abs(int(end_y - self.y)) + thickness) if self.x < end_x else (thickness, abs(int(end_y - self.y)) + thickness)
                
                pygame.draw.line(surf, (*self.color, current_alpha), start, end, thickness)
                screen.blit(surf, (min(int(self.x), int(end_x)) - thickness, 
                                  min(int(self.y), int(end_y)) - thickness))

class ParticleSystem:
    """Sistema de gestión de partículas mejorado"""
    
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, count, color, spread=360, speed_range=(2, 8), 
             lifetime_range=(0.5, 1.5), size_range=(3, 8), particle_type='circle'):
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
            
            particle = Particle(x, y, color_var, velocity, lifetime, size, particle_type)
            self.particles.append(particle)
    
    def emit_explosion(self, x, y, color):
        """Explosión de partículas mejorada"""
        # Círculos grandes
        self.emit(
            x, y,
            count=15,
            color=color,
            spread=360,
            speed_range=(5, 15),
            lifetime_range=(0.3, 0.8),
            size_range=(4, 10),
            particle_type='circle'
        )
        
        # Cuadrados giratorios
        self.emit(
            x, y,
            count=10,
            color=color,
            spread=360,
            speed_range=(3, 10),
            lifetime_range=(0.4, 0.9),
            size_range=(3, 7),
            particle_type='square'
        )
        
        # Chispas
        self.emit(
            x, y,
            count=8,
            color=(255, 255, 200),
            spread=360,
            speed_range=(8, 20),
            lifetime_range=(0.2, 0.5),
            size_range=(2, 4),
            particle_type='spark'
        )
    
    def emit_trail(self, x, y, color):
        """Estela de partículas mejorada"""
        self.emit(
            x, y,
            count=2,
            color=color,
            spread=180,
            speed_range=(0.5, 2),
            lifetime_range=(0.3, 0.6),
            size_range=(2, 5),
            particle_type='circle'
        )
    
    def emit_sparkle(self, x, y):
        """Destello brillante mejorado"""
        colors = [
            (255, 255, 100),
            (255, 200, 100),
            (255, 255, 200)
        ]
        
        # Estrellas
        for color in colors:
            self.emit(
                x, y,
                count=8,
                color=color,
                spread=360,
                speed_range=(2, 8),
                lifetime_range=(0.4, 0.8),
                size_range=(3, 7),
                particle_type='star'
            )
        
        # Chispas adicionales
        self.emit(
            x, y,
            count=12,
            color=(255, 255, 255),
            spread=360,
            speed_range=(5, 15),
            lifetime_range=(0.3, 0.6),
            size_range=(2, 4),
            particle_type='spark'
        )
    
    def emit_powerup_collect(self, x, y):
        """Efecto de recolección de power-up mejorado"""
        # Anillo expansivo de estrellas
        for i in range(12):
            angle = (i / 12) * 360
            rad_angle = math.radians(angle)
            speed = 10
            velocity = (math.cos(rad_angle) * speed, math.sin(rad_angle) * speed)
            
            particle = Particle(
                x, y,
                (255, 255, 100),
                velocity,
                0.8,
                6,
                'star'
            )
            self.particles.append(particle)
        
        # Círculos brillantes
        self.emit(
            x, y,
            count=20,
            color=(255, 255, 0),
            spread=360,
            speed_range=(3, 12),
            lifetime_range=(0.5, 1.2),
            size_range=(4, 8),
            particle_type='circle'
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
    """Pulso visual mejorado para indicar el beat de la música"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = 150
        self.alpha = 255
        self.active = False
        self.rings = []
    
    def trigger(self):
        """Activa el pulso"""
        self.radius = 0
        self.alpha = 255
        self.active = True
        
        # Agregar anillo secundario
        self.rings.append({
            'radius': 0,
            'alpha': 200,
            'max_radius': 100
        })
    
    def update(self, dt):
        """Actualiza el pulso"""
        if self.active:
            self.radius += dt * 400
            self.alpha = int(255 * (1 - self.radius / self.max_radius))
            
            if self.radius >= self.max_radius:
                self.active = False
        
        # Actualizar anillos secundarios
        for ring in self.rings[:]:
            ring['radius'] += dt * 300
            ring['alpha'] = int(200 * (1 - ring['radius'] / ring['max_radius']))
            
            if ring['radius'] >= ring['max_radius']:
                self.rings.remove(ring)
    
    def draw(self, screen):
        """Dibuja el pulso con múltiples anillos"""
        # Anillos secundarios
        for ring in self.rings:
            if ring['alpha'] > 0:
                surf = pygame.Surface((ring['max_radius'] * 2, ring['max_radius'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    surf,
                    (100, 200, 255, ring['alpha']),
                    (ring['max_radius'], ring['max_radius']),
                    int(ring['radius']),
                    4
                )
                screen.blit(surf, (self.x - ring['max_radius'], self.y - ring['max_radius']))
        
        # Pulso principal
        if self.active and self.alpha > 0:
            surf = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
            
            # Múltiples anillos concéntricos
            for i in range(3):
                current_alpha = max(0, self.alpha - (i * 60))
                if current_alpha > 0:
                    pygame.draw.circle(
                        surf,
                        (100, 200, 255, current_alpha),
                        (self.max_radius, self.max_radius),
                        int(self.radius + i * 10),
                        4 - i
                    )
            
            screen.blit(surf, (self.x - self.max_radius, self.y - self.max_radius))