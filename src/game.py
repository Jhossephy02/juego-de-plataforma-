# src/game.py - Sistema de juego mejorado con mejor jugabilidad

import pygame
import os
import math
from src.settings import (WIDTH, HEIGHT, FPS, BLACK, WHITE, GREEN, RED, YELLOW,
                          UI_CONFIG, PURPLE, BLUE)
from src.entities.player import Player
from src.entities.obstacle_manager import ObstacleManager
from src.world.parallax import Parallax
from src.core.audio_analyzer import AudioAnalyzer
from src.effects.particles import ParticleSystem, BeatPulse

class Game:
    """Juego mejorado con mejor sincronización musical"""
    
    def __init__(self, screen, clock, music_path=None, difficulty='normal'):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.difficulty = difficulty
        
        # Sistema de música y análisis
        self.music_path = music_path
        self.audio_analyzer = None
        
        if music_path and os.path.exists(music_path):
            try:
                print(f"\n{'='*60}")
                print(f"🎮 INICIANDO JUEGO - Dificultad: {difficulty.upper()}")
                print(f"{'='*60}")
                
                # Analizar audio
                self.audio_analyzer = AudioAnalyzer(music_path)
                
                # Cargar y reproducir música
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.7)
                
                print(f"{'='*60}\n")
            except Exception as e:
                print(f"❌ Error con el audio: {e}")
                self.audio_analyzer = None
        
        # Setup del mundo
        base = os.path.dirname(os.path.dirname(__file__))
        
        # Capas de parallax con velocidad ajustada por dificultad
        diff_mult = self._get_difficulty_multiplier()
        layers = [
            ('sky', 'sky.png', 0.01 * diff_mult),
            ('mountains', 'mountains.png', 0.03 * diff_mult),
            ('mid', 'mid1.png', 0.05 * diff_mult),
            ('mid', 'mid2.png', 0.07 * diff_mult),
            ('foreground', 'fg1.png', 0.1 * diff_mult),
            ('foreground', 'fg2.png', 0.13 * diff_mult)
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
        
        # Aplicar multiplicadores de dificultad
        self._apply_difficulty_settings()
        
        # Efectos visuales
        self.particle_system = ParticleSystem()
        self.beat_pulse = BeatPulse(WIDTH // 2, HEIGHT // 2)
        self.beat_indicators = []  # Indicadores visuales de beats
        
        # Estado del juego
        self.game_time = 0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.perfect_dodges = 0  # Esquivas perfectas (muy cerca)
        self.health = 3
        self.max_health = 3
        self.game_over = False
        self.paused = False
        self.music_started = False
        
        # Slow motion
        self.slow_motion_active = False
        self.slow_motion_timer = 0
        self.slow_motion_duration = 3.0
        
        # UI
        self.setup_ui()
        
        # Sistema de cámara shake
        self.camera_shake = 0
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        
        # Detección de beats
        self.last_beat_time = 0
        self.beat_cooldown = 0.1
        
        # Sistema de feedback visual
        self.feedback_messages = []
    
    def _get_difficulty_multiplier(self):
        """Obtiene multiplicador basado en dificultad"""
        from src.ui.difficulty_selector import DifficultySelector
        return DifficultySelector.DIFFICULTIES.get(self.difficulty, {}).get('speed_mult', 1.0)
    
    def _apply_difficulty_settings(self):
        """Aplica configuración de dificultad"""
        from src.ui.difficulty_selector import DifficultySelector
        settings = DifficultySelector.DIFFICULTIES.get(self.difficulty, {})
        
        speed_mult = settings.get('speed_mult', 1.0)
        spawn_mult = settings.get('spawn_mult', 1.0)
        
        # Ajustar velocidad base
        self.obstacle_manager.base_speed *= speed_mult
        
        # Ajustar frecuencia de spawn (inverso porque menor = más rápido)
        self.obstacle_manager.spawn_freq_mult = 1.0 / spawn_mult
    
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
        self.font_tiny = pygame.font.SysFont(
            UI_CONFIG['font_name'],
            14
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
            # Calcular delta time
            dt = self.clock.tick(FPS) / 1000.0
            
            # Aplicar slow motion
            if self.slow_motion_active:
                dt *= 0.5
            
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
                    
                    # Activar slow motion manual (como power-up de habilidad)
                    if event.key == pygame.K_LSHIFT and not self.slow_motion_active:
                        self.activate_slow_motion()
            
            # Actualizar solo si no está pausado
            if not self.paused and not self.game_over:
                self.update(dt)
            
            # Dibujar siempre
            self.draw()
            
            pygame.display.flip()
        
        return 'menu'
    
    def activate_slow_motion(self):
        """Activa cámara lenta temporal"""
        self.slow_motion_active = True
        self.slow_motion_timer = 0
        self.show_feedback("SLOW MOTION!", (100, 200, 255), 1.5)
    
    def update(self, dt):
        """Actualiza la lógica del juego"""
        self.game_time += dt
        
        # Actualizar slow motion
        if self.slow_motion_active:
            self.slow_motion_timer += dt / 0.5  # Compensar por el dt reducido
            if self.slow_motion_timer >= self.slow_motion_duration:
                self.slow_motion_active = False
                self.slow_motion_timer = 0
        
        # Detectar beats para efectos visuales
        if self.audio_analyzer:
            if self.audio_analyzer.is_beat(self.game_time, 0.05):
                if self.game_time - self.last_beat_time > self.beat_cooldown:
                    self.beat_pulse.trigger()
                    self.create_beat_indicator()
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
        self.player.update(keys, self.ground_y, dt)
        
        # Actualizar obstáculos
        self.obstacle_manager.update(dt, self.game_time)
        
        # Verificar colisión con power-ups
        powerup_type = self.obstacle_manager.check_powerup_collision(self.player.rect)
        if powerup_type:
            self.activate_powerup(powerup_type)
        
        # Verificar colisiones con obstáculos
        collision = self.obstacle_manager.check_collision(self.player.rect)
        if collision:
            if self.player.shield_active or self.player.invincible_active:
                # Power-up absorbe el golpe
                collision.kill()
                if self.player.shield_active:
                    self.player.shield_active = False
                self.particle_system.emit_explosion(
                    collision.rect.centerx,
                    collision.rect.centery,
                    (100, 200, 255)
                )
                self.show_feedback("PROTEGIDO!", (100, 255, 100), 1.0)
            elif not self.player.invulnerable:
                self.handle_collision(collision)
        
        # Verificar obstáculos esquivados
        self.check_dodged_obstacles()
        
        # Actualizar efectos
        self.particle_system.update(dt)
        self.beat_pulse.update(dt)
        self.update_beat_indicators(dt)
        self.update_feedback_messages(dt)
        
        # Generar estela de partículas del jugador
        if int(self.game_time * 60) % 3 == 0 and not self.player.on_ground:
            self.particle_system.emit_trail(
                self.player.rect.centerx,
                self.player.rect.bottom,
                BLUE
            )
        
        # Verificar fin de música
        if self.music_path and not pygame.mixer.music.get_busy() and self.game_time > 1:
            self.game_over = True
            self.show_feedback("¡COMPLETADO!", GREEN, 3.0)
            print(f"\n🎉 ¡Juego completado! Score: {self.score}")
    
    def create_beat_indicator(self):
        """Crea indicador visual de beat en el suelo"""
        self.beat_indicators.append({
            'x': WIDTH,
            'alpha': 255,
            'size': 20
        })
    
    def update_beat_indicators(self, dt):
        """Actualiza indicadores de beat"""
        for indicator in self.beat_indicators[:]:
            indicator['x'] -= 300 * dt
            indicator['alpha'] -= 500 * dt
            indicator['size'] += 50 * dt
            
            if indicator['alpha'] <= 0:
                self.beat_indicators.remove(indicator)
    
    def show_feedback(self, message, color, duration=1.0):
        """Muestra mensaje de feedback"""
        self.feedback_messages.append({
            'text': message,
            'color': color,
            'time': 0,
            'duration': duration,
            'y': HEIGHT // 2 - 100
        })
    
    def update_feedback_messages(self, dt):
        """Actualiza mensajes de feedback"""
        for msg in self.feedback_messages[:]:
            msg['time'] += dt
            msg['y'] -= 30 * dt
            
            if msg['time'] >= msg['duration']:
                self.feedback_messages.remove(msg)
    
    def activate_powerup(self, powerup_type):
        """Activa un power-up"""
        self.player.activate_powerup(powerup_type)
        
        if powerup_type == 'shield':
            self.show_feedback("¡ESCUDO!", (100, 200, 255), 1.5)
        elif powerup_type == 'invincible':
            self.show_feedback("¡INVENCIBLE!", YELLOW, 1.5)
        elif powerup_type == 'slow':
            self.activate_slow_motion()
        
        # Efecto visual
        self.particle_system.emit_powerup_collect(
            self.player.rect.centerx,
            self.player.rect.centery
        )
        
        print(f"⭐ Power-up activado: {powerup_type}")
    
    def handle_collision(self, obstacle):
        """Maneja colisión con obstáculo"""
        if self.player.take_damage():
            self.health -= 1
            self.combo = 0
            
            # Efecto de cámara shake
            self.camera_shake = 2.0
            
            # Partículas de colisión
            self.particle_system.emit_explosion(
                obstacle.rect.centerx,
                obstacle.rect.centery,
                RED
            )
            
            # Feedback
            self.show_feedback("¡AUCH!", RED, 1.0)
            
            # Eliminar obstáculo
            obstacle.kill()
            
            print(f"💥 Colisión! HP: {self.health}")
            
            if self.health <= 0:
                self.game_over = True
                pygame.mixer.music.stop()
                self.show_feedback("GAME OVER", RED, 3.0)
                print(f"\n💀 Game Over! Score final: {self.score}")
    
    def check_dodged_obstacles(self):
        """Verifica si se esquivó algún obstáculo"""
        for obstacle in self.obstacle_manager.obstacles:
            # Si el obstáculo pasó al jugador
            if obstacle.rect.right < self.player.rect.left and not hasattr(obstacle, 'counted'):
                points = obstacle.get_score()
                
                # Verificar si fue esquiva perfecta (muy cerca)
                distance = abs(obstacle.rect.right - self.player.rect.left)
                perfect_dodge = distance < 50
                
                if perfect_dodge:
                    self.perfect_dodges += 1
                    points *= 2
                    self.show_feedback("¡PERFECTO!", YELLOW, 0.8)
                    self.particle_system.emit_sparkle(
                        self.player.rect.centerx,
                        self.player.rect.centery
                    )
                
                # Multiplicador de combo
                combo_mult = 1.0 + (self.combo * 0.1)
                final_points = int(points * combo_mult)
                
                self.score += final_points
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                obstacle.counted = True
                
                # Efecto visual de combo
                if self.combo > 3:
                    self.show_feedback(f"COMBO x{self.combo}!", GREEN, 0.6)
    
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
        
        # Pulso de beat
        self.beat_pulse.draw(camera_surface)
        
        # Indicadores de beat en el suelo
        for indicator in self.beat_indicators:
            alpha = int(indicator['alpha'])
            size = int(indicator['size'])
            surf = pygame.Surface((size * 2, 10), pygame.SRCALPHA)
            color = (100, 200, 255, alpha)
            pygame.draw.rect(surf, color, (0, 0, size * 2, 10), border_radius=5)
            camera_surface.blit(surf, (indicator['x'] - size, self.ground_y - 5))
        
        # Suelo
        pygame.draw.rect(camera_surface, (80, 60, 40),
                        (0, self.ground_y, WIDTH, HEIGHT - self.ground_y))
        
        # Línea de suelo con efecto
        pygame.draw.line(camera_surface, (100, 80, 50),
                        (0, self.ground_y), (WIDTH, self.ground_y), 3)
        
        # Obstáculos
        self.obstacle_manager.draw(camera_surface)
        
        # Partículas
        self.particle_system.draw(camera_surface)
        
        # Jugador
        self.player.draw(camera_surface)
        
        # UI
        self.draw_ui(camera_surface)
        
        # Feedback messages
        self.draw_feedback_messages(camera_surface)
        
        # Aplicar camera shake
        self.screen.blit(camera_surface, (self.camera_offset_x, self.camera_offset_y))
        
        # Pantallas superpuestas (sin shake)
        if self.paused:
            self.draw_pause_screen()
        
        if self.game_over:
            self.draw_game_over_screen()
    
    def draw_ui(self, surface):
        """Dibuja la interfaz de usuario mejorada"""
        # Score
        score_text = self.font_large.render(
            f"{self.score}",
            True, WHITE
        )
        surface.blit(score_text, (20, 20))
        
        # Label de score
        label_text = self.font_tiny.render("SCORE", True, (180, 180, 180))
        surface.blit(label_text, (20, 60))
        
        # Salud
        health_x, health_y = WIDTH - 200, 30
        for i in range(self.max_health):
            color = RED if i < self.health else (50, 50, 50)
            pygame.draw.circle(surface, color, (health_x + i * 40, health_y), 15)
            pygame.draw.circle(surface, (255, 255, 255), (health_x + i * 40, health_y), 15, 2)
        
        # Combo
        if self.combo > 1:
            combo_scale = 1.0 + math.sin(self.game_time * 10) * 0.1
            combo_size = int(32 * combo_scale)
            combo_font = pygame.font.SysFont('arial', combo_size, bold=True)
            
            combo_text = combo_font.render(
                f"x{self.combo}",
                True, YELLOW
            )
            combo_rect = combo_text.get_rect(midtop=(WIDTH // 2, 20))
            
            # Sombra
            shadow = combo_font.render(f"x{self.combo}", True, BLACK)
            shadow_rect = shadow.get_rect(midtop=(WIDTH // 2 + 2, 22))
            surface.blit(shadow, shadow_rect)
            surface.blit(combo_text, combo_rect)
        
        # Barra de progreso musical
        if self.audio_analyzer:
            progress = min(1.0, self.game_time / self.audio_analyzer.duration)
            bar_width = 300
            bar_height = 8
            bar_x = WIDTH // 2 - bar_width // 2
            bar_y = HEIGHT - 30
            
            # Fondo
            pygame.draw.rect(surface, (50, 50, 50),
                           (bar_x, bar_y, bar_width, bar_height),
                           border_radius=4)
            
            # Progreso
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                pygame.draw.rect(surface, (100, 200, 255),
                               (bar_x, bar_y, progress_width, bar_height),
                               border_radius=4)
            
            # Marcadores de beats
            for beat_time in self.audio_analyzer.beat_times:
                if beat_time < self.audio_analyzer.duration:
                    beat_x = bar_x + int((beat_time / self.audio_analyzer.duration) * bar_width)
                    pygame.draw.line(surface, (255, 255, 255),
                                   (beat_x, bar_y), (beat_x, bar_y + bar_height), 1)
    
    def draw_feedback_messages(self, surface):
        """Dibuja mensajes de feedback"""
        for msg in self.feedback_messages:
            alpha = int(255 * (1 - msg['time'] / msg['duration']))
            font = pygame.font.SysFont('arial', 48, bold=True)
            
            text = font.render(msg['text'], True, msg['color'])
            text.set_alpha(alpha)
            
            text_rect = text.get_rect(center=(WIDTH // 2, int(msg['y'])))
            surface.blit(text, text_rect)
    
    def draw_pause_screen(self):
        """Dibuja pantalla de pausa"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_font = pygame.font.SysFont('arial', 72, bold=True)
        pause_text = pause_font.render("PAUSA", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        instructions = [
            "ESC - Continuar",
            "R - Reiniciar (Game Over)",
        ]
        
        y_offset = HEIGHT // 2 + 50
        for instruction in instructions:
            text = self.font_medium.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40
    
    def draw_game_over_screen(self):
        """Dibuja pantalla de game over"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title_font = pygame.font.SysFont('arial', 72, bold=True)
        
        if self.health <= 0:
            title = title_font.render("GAME OVER", True, RED)
        else:
            title = title_font.render("¡COMPLETADO!", True, GREEN)
        
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        self.screen.blit(title, title_rect)
        
        # Estadísticas detalladas
        stats = [
            f"Score Final: {self.score}",
            f"Max Combo: x{self.max_combo}",
            f"Esquivas Perfectas: {self.perfect_dodges}",
            f"Dificultad: {self.difficulty.title()}",
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
            "R - Reintentar",
            "ESC - Volver al menú",
        ]
        
        for instruction in instructions:
            text = self.font_medium.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35