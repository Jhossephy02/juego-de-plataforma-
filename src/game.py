# src/game.py - Sistema de juego completo y mejorado
import pygame
import os
import math
from src.settings import (WIDTH, HEIGHT, FPS, BLACK, WHITE, GREEN, RED, YELLOW,
                          UI_CONFIG, PURPLE)
from src.entities.player import Player
from src.entities.obstacle_manager import ObstacleManager
from src.world.parallax import Parallax
from src.core.audio_analyzer import AudioAnalyzer
from src.effects.particles import ParticleSystem, BeatPulse

class Game:
    """Clase principal del juego con mejoras visuales y de gameplay"""
    
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
        
        # Efectos visuales
        self.particle_system = ParticleSystem()
        self.beat_pulse = BeatPulse(WIDTH // 2, HEIGHT // 2)
        
        # Estado del juego
        self.game_time = 0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 3
        self.max_health = 3
        self.game_over = False
        self.paused = False
        self.music_started = False
        
        # Power-ups activos
        self.shield_active = False
        self.shield_timer = 0
        self.shield_duration = 5.0
        
        # UI
        self.setup_ui()
        
        # Sistema de cámara shake
        self.camera_shake = 0
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        
        # Detección de beats para efectos
        self.last_beat_time = 0
        self.beat_cooldown = 0.1
    
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
        
        # Detectar beats para efectos visuales
        if self.audio_analyzer:
            if self.audio_analyzer.is_beat(self.game_time, 0.05):
                if self.game_time - self.last_beat_time > self.beat_cooldown:
                    self.beat_pulse.trigger()
                    self.last_beat_time = self.game_time
        
        # Actualizar camera shake
        if self.camera_shake > 0:
            self.camera_shake -= dt * 5
            import random
            self.camera_offset_x = random.randint(-int(self.camera_shake * 10), int(self.camera_shake * 10))
            self.camera_offset_y = random.randint(-int(self.camera_shake * 10), int(self.camera_shake * 10))
        else:
            self.camera_offset_x = 0
            self.camera_offset_y = 0
        
        # Actualizar capas de parallax
        for layer in self.layers:
            layer.update(dt * 1000)
        
        # Actualizar jugador
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.ground_y)
        
        # Actualizar obstáculos
        self.obstacle_manager.update(dt, self.game_time)
        
        # Verificar colisión con power-ups
        powerup_type = self.obstacle_manager.check_powerup_collision(self.player.rect)
        if powerup_type:
            self.activate_powerup(powerup_type)
        
        # Actualizar power-ups activos
        if self.shield_active:
            self.shield_timer += dt
            if self.shield_timer >= self.shield_duration:
                self.shield_active = False
                self.shield_timer = 0
        
        # Verificar colisiones con obstáculos
        collision = self.obstacle_manager.check_collision(self.player.rect)
        if collision:
            if self.shield_active:
                # El escudo absorbe el golpe
                collision.kill()
                self.shield_active = False
                self.particle_system.emit_explosion(
                    collision.rect.centerx,
                    collision.rect.centery,
                    (100, 200, 255)
                )
            elif not self.player.invulnerable:
                self.handle_collision(collision)
        
        # Verificar obstáculos esquivados
        self.check_dodged_obstacles()
        
        # Actualizar efectos
        self.particle_system.update(dt)
        self.beat_pulse.update(dt)
        
        # Generar estela de partículas del jugador
        if int(self.game_time * 60) % 3 == 0:
            self.particle_system.emit_trail(
                self.player.rect.centerx,
                self.player.rect.centery,
                (100, 150, 255)
            )
        
        # Verificar fin de música
        if self.music_path and not pygame.mixer.music.get_busy() and self.game_time > 1:
            self.game_over = True
            print(f"\n🎉 ¡Juego completado! Score: {self.score}")
    
    def activate_powerup(self, powerup_type):
        """Activa un power-up"""
        if powerup_type == 'shield':
            self.shield_active = True
            self.shield_timer = 0
            print("🛡️ ¡Escudo activado!")
            
            # Efecto visual
            self.particle_system.emit_powerup_collect(
                self.player.rect.centerx,
                self.player.rect.centery
            )
    
    def handle_collision(self, obstacle):
        """Maneja colisión con obstáculo"""
        self.health -= 1
        self.combo = 0
        self.player.take_damage()
        
        # Efecto de cámara shake
        self.camera_shake = 2.0
        
        # Partículas de colisión
        self.particle_system.emit_explosion(
            obstacle.rect.centerx,
            obstacle.rect.centery,
            RED
        )
        
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
                points = obstacle.get_score()
                
                # Multiplicador de combo
                combo_mult = 1.0 + (self.combo * 0.1)
                final_points = int(points * combo_mult)
                
                self.score += final_points
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                obstacle.counted = True
                
                # Efecto visual de combo
                if self.combo > 1:
                    self.particle_system.emit_sparkle(
                        obstacle.rect.centerx,
                        obstacle.rect.centery
                    )
    
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
        # Aplicar offset de cámara
        camera_surface = pygame.Surface((WIDTH, HEIGHT))
        
        # Fondo
        camera_surface.fill(BLACK)
        
        # Capas de parallax
        for layer in self.layers:
            layer.draw(camera_surface)
        
        # Pulso de beat (detrás de todo)
        self.beat_pulse.draw(camera_surface)
        
        # Suelo
        pygame.draw.rect(camera_surface, (80, 60, 40),
                        (0, self.ground_y, WIDTH, HEIGHT - self.ground_y))
        
        # Línea de suelo
        pygame.draw.line(camera_surface, (100, 80, 50),
                        (0, self.ground_y), (WIDTH, self.ground_y), 3)
        
        # Obstáculos
        self.obstacle_manager.draw(camera_surface)
        
        # Partículas
        self.particle_system.draw(camera_surface)
        
        # Jugador
        self.player.draw(camera_surface)
        
        # Escudo visual si está activo
        if self.shield_active:
            shield_alpha = int(100 + math.sin(self.game_time * 10) * 50)
            shield_surf = pygame.Surface((80, 80))
            shield_surf.set_colorkey((0, 0, 0))
            shield_surf.set_alpha(shield_alpha)
            pygame.draw.circle(shield_surf, (100, 200, 255), (40, 40), 35, 3)
            camera_surface.blit(shield_surf, (self.player.rect.centerx - 40, self.player.rect.centery - 40))
        
        # UI
        self.draw_ui(camera_surface)
        
        # Aplicar camera shake
        self.screen.blit(camera_surface, (self.camera_offset_x, self.camera_offset_y))
        
        # Pantalla de pausa (sin shake)
        if self.paused:
            self.draw_pause_screen()
        
        # Pantalla de game over (sin shake)
        if self.game_over:
            self.draw_game_over_screen()
    
    def draw_ui(self, surface):
        """Dibuja la interfaz de usuario"""
        # Score
        score_text = self.font_large.render(
            f"Score: {self.score}",
            True, WHITE
        )
        surface.blit(score_text, UI_CONFIG['score_pos'])
        
        # Salud
        health_x, health_y = UI_CONFIG['health_pos']
        heart_size = 30
        spacing = 40
        
        for i in range(self.max_health):
            color = RED if i < self.health else (50, 50, 50)
            pygame.draw.circle(
                surface, color,
                (health_x + i * spacing, health_y),
                heart_size // 2
            )
        
        # Combo
        if self.combo > 1:
            combo_scale = 1.0 + math.sin(self.game_time * 10) * 0.1
            combo_size = int(self.font_large.get_height() * combo_scale)
            combo_font = pygame.font.SysFont('arial', combo_size, bold=True)
            
            combo_text = combo_font.render(
                f"COMBO x{self.combo}",
                True, YELLOW
            )
            combo_rect = combo_text.get_rect(center=UI_CONFIG['combo_pos'])
            
            surface.blit(combo_text, combo_rect)
        
        # Power-ups activos
        if self.shield_active:
            shield_text = self.font_small.render(
                f"🛡️ Escudo: {self.shield_duration - self.shield_timer:.1f}s",
                True, (100, 200, 255)
            )
            surface.blit(shield_text, (20, 80))
        
        # Información de música
        if self.audio_analyzer:
            progress = min(1.0, self.game_time / self.audio_analyzer.duration)
            bar_width = 300
            bar_height = 20
            bar_x = WIDTH // 2 - bar_width // 2
            bar_y = HEIGHT - 50
            
            # Barra de fondo
            pygame.draw.rect(surface, (50, 50, 50),
                           (bar_x, bar_y, bar_width, bar_height),
                           border_radius=10)
            
            # Barra de progreso
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                pygame.draw.rect(surface, (100, 200, 100),
                               (bar_x, bar_y, progress_width, bar_height),
                               border_radius=10)
            
            # Borde
            pygame.draw.rect(surface, (100, 100, 100),
                           (bar_x, bar_y, bar_width, bar_height),
                           2, border_radius=10)
            
            # Tiempo
            time_text = self.font_small.render(
                f"{int(self.game_time)}s / {int(self.audio_analyzer.duration)}s",
                True, (200, 200, 200)
            )
            time_rect = time_text.get_rect(center=(WIDTH // 2, bar_y - 15))
            surface.blit(time_text, time_rect)
    
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