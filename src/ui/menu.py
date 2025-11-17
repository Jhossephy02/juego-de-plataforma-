# src/ui/menu.py - Menú principal profesional

import pygame
import math
import random
from src.settings import WIDTH, HEIGHT

class MenuButton:
    """Botón animado del menú"""
    
    def __init__(self, rect, text, font, bg_color, hover_color, icon=""):
        self.rect = pygame.Rect(rect)
        self.original_y = rect[1]
        self.text = text
        self.icon = icon
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.hovered = False
        self.animation_time = random.uniform(0, math.pi * 2)
        self.click_scale = 1.0
    
    def update(self, dt, events):
        """Actualiza el botón"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Animación flotante
        self.animation_time += dt * 2
        offset = math.sin(self.animation_time) * 3
        self.rect.y = self.original_y + offset
        
        # Animación de click
        if self.click_scale > 1.0:
            self.click_scale -= dt * 3
            self.click_scale = max(1.0, self.click_scale)
        
        # Detectar click
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered:
                    self.click_scale = 1.15
                    return True
        return False
    
    def draw(self, screen):
        """Dibuja el botón"""
        # Color según estado
        color = self.hover_color if self.hovered else self.bg_color
        
        # Aplicar escala de click
        rect = self.rect.copy()
        if self.click_scale > 1.0:
            size_increase = (self.click_scale - 1.0) * rect.width
            rect.inflate_ip(size_increase, size_increase * 0.5)
        
        # Sombra
        shadow_rect = rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=15)
        
        # Fondo del botón
        pygame.draw.rect(screen, color, rect, border_radius=15)
        
        # Borde brillante
        if self.hovered:
            pygame.draw.rect(screen, (255, 255, 255), rect, 4, border_radius=15)
        else:
            pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=15)
        
        # Icono
        if self.icon:
            icon_font = pygame.font.SysFont('arial', 48)
            icon_surf = icon_font.render(self.icon, True, (255, 255, 255))
            icon_rect = icon_surf.get_rect(midleft=(rect.left + 20, rect.centery))
            screen.blit(icon_surf, icon_rect)
        
        # Texto
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        if self.icon:
            text_rect = text_surf.get_rect(center=(rect.centerx + 20, rect.centery))
        else:
            text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

class Particle:
    """Partícula decorativa para el menú"""
    
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed_y = random.uniform(20, 60)
        self.speed_x = random.uniform(-10, 10)
        self.size = random.randint(2, 6)
        self.color = random.choice([
            (100, 150, 255),
            (150, 100, 255),
            (255, 150, 200),
            (150, 255, 200)
        ])
        self.alpha = random.randint(100, 200)
        self.lifetime = random.uniform(3, 6)
        self.age = 0
    
    def update(self, dt):
        """Actualiza la partícula"""
        self.y += self.speed_y * dt
        self.x += self.speed_x * dt
        self.age += dt
        
        # Desvanecer al final de la vida
        fade_start = self.lifetime * 0.7
        if self.age > fade_start:
            fade_progress = (self.age - fade_start) / (self.lifetime - fade_start)
            self.alpha = int(200 * (1 - fade_progress))
        
        # Resetear si sale de pantalla o muere
        if self.y > HEIGHT + 10 or self.age > self.lifetime:
            self.__init__()
            self.y = -10
    
    def draw(self, screen):
        """Dibuja la partícula"""
        surf = pygame.Surface((self.size * 2, self.size * 2))
        surf.set_colorkey((0, 0, 0))
        pygame.draw.circle(surf, self.color, (self.size, self.size), self.size)
        surf.set_alpha(self.alpha)
        screen.blit(surf, (self.x - self.size, self.y - self.size))

def run_menu(screen, clock):
    """Menú principal del juego"""
    
    # Fuentes
    font_title = pygame.font.SysFont('arial', 80, bold=True)
    font_subtitle = pygame.font.SysFont('arial', 28, italic=True)
    font_button = pygame.font.SysFont('arial', 36, bold=True)
    font_small = pygame.font.SysFont('arial', 18)
    
    # Crear botones
    button_width = 350
    button_height = 70
    button_spacing = 90
    start_y = HEIGHT // 2 + 20
    
    btn_play = MenuButton(
        (WIDTH // 2 - button_width // 2, start_y, button_width, button_height),
        "JUGAR",
        font_button,
        (80, 150, 255),
        (100, 180, 255),
        "▶"
    )
    
    btn_options = MenuButton(
        (WIDTH // 2 - button_width // 2, start_y + button_spacing, button_width, button_height),
        "OPCIONES",
        font_button,
        (150, 100, 255),
        (180, 130, 255),
        "⚙"
    )
    
    btn_quit = MenuButton(
        (WIDTH // 2 - button_width // 2, start_y + button_spacing * 2, button_width, button_height),
        "SALIR",
        font_button,
        (255, 100, 100),
        (255, 130, 130),
        "✕"
    )
    
    buttons = [btn_play, btn_options, btn_quit]
    
    # Sistema de partículas
    particles = [Particle() for _ in range(100)]
    
    # Animación del título
    title_scale = 1.0
    title_time = 0
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return 'quit'
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit'
        
        # Actualizar animación del título
        title_time += dt
        title_scale = 1.0 + math.sin(title_time * 2) * 0.05
        
        # Actualizar partículas
        for particle in particles:
            particle.update(dt)
        
        # Actualizar botones
        for button in buttons:
            if button.update(dt, events):
                if button == btn_play:
                    return 'play'
                elif button == btn_options:
                    # Por ahora volver al menú
                    pass
                elif button == btn_quit:
                    return 'quit'
        
        # Dibujar
        # Fondo degradado
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(30 + ratio * 20)
            g = int(40 + ratio * 30)
            b = int(80 + ratio * 60)
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
        
        # Dibujar partículas
        for particle in particles:
            particle.draw(screen)
        
        # Título con efecto de escala
        title_text = "RAYMAN SHINOBI"
        title_surf = font_title.render(title_text, True, (255, 255, 255))
        
        # Aplicar escala
        scaled_width = int(title_surf.get_width() * title_scale)
        scaled_height = int(title_surf.get_height() * title_scale)
        title_surf = pygame.transform.scale(title_surf, (scaled_width, scaled_height))
        
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 180))
        
        # Sombra del título
        shadow_surf = font_title.render(title_text, True, (0, 0, 0))
        shadow_surf = pygame.transform.scale(shadow_surf, (scaled_width, scaled_height))
        shadow_rect = shadow_surf.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 2 - 176))
        screen.blit(shadow_surf, shadow_rect)
        
        # Título
        screen.blit(title_surf, title_rect)
        
        # Subtítulo
        subtitle = font_subtitle.render("Music Rhythm Runner", True, (200, 220, 255))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(subtitle, subtitle_rect)
        
        # Dibujar botones
        for button in buttons:
            button.draw(screen)
        
        # Instrucciones en la parte inferior
        instructions = [
            "Controles: ESPACIO / ↑ / W - Saltar (doble salto disponible)",
            "ESC - Pausar | R - Reiniciar (en Game Over)"
        ]
        
        y_offset = HEIGHT - 60
        for instruction in instructions:
            text = font_small.render(instruction, True, (180, 180, 200))
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 25
        
        # Versión
        version_text = font_small.render("v1.0 | Made with ♥", True, (150, 150, 170))
        version_rect = version_text.get_rect(bottomright=(WIDTH - 20, HEIGHT - 10))
        screen.blit(version_text, version_rect)
        
        pygame.display.flip()
    
    return 'quit'