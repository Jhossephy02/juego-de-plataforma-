# src/ui/music_selector.py - Sistema completo de selección de música

import pygame
import os
import random
from tkinter import filedialog
import tkinter as tk
from src.settings import WIDTH, HEIGHT, MUSIC_DIR, SUPPORTED_AUDIO_FORMATS

class Button:
    """Botón mejorado con efectos visuales"""
    
    def __init__(self, rect, text, font, bg_color, hover_color, text_color=(0, 0, 0)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.click_animation = 0
    
    def update(self, events):
        """Actualiza estado del botón"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Animación de click
        if self.click_animation > 0:
            self.click_animation -= 0.1
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered:
                    self.click_animation = 1.0
                    return True
        return False
    
    def draw(self, screen):
        """Dibuja el botón con efectos"""
        # Color según estado
        color = self.hover_color if self.hovered else self.bg_color
        
        # Efecto de click
        rect = self.rect.copy()
        if self.click_animation > 0:
            shrink = int(5 * self.click_animation)
            rect.inflate_ip(-shrink, -shrink)
        
        # Sombra
        shadow_rect = rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=12)
        
        # Botón
        pygame.draw.rect(screen, color, rect, border_radius=12)
        
        # Borde brillante si está hover
        if self.hovered:
            pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=12)
        
        # Texto
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

class MusicEntry:
    """Entrada individual de música en el catálogo"""
    
    def __init__(self, rect, filename, font):
        self.rect = pygame.Rect(rect)
        self.filename = filename
        self.display_name = os.path.splitext(filename)[0][:30]  # Truncar nombre
        self.font = font
        self.hovered = False
        self.selected = False
    
    def update(self, events):
        """Actualiza estado"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered:
                    return True
        return False
    
    def draw(self, screen):
        """Dibuja la entrada"""
        # Fondo
        color = (100, 150, 200) if self.selected else ((80, 120, 180) if self.hovered else (60, 80, 120))
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # Borde
        border_color = (255, 255, 255) if self.hovered or self.selected else (100, 120, 150)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)
        
        # Texto
        text_surf = self.font.render(self.display_name, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midleft=(self.rect.left + 15, self.rect.centery))
        screen.blit(text_surf, text_rect)
        
        # Indicador de archivo de audio
        icon_text = self.font.render("♪", True, (150, 200, 255))
        icon_rect = icon_text.get_rect(midright=(self.rect.right - 15, self.rect.centery))
        screen.blit(icon_text, icon_rect)

