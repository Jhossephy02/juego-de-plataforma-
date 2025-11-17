# src/game.py - Sistema de juego mejorado con generación basada en música

import pygame
import os
from src.settings import (WIDTH, HEIGHT, FPS, BLACK, WHITE, GREEN, RED, YELLOW,
                          UI_CONFIG)
from src.entities.player import Player
from src.entities.obstacle_manager import ObstacleManager
from src.world.parallax import Parallax
from src.core.audio_analyzer import AudioAnalyzer

class Game:
    """Clase principal del juego"""
    
    def __init__(self, screen, clock, music_path=None):
        self.screen = screen
        self.clock = clock
        self.running = True
        
        # Sistema de música y análisis
        self.music_path = music_path
        self.audio_analyzer = None
        
        if music_path and os.path.exists(music_path):
            try:
                print(f"\n{'='*60}")
                print(f"🎮 INICIANDO JUEGO")
                print(f"{'='*60}")
                
                # Analizar audio
                self.audio_analyzer = AudioAnalyzer(music_path)
                
                # Cargar y reproducir música
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.6)
                
                print(f"{'='*60}\n")
            except Exception as e:
                print(f"❌ Error con el audio: {e}")
                self.audio_analyzer = None
        
        # Setup del mundo
        base = os.path.dirname(os.path.dirname(__file__))
        
        # Capas de parallax
        layers = [
            ('sky', 'sky.png', 0.01),
            ('mountains', 'mountains.png', 0.03),
            ('mid', 'mid1.png', 0.05),
            ('mid', 'mid2.png', 0.07),
            ('foreground', 'fg1.png', 0.1),
            ('foreground', 'fg2.png', 0.13)
        ]
        
        self.layers = []
        for folder, filename, speed in layers:
            try:
                parallax = Parallax(base, folder, filename, speed)
                self.layers.append(parallax)
            except Exception as e:
                print(f"⚠️ No se pudo cargar capa {filename}: {e}")
        
        # Jugador
        self.ground_y = HEIGHT - 80
        self.player = Player((200, self.ground_y - 50))
        
        # Sistema de obstáculos
        self.obstacle_manager = ObstacleManager(
            self.audio_analyzer,
            self.ground_y
        )
        
        # Estado del juego
        self.game_time = 0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 3
        self.game_over = False
        self.paused = False
        self.music_started = False
        
        # UI
        self.setup_ui()
        
        # Contador de frames para debug
        self.frame_count = 0
    
    def setup_ui(self):
        """Configura elementos de UI"""
        self.font_large = pygame.font.SysFont(
            UI_CONFIG['font_name'],
            UI_CONFIG['font_size'],
            bold=True
        )
        self.font_medium = pygame.font.SysFont(
            UI_CONFIG['font_name'],
            24
        )
        self.font_small = pygame.font.SysFont(
            UI_CONFIG['font_name'],
            18
        )
    
    def start_music(self):
        """Inicia la reproducción de música"""
        if not self.music_started and self.music_path:
            try:
                pygame.mixer.music.play()
                self.music_started = True
                print("🎵 Música iniciada")
            except Exception as e:
                print(f"Error iniciando música: {e}")
    
    def run(self):
        """Loop principal del juego"""
        # Pantalla de countdown
        self.countdown()
        
        # Iniciar música
        self.start_music()
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.frame_count += 1
            
            # Eventos
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return 'quit'
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_over:
                            return 'menu'
                        else:
                            self.paused = not self.paused
                    
                    if event.key == pygame.K_r and self.game_over:
                        return 'restart'
            
            # Actualizar solo si no está pausado
            if not self.paused and not self.game_over:
                self.update(dt)
            
            # Dibujar siempre
            self.draw()
            
            pygame.display.flip()
        
        return 'menu'
    
    def update(self, dt):
        """Actualiza la lógica del juego"""
        self.game_time += dt
        
        # Actualizar capas de parallax
        for layer in self.layers:
            layer.update(dt * 1000)
        
        # Actualizar jugador
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.ground_y)
        
        # Actualizar obstáculos
        self.obstacle_manager.update(dt, self.game_time)
        
        # Verificar colisiones
        collision = self.obstacle_manager.check_collision(self.player.rect)
        if collision and not self.player.invulnerable:
            self.handle_collision(collision)
        
        # Verificar obstáculos esquivados
        self.check_dodged_obstacles()
        
        # Verificar fin de música
        if self.music_path and not pygame.mixer.music.get_busy() and self.game_time > 1:
            self.game_over = True
            print(f"\n🎉 ¡Juego completado! Score: {self.score}")
    
    def handle_collision(self, obstacle):
        """Maneja colisión con obstáculo"""
        self.health -= 1
        self.combo = 0
        self.player.take_damage()
        
        # Eliminar obstáculo
        obstacle.kill()
        
        print(f"💥 Colisión! HP: {self.health}")
        
        if self.health <= 0:
            self.game_over = True
            pygame.mixer.music.stop()
            print(f"\n💀 Game Over! Score final: {self.score}")
    
    def check_dodged_obstacles(self):
        """Verifica si se esquivó algún obstáculo"""
        for obstacle in self.obstacle_manager.obstacles:
            # Si el obstáculo pasó al jugador
            if obstacle.rect.right < self.player.rect.left and not hasattr(obstacle, 'counted'):
                self.score += obstacle.get_score()
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                obstacle.counted = True
    
    def countdown(self):
        """Muestra cuenta regresiva antes de comenzar"""
        countdown_font = pygame.font.SysFont('arial', 120, bold=True)
        
        for i in range(3, 0, -1):
            self.screen.fill(BLACK)
            
            # Dibujar fondo
            for layer in self.layers:
                layer.draw(self.screen)
            
            # Número de countdown
            text = countdown_font.render(str(i), True, YELLOW)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            # Sombra
            shadow = countdown_font.render(str(i), True, BLACK)
            shadow_rect = shadow.get_rect(center=(WIDTH // 2 + 5, HEIGHT // 2 + 5))
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(text, text_rect)
            
            pygame.display.flip()
            pygame.time.wait(1000)
        
        # GO!
        self.screen.fill(BLACK)
        for layer in self.layers:
            layer.draw(self.screen)
        
        text = countdown_font.render("GO!", True, GREEN)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        pygame.display.flip()
        pygame.time.wait(500)
    
    def draw(self):
        """Dibuja todo en pantalla"""
        # Fondo
        self.screen.fill(BLACK)
        
        # Capas de parallax
        for layer in self.layers:
            layer.draw(self.screen)
        
        # Suelo
        pygame.draw.rect(self.screen, (80, 60, 40),
                        (0, self.ground_y, WIDTH, HEIGHT - self.ground_y))
        
        # Línea de suelo
        pygame.draw.line(self.screen, (100, 80, 50),
                        (0, self.ground_y), (WIDTH, self.ground_y), 3)
        
        # Obstáculos
        self.obstacle_manager.draw(self.screen)
        
        # Jugador
        self.screen.blit(self.player.image, self.player.rect)
        
        # UI
        self.draw_ui()
        
        # Pantalla de pausa
        if self.paused:
            self.draw_pause_screen()
        
        # Pantalla de game over
        if self.game_over:
            self.draw_game_over_screen()
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        # Score
        score_text = self.font_large.render(
            f"Score: {self.score}",
            True, WHITE
        )
        self.screen.blit(score_text, UI_CONFIG['score_pos'])
        
        # Salud
        health_x, health_y = UI_CONFIG['health_pos']
        heart_size = 30
        spacing = 40
        
        for i in range(3):
            color = RED if i < self.health else (50, 50, 50)
            pygame.draw.circle(
                self.screen, color,
                (health_x + i * spacing, health_y),
                heart_size // 2
            )
        
        # Combo
        if self.combo > 1:
            combo_text = self.font_large.render(
                f"COMBO x{self.combo}",
                True, YELLOW
            )
            combo_rect = combo_text.get_rect(center=UI_CONFIG['combo_pos'])
            
            # Efecto de pulso
            import math
            scale = 1.0 + math.sin(self.game_time * 10) * 0.1
            
            self.screen.blit(combo_text, combo_rect)
        
        # Información de música
        if self.audio_analyzer:
            info_text = self.font_small.render(
                f"Tempo: {self.audio_analyzer.tempo:.0f} BPM | "
                f"Tiempo: {int(self.game_time)}s / {int(self.audio_analyzer.duration)}s",
                True, (200, 200, 200)
            )
            self.screen.blit(info_text, (20, HEIGHT - 30))
    
    def draw_pause_screen(self):
        """Dibuja pantalla de pausa"""
        # Overlay semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Texto
        pause_font = pygame.font.SysFont('arial', 72, bold=True)
        pause_text = pause_font.render("PAUSA", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        # Instrucciones
        instructions = [
            "ESC - Continuar",
            "R - Reiniciar (desde game over)",
        ]
        
        y_offset = HEIGHT // 2 + 50
        for instruction in instructions:
            text = self.font_medium.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40
    
    def draw_game_over_screen(self):
        """Dibuja pantalla de game over"""
        # Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Título
        title_font = pygame.font.SysFont('arial', 72, bold=True)
        
        if self.health <= 0:
            title = title_font.render("GAME OVER", True, RED)
        else:
            title = title_font.render("¡COMPLETADO!", True, GREEN)
        
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        self.screen.blit(title, title_rect)
        
        # Estadísticas
        stats = [
            f"Score Final: {self.score}",
            f"Max Combo: x{self.max_combo}",
            f"Tiempo: {int(self.game_time)}s",
        ]
        
        y_offset = HEIGHT // 2 - 50
        for stat in stats:
            text = self.font_large.render(stat, True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 50
        
        # Instrucciones
        y_offset += 50
        instructions = [
            "R - Reintentar con esta canción",
            "ESC - Volver al menú",
        ]
        
        for instruction in instructions:
            text = self.font_medium.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35