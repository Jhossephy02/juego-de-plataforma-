import pygame
import math
import os
from src.settings import (GRAVITY, PLAYER_SPEED, PLAYER_JUMP, PLAYER_DOUBLE_JUMP,
                          RED, WHITE, BLUE, YELLOW, PURPLE, BASE_DIR)

# ¡¡¡CONTEO REAL DE FRAMES BASADO EN LAS IMÁGENES!!!
FRAME_COUNTS = {
    'Attack_3.png': 4,
    'Dead.png': 3,
    'Hurt.png': 3,
    'Idle.png': 6,
    'Jump.png': 10,
    'Run.png': 9,
}

class Player(pygame.sprite.Sprite):
    """Jugador con sprites animados de Rayman"""
    
    def __init__(self, pos):
        super().__init__()
        
        # Dimensiones
        self.width = 60
        self.height = 70
        
        # Sistema de sprites
        self.animations = {
            'idle': [], 'run': [], 'jump': [], 'fall': [], 
            'attack': [], 'hurt': [], 'dead': [],
        }
        
        self.current_animation = 'idle'
        
        # CORRECCIÓN CLAVE: Usaremos 'animation_frame' como un flotante para una progresión suave.
        self.animation_frame_float = 0.0 
        
        # Velocidad de animación
        self.animation_speed = 0.15  # Velocidad base de animación (segundos por frame)
        self.animation_timer = 0
        
        # Cargar sprites
        self.load_sprites()
        
        # Crear sprite inicial
        if self.animations['idle']:
            self.image = self.animations['idle'][0]
        else:
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self._draw_procedural_fallback()
        
        self.rect = self.image.get_rect(topleft=pos)
        
        # Física
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.on_ground = False
        self.can_double_jump = True
        
        # Estado y control de animación
        self.invulnerable = False
        self.invuln_timer = 0
        self.invuln_duration = 1.5
        self.is_animation_overriding = False 
        
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
        
        # Para fallback procedural
        self.use_procedural = len(self.animations['idle']) == 0
    
    def load_sprites(self): 
        """Carga los sprites desde las carpetas (tiras de sprites)"""
        
        if self._load_from_folders():
            print("✅ Sprites cargados desde carpetas individuales (como sprite sheets)")
            # Asignar fall si jump se cargó
            if self.animations['jump'] and not self.animations['fall']:
                self.animations['fall'] = self.animations['jump'].copy()
            return
        
        if not any(len(v) > 0 for v in self.animations.values()):
            print("⚠️ No se encontraron sprites de Rayman. Usando sprites procedurales.")
            self.use_procedural = True
    
    # --- FUNCIONES DE CARGA Y ESCALADO (Mantenidas) ---
    def _extract_frames_from_sheet(self, sheet, frame_count):
        """
        Divide la tira de sprites horizontal en frames individuales, los recorta y los escala.
        """
        frames = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        
        # Ancho de cada frame
        frame_width = sheet_width // frame_count
        
        for i in range(frame_count):
            # 1. Extraer el sub-sprite (tamaño consistente)
            x = i * frame_width
            frame_surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
            frame_surface.blit(sheet, (0, 0), (x, 0, frame_width, sheet_height))
            
            # 2. Escalar al tamaño del jugador (60x70)
            scaled_frame = self._scale_sprite_to_size(frame_surface, self.width, self.height)
            
            frames.append(scaled_frame)
            
        return frames

    def _load_from_folders(self):
        """Carga sprites desde carpetas individuales, tratando cada PNG como un sprite sheet."""
        player_dir = os.path.join(BASE_DIR, 'assets', 'player')
        # ... (Resto de la lógica de carga, no modificada)
        if not os.path.exists(player_dir):
            return False
        
        file_to_animation = {
            'Idle.png': ('idle', FRAME_COUNTS['Idle.png']),
            'Run.png': ('run', FRAME_COUNTS['Run.png']),
            'Jump.png': ('jump', FRAME_COUNTS['Jump.png']),
            'Attack_3.png': ('attack', FRAME_COUNTS['Attack_3.png']),
            'Hurt.png': ('hurt', FRAME_COUNTS['Hurt.png']),
            'Dead.png': ('dead', FRAME_COUNTS['Dead.png']),
        }
        
        loaded_any = False
        
        for file_name, (animation_key, frame_count) in file_to_animation.items():
            folder_name = file_name.split('.')[0] # Ej: 'Idle'
            folder_path = os.path.join(player_dir, folder_name, file_name)
            
            if not os.path.exists(folder_path):
                folder_path = os.path.join(player_dir, file_name)
            
            if os.path.exists(folder_path):
                try:
                    sheet = pygame.image.load(folder_path).convert_alpha()
                    frames = self._extract_frames_from_sheet(sheet, frame_count)
                    
                    if frames:
                        self.animations[animation_key] = frames
                        loaded_any = True
                        # print(f"✅ Cargado: {file_name} -> {animation_key} ({len(frames)} frames)")
                    else:
                        print(f"⚠️ No se pudieron extraer frames de {file_name}")

                except Exception as e:
                    print(f"⚠️ Error cargando {file_name}: {e}")
            else:
                pass
        
        if not self.animations['fall'] and self.animations['jump']:
            self.animations['fall'] = self.animations['jump'].copy()
        
        return loaded_any
    
    def _scale_sprite_to_size(self, sprite, target_width, target_height):
        """
        Escala el sprite al tamaño objetivo manteniendo proporción
        """
        original_width = sprite.get_width()
        original_height = sprite.get_height()
        
        if original_width == 0 or original_height == 0:
            return sprite
        
        scale_x = target_width / original_width
        scale_y = target_height / original_height
        
        # Usar el menor factor de escala para mantener la proporción y que quepa.
        scale = min(scale_x, scale_y) 
        
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        if new_width > 0 and new_height > 0:
            return pygame.transform.scale(sprite, (new_width, new_height))
        
        return sprite
    
    # ... (funciones auxiliares procedurales, no modificadas)

    def _draw_procedural_fallback(self):
        """Dibuja sprite procedural como fallback si no hay imágenes"""
        # ... (código procedural se mantiene igual)
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.width // 2, self.height // 2
        
        body_color = (50, 150, 255)
        
        # CUERPO
        pygame.draw.ellipse(self.image, body_color, (cx - 15, cy - 20, 30, 40))
        pygame.draw.ellipse(self.image, WHITE, (cx - 15, cy - 20, 30, 40), 2)
        
        # BRAZOS
        pygame.draw.line(self.image, body_color, (cx - 12, cy), (cx - 25, cy + 10), 6)
        pygame.draw.circle(self.image, body_color, (cx - 25, cy + 10), 4)
        pygame.draw.line(self.image, body_color, (cx + 12, cy), (cx + 25, cy + 10), 6)
        pygame.draw.circle(self.image, body_color, (cx + 25, cy + 10), 4)
        
        # PIERNAS
        pygame.draw.line(self.image, body_color, (cx - 6, cy + 15), (cx - 6, cy + 30), 7)
        pygame.draw.circle(self.image, body_color, (cx - 6, cy + 30), 5)
        pygame.draw.line(self.image, body_color, (cx + 6, cy + 15), (cx + 6, cy + 30), 7)
        pygame.draw.circle(self.image, body_color, (cx + 6, cy + 30), 5)
        
        # CABEZA
        pygame.draw.circle(self.image, (255, 220, 180), (cx, cy - 25), 12)
        pygame.draw.circle(self.image, WHITE, (cx, cy - 25), 12, 2)
        pygame.draw.circle(self.image, (0, 0, 0), (cx - 4, cy - 27), 2)
        pygame.draw.circle(self.image, (0, 0, 0), (cx + 4, cy - 27), 2)
        
        # PELO
        hair_points = [(cx - 10, cy - 37), (cx, cy - 43), (cx + 10, cy - 37)]
        pygame.draw.polygon(self.image, (30, 100, 200), hair_points)

    def _draw_procedural_running(self, bounce):
        """Dibuja el personaje corriendo (fallback procedural)"""
        # ... (código procedural se mantiene igual)
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.width // 2, self.height // 2
        body_color = (50, 150, 255)
        
        # CUERPO
        pygame.draw.ellipse(self.image, body_color, (cx - 15, cy - 20 + bounce, 30, 40))
        pygame.draw.ellipse(self.image, WHITE, (cx - 15, cy - 20 + bounce, 30, 40), 2)
        
        # BRAZOS animados
        arm_angle = math.sin(self.animation_time * 15) * 20
        arm_start = (cx - 12, cy + bounce)
        arm_end = (cx - 12 + math.sin(math.radians(arm_angle + 45)) * 15,
                    cy + bounce + math.cos(math.radians(arm_angle + 45)) * 15)
        pygame.draw.line(self.image, body_color, arm_start, arm_end, 6)
        pygame.draw.circle(self.image, body_color, (int(arm_end[0]), int(arm_end[1])), 4)
        
        arm_start = (cx + 12, cy + bounce)
        arm_end = (cx + 12 + math.sin(math.radians(-arm_angle + 45)) * 15,
                    cy + bounce + math.cos(math.radians(-arm_angle + 45)) * 15)
        pygame.draw.line(self.image, body_color, arm_start, arm_end, 6)
        pygame.draw.circle(self.image, body_color, (int(arm_end[0]), int(arm_end[1])), 4)
        
        # PIERNAS animadas
        leg_angle = math.sin(self.animation_time * 15) * 30
        leg_start = (cx - 6, cy + 15 + bounce)
        leg_end = (cx - 6 + math.sin(math.radians(leg_angle)) * 12, cy + 30 + bounce)
        pygame.draw.line(self.image, body_color, leg_start, leg_end, 7)
        pygame.draw.circle(self.image, body_color, (int(leg_end[0]), int(leg_end[1])), 5)
        
        leg_start = (cx + 6, cy + 15 + bounce)
        leg_end = (cx + 6 + math.sin(math.radians(-leg_angle)) * 12, cy + 30 + bounce)
        pygame.draw.line(self.image, body_color, leg_start, leg_end, 7)
        pygame.draw.circle(self.image, body_color, (int(leg_end[0]), int(leg_end[1])), 5)
        
        # CABEZA
        head_y = cy - 25 + bounce
        pygame.draw.circle(self.image, (255, 220, 180), (cx, int(head_y)), 12)
        pygame.draw.circle(self.image, WHITE, (cx, int(head_y)), 12, 2)
        pygame.draw.circle(self.image, (0, 0, 0), (cx - 4, int(head_y - 2)), 2)
        pygame.draw.circle(self.image, (0, 0, 0), (cx + 4, int(head_y - 2)), 2)
        
        # Boca sonriente
        mouth_rect = pygame.Rect(cx - 5, int(head_y + 2), 10, 5)
        pygame.draw.arc(self.image, (0, 0, 0), mouth_rect, 0, math.pi, 2)
        
        # PELO
        hair_points = [(cx - 10, int(head_y - 12)), (cx, int(head_y - 18)), (cx + 10, int(head_y - 12))]
        pygame.draw.polygon(self.image, (30, 100, 200), hair_points)
        pygame.draw.polygon(self.image, WHITE, hair_points, 2)
    
    def _draw_procedural_jump(self):
        """Dibuja el personaje saltando (fallback procedural)"""
        # ... (código procedural se mantiene igual)
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.width // 2, self.height // 2
        body_color = (50, 150, 255)
        
        # CUERPO
        pygame.draw.ellipse(self.image, body_color, (cx - 15, cy - 20, 30, 40))
        pygame.draw.ellipse(self.image, WHITE, (cx - 15, cy - 20, 30, 40), 2)
        
        # BRAZOS extendidos
        pygame.draw.line(self.image, body_color, (cx - 10, cy - 5), (cx - 18, cy - 25), 6)
        pygame.draw.circle(self.image, body_color, (cx - 18, cy - 25), 4)
        pygame.draw.line(self.image, body_color, (cx + 10, cy - 5), (cx + 18, cy - 25), 6)
        pygame.draw.circle(self.image, body_color, (cx + 18, cy - 25), 4)
        
        # PIERNAS juntas
        pygame.draw.line(self.image, body_color, (cx - 6, cy + 15), (cx - 6, cy + 30), 7)
        pygame.draw.circle(self.image, body_color, (cx - 6, cy + 30), 5)
        pygame.draw.line(self.image, body_color, (cx + 6, cy + 15), (cx + 6, cy + 30), 7)
        pygame.draw.circle(self.image, body_color, (cx + 6, cy + 30), 5)
        
        # CABEZA
        pygame.draw.circle(self.image, (255, 220, 180), (cx, cy - 25), 12)
        pygame.draw.circle(self.image, WHITE, (cx, cy - 25), 12, 2)
        pygame.draw.circle(self.image, (0, 0, 0), (cx - 4, cy - 27), 3)
        pygame.draw.circle(self.image, (0, 0, 0), (cx + 4, cy - 27), 3)
        pygame.draw.circle(self.image, (0, 0, 0), (cx, cy - 21), 3, 1)
        
        # PELO
        hair_points = [(cx - 10, cy - 37), (cx, cy - 43), (cx + 10, cy - 37)]
        pygame.draw.polygon(self.image, (30, 100, 200), hair_points)
        pygame.draw.polygon(self.image, WHITE, hair_points, 2)

    def update(self, keys, ground_y, dt):
        """Actualiza el jugador"""
        self.animation_time += dt
        
        # Determinar animación previa
        previous_animation = self.current_animation
        
        # Lógica de Movimiento
        self.vel.x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = self.speed
            self.facing_right = True

        # --- LÓGICA DE DETERMINACIÓN DE ESTADO ---
        
        # Prioridad 1: Animaciones de un solo ciclo (Hurt, Attack, Dead)
        if self.is_animation_overriding:
            if self.current_animation == 'dead':
                pass 
            elif self.current_animation == 'hurt':
                self.current_animation = 'hurt'
            elif self.current_animation == 'attack':
                self.current_animation = 'attack'
        
        # Prioridad 2: Ataque (Si no está en un estado forzado como 'hurt' o 'dead')
        elif keys[pygame.K_z] or keys[pygame.K_k]: 
            if self.current_animation != 'attack':
                self.current_animation = 'attack'
                self.animation_frame_float = 0.0 # Reiniciar frame float
                self.animation_timer = 0
                self.is_animation_overriding = True
            
        # Prioridad 3: Salto/Caída
        elif not self.on_ground:
            if self.vel.y < 0:
                self.current_animation = 'jump'
            else:
                self.current_animation = 'fall'
        
        # Prioridad 4: En el suelo (Idle o Run)
        else:
            self.current_animation = 'run' if abs(self.vel.x) > 0.1 else 'idle'
            
        # --- FIN LÓGICA DE ESTADO ---
            
        # Gravedad, Salto y Doble Salto 
        if self.current_animation not in ['attack', 'hurt']:
            if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
                if self.on_ground:
                    self.vel.y = PLAYER_JUMP
                    self.on_ground = False
                    self.can_double_jump = True
                    self.animation_frame_float = 0.0  # Resetear frame de salto
                elif self.can_double_jump:
                    self.vel.y = PLAYER_DOUBLE_JUMP
                    self.can_double_jump = False
                    self.animation_frame_float = 0.0

        self.vel.y += GRAVITY
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        
        # Colisión con suelo (Manejo de suelo simple)
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel.y = 0
            if not self.on_ground: # Solo si acaba de tocar el suelo
                 self.animation_frame_float = 0.0
            self.on_ground = True
            self.can_double_jump = True
            
        # Mantener en pantalla
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > 1280: self.rect.right = 1280
        
        # --- ACTUALIZACIÓN DE ANIMACIÓN (Corregido para suavizar el ciclo) ---

        # 1. Determinar la velocidad de animación específica para el estado
        animation_speed_factor = self.animation_speed
        if self.current_animation == 'run':
             # CORRECCIÓN: Velocidad de correr un poco más rápida para la fluidez
             animation_speed_factor = 0.12 

        current_frames = self.animations.get(self.current_animation, [])
        frame_count = len(current_frames)
        
        if frame_count > 0:
             # CORRECCIÓN CLAVE: Aumentar el contador float usando dt y el factor de velocidad
             self.animation_frame_float += (dt / animation_speed_factor)
             
             # 2. Lógica para animaciones de UN SOLO CICLO (Attack, Hurt, Dead)
             if self.current_animation in ['attack', 'hurt', 'dead']:
                 if self.animation_frame_float >= frame_count:
                     # Limitar al último frame y desactivar override si es Attack/Hurt
                     self.animation_frame_float = frame_count - 0.001 # Asegura que el índice entero sea el último
                     if self.current_animation in ['attack', 'hurt']:
                         self.is_animation_overriding = False 
             
             # 3. Lógica para animaciones de CICLO CONTINUO (Idle, Run, Jump, Fall)
             else:
                 # El operador módulo garantiza que el frame index vuelva a 0 perfectamente
                 self.animation_frame_float %= frame_count


        # Resetear frame float si cambió la animación
        if previous_animation != self.current_animation:
             self.animation_frame_float = 0.0
             self.animation_timer = 0 # No es estrictamente necesario, pero se mantiene por seguridad

        # Actualizar invulnerabilidad y power-ups (no modificados)
        if self.invulnerable:
            self.invuln_timer += dt
            if self.invuln_timer >= self.invuln_duration:
                self.invulnerable = False
                self.invuln_timer = 0
            self.flash_timer += 0.1
        
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
    
    def _update_sprite(self):
        """Actualiza el sprite actual"""
        # ... (código no modificado)
        if self.use_procedural:
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            if not self.on_ground:
                self._draw_procedural_jump()
            else:
                bounce = abs(math.sin(self.animation_time * 10)) * 3
                self._draw_procedural_running(bounce)
        else:
            current_frames = self.animations.get(self.current_animation, [])
            
            if current_frames:
                # OBTENER ÍNDICE ENTERO DEL FLOAT
                frame_index = int(self.animation_frame_float)
                # Asegurar que el índice esté dentro del rango (debe estarlo gracias al módulo/cap)
                frame_index = frame_index % len(current_frames) 
                
                sprite = current_frames[frame_index]
                
                # Crear superficie del tamaño completo del jugador
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                
                # Centrar el sprite en la superficie
                sprite_rect = sprite.get_rect(center=(self.width // 2, self.height // 2))
                
                # Voltear si mira a la izquierda
                if not self.facing_right:
                    sprite = pygame.transform.flip(sprite, True, False)
                
                self.image.blit(sprite, sprite_rect)
            else:
                # Fallback si no hay frames
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                self._draw_procedural_fallback()
    
    def take_damage(self):
        """
        Recibe daño y activa invulnerabilidad
        """
        if self.invulnerable or self.invincible_active:
            return False
        
        self.invulnerable = True
        self.invuln_timer = 0
        
        # Pequeño impulso hacia arriba
        if self.on_ground:
            self.vel.y = PLAYER_JUMP * 0.5
        
        # Lógica para cambiar a animación 'hurt'
        self.current_animation = 'hurt'
        self.animation_frame_float = 0.0 # Resetear frame float
        self.animation_timer = 0
        self.is_animation_overriding = True # Nueva bandera para forzar la animación
        
        return True
    
    # ... (Resto de funciones draw, powerups, y procedurales no modificadas)
    def activate_powerup(self, powerup_type):
        """Activa un power-up (no modificado)"""
        if powerup_type == 'shield':
            self.shield_active = True
            self.shield_timer = 0
        elif powerup_type == 'invincible':
            self.invincible_active = True
            self.invincible_timer = 0
        elif powerup_type == 'slow':
            pass 

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
            
            pulse = abs(math.sin(pygame.time.get_ticks() / 200)) * 0.3 + 0.7
            alpha = int(120 * pulse)
            
            # Círculo de escudo hexagonal
            for i in range(6):
                angle = (pygame.time.get_ticks() / 20 + i * 60) % 360
                x1 = shield_radius + int(shield_radius * math.cos(math.radians(angle)))
                y1 = shield_radius + int(shield_radius * math.sin(math.radians(angle)))
                x2 = shield_radius + int(shield_radius * math.cos(math.radians(angle + 60)))
                y2 = shield_radius + int(shield_radius * math.sin(math.radians(angle + 60)))
                pygame.draw.line(shield_surf, (100, 200, 255, alpha), (x1, y1), (x2, y2), 3)
            
            screen.blit(shield_surf, (self.rect.centerx - shield_radius, self.rect.centery - shield_radius))
        
        # Efecto de invencibilidad
        if self.invincible_active:
            for i in range(3):
                star_size = 8
                angle = (pygame.time.get_ticks() / 10 + i * 120) % 360
                distance = 35
                x = int(self.rect.centerx + distance * math.cos(math.radians(angle)))
                y = int(self.rect.centery + distance * math.sin(math.radians(angle)))
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