class MusicSelector:
    """Pantalla de selección de música"""
    
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        
        # Fuentes
        self.font_title = pygame.font.SysFont('arial', 56, bold=True)
        self.font_large = pygame.font.SysFont('arial', 32, bold=True)
        self.font_medium = pygame.font.SysFont('arial', 24)
        self.font_small = pygame.font.SysFont('arial', 18)
        
        # Cargar catálogo de música
        self.music_files = self._load_music_catalog()
        self.selected_music = None
        
        # Scroll
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Crear entradas de música
        self.music_entries = []
        self._create_music_entries()
        
        # Botones
        button_width = 280
        button_height = 55
        button_spacing = 70
        start_y = HEIGHT - 180
        
        self.btn_load_file = Button(
            (WIDTH // 2 - button_width - 10, start_y, button_width, button_height),
            "📁 Cargar Archivo",
            self.font_medium,
            (100, 200, 100),
            (120, 255, 120),
            (255, 255, 255)
        )
        
        self.btn_play = Button(
            (WIDTH // 2 + 10, start_y, button_width, button_height),
            "▶ Jugar",
            self.font_medium,
            (100, 180, 255),
            (120, 200, 255),
            (255, 255, 255)
        )
        
        self.btn_back = Button(
            (WIDTH // 2 - button_width // 2, start_y + button_spacing, button_width, button_height),
            "⬅ Volver al Menú",
            self.font_medium,
            (200, 100, 100),
            (255, 120, 120),
            (255, 255, 255)
        )
        
        # Partículas de fondo
        self.particles = []
        for _ in range(30):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'speed': random.uniform(0.5, 2),
                'size': random.randint(2, 5)
            })
    
    def _load_music_catalog(self):
        """Carga archivos de música del directorio"""
        music_files = []
        
        if os.path.exists(MUSIC_DIR):
            for file in os.listdir(MUSIC_DIR):
                if any(file.lower().endswith(ext) for ext in SUPPORTED_AUDIO_FORMATS):
                    music_files.append(file)
        
        music_files.sort()
        return music_files
    
    def _create_music_entries(self):
        """Crea las entradas visuales de música"""
        self.music_entries = []
        
        entry_width = 600
        entry_height = 50
        entry_spacing = 60
        start_x = WIDTH // 2 - entry_width // 2
        start_y = 150
        
        for i, music_file in enumerate(self.music_files):
            entry = MusicEntry(
                (start_x, start_y + i * entry_spacing, entry_width, entry_height),
                music_file,
                self.font_medium
            )
            self.music_entries.append(entry)
        
        # Calcular scroll máximo
        total_height = len(self.music_entries) * entry_spacing
        visible_height = HEIGHT - 400
        self.max_scroll = max(0, total_height - visible_height)
    
    def run(self):
        """Loop principal del selector"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return None, 'quit'
                
                # Scroll con rueda del mouse
                if event.type == pygame.MOUSEWHEEL:
                    self.scroll_offset -= event.y * 30
                    self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None, 'menu'
            
            # Actualizar
            self._update(events)
            
            # Dibujar
            self._draw()
            
            pygame.display.flip()
        
        return self.selected_music, 'play' if self.selected_music else 'menu'
    
    def _update(self, events):
        """Actualiza lógica"""
        # Actualizar partículas
        for particle in self.particles:
            particle['y'] += particle['speed']
            if particle['y'] > HEIGHT:
                particle['y'] = 0
                particle['x'] = random.randint(0, WIDTH)
        
        # Actualizar entradas de música
        for entry in self.music_entries:
            # Ajustar posición por scroll
            entry.rect.y = 150 + self.music_entries.index(entry) * 60 - self.scroll_offset
            
            # Solo actualizar si es visible
            if -60 < entry.rect.y < HEIGHT:
                if entry.update(events):
                    # Seleccionar música
                    for e in self.music_entries:
                        e.selected = False
                    entry.selected = True
                    self.selected_music = os.path.join(MUSIC_DIR, entry.filename)
                    print(f"🎵 Seleccionada: {entry.filename}")
        
        # Actualizar botones
        if self.btn_load_file.update(events):
            self._load_custom_file()
        
        if self.btn_play.update(events):
            if self.selected_music:
                self.running = False
        
        if self.btn_back.update(events):
            self.selected_music = None
            self.running = False
    
    def _load_custom_file(self):
        """Abre diálogo para cargar archivo personalizado"""
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        
        filetypes = [
            ('Archivos de audio', ' '.join(f'*{ext}' for ext in SUPPORTED_AUDIO_FORMATS)),
            ('Todos los archivos', '*.*')
        ]
        
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de música",
            filetypes=filetypes
        )
        
        root.destroy()
        
        if filepath:
            self.selected_music = filepath
            print(f"🎵 Archivo cargado: {os.path.basename(filepath)}")
            
            # Marcar como seleccionado visualmente
            for entry in self.music_entries:
                entry.selected = False
    
    def _draw(self):
        """Dibuja la pantalla"""
        # Fondo degradado
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(20 + ratio * 30)
            g = int(30 + ratio * 40)
            b = int(70 + ratio * 50)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        
        # Partículas de fondo
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                (100, 150, 200),
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
        
        # Título
        title_text = self.font_title.render("Selecciona tu Música", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, 80))
        
        # Sombra del título
        shadow_text = self.font_title.render("Selecciona tu Música", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 3, 83))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Área de scroll (crear máscara de recorte)
        scroll_area = pygame.Surface((WIDTH, HEIGHT - 400))
        scroll_area.set_colorkey((0, 0, 0))
        
        # Dibujar entradas en el área de scroll
        for entry in self.music_entries:
            if -60 < entry.rect.y < HEIGHT:
                entry.draw(self.screen)
        
        # Indicador de scroll si hay más contenido
        if self.max_scroll > 0:
            scroll_text = self.font_small.render("⇅ Usa la rueda del mouse para desplazar", True, (180, 180, 180))
            scroll_rect = scroll_text.get_rect(center=(WIDTH // 2, HEIGHT - 250))
            self.screen.blit(scroll_text, scroll_rect)
        
        # Mensaje si no hay música
        if not self.music_files:
            no_music_text = self.font_medium.render(
                "No hay archivos de música. Usa 'Cargar Archivo' para seleccionar uno.",
                True, (255, 200, 100)
            )
            no_music_rect = no_music_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(no_music_text, no_music_rect)
        
        # Dibujar botones
        self.btn_load_file.draw(self.screen)
        self.btn_play.draw(self.screen)
        self.btn_back.draw(self.screen)
        
        # Indicador de selección
        if self.selected_music:
            selected_name = os.path.basename(self.selected_music)
            selected_text = self.font_small.render(
                f"Seleccionado: {selected_name[:40]}",
                True, (100, 255, 100)
            )
            selected_rect = selected_text.get_rect(center=(WIDTH // 2, HEIGHT - 280))
            self.screen.blit(selected_text, selected_rect)