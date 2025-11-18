# src/ui/difficulty_selector.py - Selector de dificultad

import pygame
import math
from src.settings import WIDTH, HEIGHT

class DifficultyButton:
    """Botón de selección de dificultad"""
    
    def __init__(self, rect, difficulty, color, description):
        self.rect = pygame.Rect(rect)
        self.difficulty = difficulty
        self.color = color
        self.description = description
        self.hovered = False
        self.scale = 1.0
    
    def update(self, events):
        """Actualiza el botón"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Animación de hover
        target_scale = 1.1 if self.hovered else 1.0
        self.scale += (target_scale - self.scale) * 0.2
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered:
                    return True
        return False
    
    def draw(self, screen, font_title, font_desc):
        """Dibuja el botón"""
        # Aplicar escala
        rect = self.rect.copy()
        if self.scale != 1.0:
            size_increase = int((self.scale - 1.0) * rect.width)
            rect.inflate_ip(size_increase, size_increase)
        
        # Sombra
        shadow_rect = rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=15)
        
        # Fondo
        pygame.draw.rect(screen, self.color, rect, border_radius=15)
        
        # Borde
        border_color = (255, 255, 255) if self.hovered else (200, 200, 200)
        border_width = 4 if self.hovered else 2
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=15)
        
        # Título
        title_text = font_title.render(self.difficulty.upper(), True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(rect.centerx, rect.centery - 20))
        screen.blit(title_text, title_rect)
        
        # Descripción
        desc_text = font_desc.render(self.description, True, (220, 220, 220))
        desc_rect = desc_text.get_rect(center=(rect.centerx, rect.centery + 20))
        screen.blit(desc_text, desc_rect)

class DifficultySelector:
    """Pantalla de selección de dificultad"""
    
    # Configuración de dificultades
    DIFFICULTIES = {
        'easy': {
            'speed_mult': 0.7,
            'spawn_mult': 0.8,
            'description': 'Para principiantes',
            'color': (100, 200, 100)
        },
        'normal': {
            'speed_mult': 1.0,
            'spawn_mult': 1.0,
            'description': 'Equilibrado',
            'color': (100, 150, 255)
        },
        'hard': {
            'speed_mult': 1.3,
            'spawn_mult': 1.3,
            'description': 'Desafío intenso',
            'color': (255, 150, 50)
        },
        'insane': {
            'speed_mult': 1.6,
            'spawn_mult': 1.6,
            'description': '¡Solo expertos!',
            'color': (255, 50, 50)
        }
    }
    
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.selected_difficulty = None
        
        # Fuentes
        self.font_title = pygame.font.SysFont('arial', 72, bold=True)
        self.font_button_title = pygame.font.SysFont('arial', 32, bold=True)
        self.font_button_desc = pygame.font.SysFont('arial', 18)
        self.font_small = pygame.font.SysFont('arial', 20)
        
        # Crear botones de dificultad
        button_width = 250
        button_height = 120
        button_spacing = 280
        start_x = WIDTH // 2 - (button_spacing * 2) + (button_spacing // 2) - (button_width // 2)
        y_pos = HEIGHT // 2 - 20
        
        self.buttons = []
        for i, (difficulty, config) in enumerate(self.DIFFICULTIES.items()):
            button = DifficultyButton(
                (start_x + i * button_spacing, y_pos, button_width, button_height),
                difficulty,
                config['color'],
                config['description']
            )
            self.buttons.append(button)
        
        # Animación del título
        self.title_time = 0
    
    def run(self):
        """Loop principal del selector"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.title_time += dt
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
            
            # Actualizar botones
            for button in self.buttons:
                if button.update(events):
                    self.selected_difficulty = button.difficulty
                    self.running = False
            
            # Dibujar
            self._draw()
            pygame.display.flip()
        
        return self.selected_difficulty
    
    def _draw(self):
        """Dibuja la pantalla"""
        # Fondo degradado
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(30 + ratio * 20)
            g = int(40 + ratio * 30)
            b = int(80 + ratio * 60)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        
        # Título con animación
        title_scale = 1.0 + math.sin(self.title_time * 2) * 0.03
        title_text = "Selecciona Dificultad"
        title_surf = self.font_title.render(title_text, True, (255, 255, 255))
        
        scaled_width = int(title_surf.get_width() * title_scale)
        scaled_height = int(title_surf.get_height() * title_scale)
        title_surf = pygame.transform.scale(title_surf, (scaled_width, scaled_height))
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 150))
        
        # Sombra del título
        shadow_surf = self.font_title.render(title_text, True, (0, 0, 0))
        shadow_surf = pygame.transform.scale(shadow_surf, (scaled_width, scaled_height))
        shadow_rect = shadow_surf.get_rect(center=(WIDTH // 2 + 3, 153))
        self.screen.blit(shadow_surf, shadow_rect)
        self.screen.blit(title_surf, title_rect)
        
        # Dibujar botones
        for button in self.buttons:
            button.draw(self.screen, self.font_button_title, self.font_button_desc)
        
        # Instrucción
        instruction = self.font_small.render(
            "Selecciona la dificultad que prefieras",
            True, (200, 200, 200)
        )
        instruction_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(instruction, instruction_rect)