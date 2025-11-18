# src/ui/leaderboard.py - Sistema de puntuaciones altas

import pygame
import json
from pathlib import Path
from datetime import datetime

class Leaderboard:
    """Sistema de tabla de puntuaciones"""
    
    def __init__(self, max_entries=10):
        self.max_entries = max_entries
        self.scores_file = Path('data/scores.json')
        self.scores_file.parent.mkdir(parents=True, exist_ok=True)
        self.scores = self._load_scores()
    
    def _load_scores(self):
        """Carga puntuaciones del archivo"""
        if not self.scores_file.exists():
            return []
        
        try:
            with open(self.scores_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_scores(self):
        """Guarda puntuaciones al archivo"""
        with open(self.scores_file, 'w') as f:
            json.dump(self.scores, f, indent=2)
    
    def add_score(self, player_name, score, difficulty, combo, perfect_dodges, song_name):
        """Agrega una nueva puntuación"""
        entry = {
            'name': player_name,
            'score': score,
            'difficulty': difficulty,
            'combo': combo,
            'perfect_dodges': perfect_dodges,
            'song': song_name,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:self.max_entries]
        self._save_scores()
        
        # Retornar posición
        return self.scores.index(entry) + 1 if entry in self.scores else None
    
    def is_high_score(self, score):
        """Verifica si es puntuación alta"""
        if len(self.scores) < self.max_entries:
            return True
        return score > self.scores[-1]['score']
    
    def get_scores(self, difficulty=None):
        """Obtiene puntuaciones, opcionalmente filtradas por dificultad"""
        if difficulty:
            return [s for s in self.scores if s['difficulty'] == difficulty]
        return self.scores

class LeaderboardScreen:
    """Pantalla de visualización del leaderboard"""
    
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.leaderboard = Leaderboard()
        
        # Fuentes
        self.font_title = pygame.font.SysFont('arial', 64, bold=True)
        self.font_header = pygame.font.SysFont('arial', 24, bold=True)
        self.font_entry = pygame.font.SysFont('arial', 20)
        self.font_small = pygame.font.SysFont('arial', 16)
    
    def show(self, new_score=None, player_name="Player"):
        """Muestra el leaderboard"""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        return 'menu'
            
            self._draw(new_score, player_name)
            pygame.display.flip()
    
    def _draw(self, new_score, player_name):
        """Dibuja el leaderboard"""
        from src.settings import WIDTH, HEIGHT
        
        # Fondo
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(20 + ratio * 30)
            g = int(30 + ratio * 40)
            b = int(70 + ratio * 50)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        
        # Título
        title = self.font_title.render("🏆 TOP SCORES 🏆", True, (255, 215, 0))
        title_rect = title.get_rect(center=(WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Headers
        headers = ["#", "Nombre", "Score", "Dificultad", "Combo", "Fecha"]
        x_positions = [150, 250, 450, 600, 750, 900]
        
        y_pos = 180
        for i, header in enumerate(headers):
            text = self.font_header.render(header, True, (200, 200, 200))
            self.screen.blit(text, (x_positions[i], y_pos))
        
        # Línea separadora
        pygame.draw.line(self.screen, (100, 100, 100), 
                        (130, y_pos + 35), (WIDTH - 130, y_pos + 35), 2)
        
        # Entradas
        y_pos = 230
        scores = self.leaderboard.get_scores()
        
        for i, entry in enumerate(scores[:10]):
            # Fondo alternado
            if i % 2 == 0:
                pygame.draw.rect(self.screen, (40, 50, 80), 
                               (130, y_pos - 5, WIDTH - 260, 40), border_radius=5)
            
            # Highlight si es nueva puntuación
            is_new = (new_score and entry['score'] == new_score['score'] and 
                     entry['name'] == player_name)
            color = (255, 255, 100) if is_new else (255, 255, 255)
            
            # Posición
            pos_text = self.font_entry.render(f"{i+1}.", True, color)
            self.screen.blit(pos_text, (x_positions[0], y_pos))
            
            # Nombre
            name_text = self.font_entry.render(entry['name'][:15], True, color)
            self.screen.blit(name_text, (x_positions[1], y_pos))
            
            # Score
            score_text = self.font_entry.render(f"{entry['score']:,}", True, color)
            self.screen.blit(score_text, (x_positions[2], y_pos))
            
            # Dificultad
            diff_colors = {
                'easy': (100, 255, 100),
                'normal': (100, 200, 255),
                'hard': (255, 150, 50),
                'insane': (255, 50, 50)
            }
            diff_color = diff_colors.get(entry['difficulty'], (255, 255, 255))
            diff_text = self.font_entry.render(entry['difficulty'].title(), True, diff_color)
            self.screen.blit(diff_text, (x_positions[3], y_pos))
            
            # Combo
            combo_text = self.font_entry.render(f"x{entry['combo']}", True, color)
            self.screen.blit(combo_text, (x_positions[4], y_pos))
            
            # Fecha
            date_text = self.font_small.render(entry['date'], True, (180, 180, 180))
            self.screen.blit(date_text, (x_positions[5], y_pos + 2))
            
            y_pos += 45
        
        # Mensaje si no hay puntuaciones
        if not scores:
            no_scores = self.font_entry.render("No hay puntuaciones aún. ¡Sé el primero!", 
                                              True, (200, 200, 200))
            no_scores_rect = no_scores.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(no_scores, no_scores_rect)
        
        # Instrucción
        instruction = self.font_small.render("Presiona ESC o ENTER para volver", 
                                            True, (150, 150, 150))
        instruction_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        self.screen.blit(instruction, instruction_rect)