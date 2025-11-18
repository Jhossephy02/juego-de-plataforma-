# src/main.py - Sistema principal mejorado con todas las integraciones

import pygame
import sys
import os
from src.settings import WIDTH, HEIGHT, TITLE, FPS
from src.ui.menu import run_menu
from src.ui.music_selector import MusicSelector
from src.ui.difficulty_selector import DifficultySelector
from src.ui.leaderboard import LeaderboardScreen
from src.game import Game

class GameApplication:
    """Aplicación principal del juego con sistema completo de features"""
    
    def __init__(self):
        # Inicializar Pygame
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Configurar ventana
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        
        # Cargar icono
        self._load_icon()
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        
        # Estado
        self.running = True
        self.current_music = None
        self.current_difficulty = 'normal'
        
        # Sistema de leaderboard
        self.leaderboard = LeaderboardScreen(self.screen, self.clock)
        
        # Música de fondo del menú
        self.menu_music_playing = False
        self._setup_menu_music()
        
        # Estadísticas de sesión
        self.session_stats = {
            'games_played': 0,
            'total_score': 0,
            'best_score': 0,
            'total_time': 0
        }
        
        self._print_welcome()
    
    def _load_icon(self):
        """Carga el icono de la aplicación"""
        icon_path = os.path.join('assets', 'ui', 'icon.png')
        if os.path.exists(icon_path):
            try:
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
            except:
                pass
    
    def _setup_menu_music(self):
        """Configura música de fondo para los menús"""
        menu_music_path = os.path.join('assets', 'music', 'menu_theme.mp3')
        
        # Si no existe, usar la primera canción disponible
        if not os.path.exists(menu_music_path):
            music_dir = os.path.join('assets', 'music')
            if os.path.exists(music_dir):
                music_files = [f for f in os.listdir(music_dir) 
                              if f.lower().endswith(('.mp3', '.ogg', '.wav'))]
                if music_files:
                    menu_music_path = os.path.join(music_dir, music_files[0])
        
        if os.path.exists(menu_music_path):
            try:
                pygame.mixer.music.load(menu_music_path)
                pygame.mixer.music.set_volume(0.3)
                self.menu_music_path = menu_music_path
            except Exception as e:
                print(f"⚠️ No se pudo cargar música de menú: {e}")
                self.menu_music_path = None
        else:
            self.menu_music_path = None
    
    def _play_menu_music(self):
        """Inicia música de fondo del menú"""
        if self.menu_music_path and not self.menu_music_playing:
            try:
                pygame.mixer.music.load(self.menu_music_path)
                pygame.mixer.music.play(-1, fade_ms=1000)
                pygame.mixer.music.set_volume(0.3)
                self.menu_music_playing = True
            except:
                pass
    
    def _stop_menu_music(self):
        """Detiene música de fondo del menú"""
        if self.menu_music_playing:
            pygame.mixer.music.fadeout(1000)
            self.menu_music_playing = False
    
    def _print_welcome(self):
        """Imprime mensaje de bienvenida"""
        print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           🎮 RAYMAN SHINOBI - MUSIC RUNNER 🎵             ║
║                                                            ║
║                  Versión 1.0 - 2024                       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

🎯 Características:
   ✓ Generación de obstáculos basada en análisis musical
   ✓ Detección automática de beats y tempo
   ✓ Sistema de dificultad adaptativa
   ✓ Efectos visuales y partículas avanzadas
   ✓ Sistema de combo y puntuación
   ✓ Tabla de puntuaciones (Leaderboard)
   ✓ Sistema de caché para carga rápida
   ✓ Soporte para múltiples formatos de audio

🎮 Controles:
   • ESPACIO / ↑ / W : Saltar (doble salto disponible)
   • Z / K : Ataque especial (daña obstáculos cercanos)
   • SHIFT : Activar cámara lenta (cooldown)
   • ESC : Pausar / Volver al menú
   • R : Reiniciar (en Game Over)

🎵 Para empezar:
   1. Coloca archivos de música en 'assets/music/'
   2. O carga un archivo desde el selector
   3. Selecciona dificultad
   4. ¡Disfruta del ritmo!

💡 Tips:
   • Las esquivas perfectas (muy cerca) dan doble puntos
   • Los combos altos multiplican tu puntuación
   • Usa power-ups estratégicamente
   • El ataque puede destruir obstáculos pequeños

""")
    
    def run(self):
        """Loop principal de la aplicación"""
        while self.running:
            # Reproducir música de menú
            self._play_menu_music()
            
            # Mostrar menú principal
            action = run_menu(self.screen, self.clock)
            
            if action == 'quit':
                self.running = False
                break
            
            elif action == 'play':
                self._stop_menu_music()
                self._start_game_flow()
            
            elif action == 'leaderboard':
                self._show_leaderboard()
            
            elif action == 'options':
                self._show_options()
        
        self._print_session_stats()
    
    def _start_game_flow(self):
        """Flujo completo de inicio de juego"""
        # Mostrar selector de música
        music_selector = MusicSelector(self.screen, self.clock)
        selected_music, next_action = music_selector.run()
        
        if next_action == 'quit':
            self.running = False
            return
        
        elif next_action == 'menu':
            return
        
        elif next_action == 'play' and selected_music:
            # Mostrar selector de dificultad
            difficulty_selector = DifficultySelector(self.screen, self.clock)
            selected_difficulty = difficulty_selector.run()
            
            if selected_difficulty:
                self.current_music = selected_music
                self.current_difficulty = selected_difficulty
                
                # Iniciar juego
                game_result = self.play_game()
                
                # Procesar resultado
                if game_result and game_result != 'quit':
                    self._process_game_result(game_result)
    
    def play_game(self):
        """Inicia una sesión de juego"""
        if not self.current_music:
            print("❌ No hay música seleccionada")
            return None
        
        # Crear y ejecutar el juego
        game = Game(
            self.screen, 
            self.clock, 
            self.current_music, 
            self.current_difficulty
        )
        
        result = game.run()
        
        # Actualizar estadísticas de sesión
        if result and isinstance(result, dict):
            self.session_stats['games_played'] += 1
            self.session_stats['total_score'] += result.get('score', 0)
            self.session_stats['best_score'] = max(
                self.session_stats['best_score'],
                result.get('score', 0)
            )
            self.session_stats['total_time'] += result.get('time', 0)
        
        # Procesar comandos especiales
        if result == 'restart':
            return self.play_game()
        elif result == 'quit':
            self.running = False
            return 'quit'
        
        return result
    
    def _process_game_result(self, result):
        """Procesa resultados del juego y actualiza leaderboard"""
        if not isinstance(result, dict):
            return
        
        score = result.get('score', 0)
        combo = result.get('max_combo', 0)
        perfect_dodges = result.get('perfect_dodges', 0)
        
        # Verificar si es high score
        if self.leaderboard.leaderboard.is_high_score(score):
            print(f"\n🎉 ¡NUEVO HIGH SCORE! {score} puntos")
            
            # Obtener nombre del jugador
            player_name = self._get_player_name()
            
            # Agregar a leaderboard
            song_name = os.path.basename(self.current_music)
            position = self.leaderboard.leaderboard.add_score(
                player_name,
                score,
                self.current_difficulty,
                combo,
                perfect_dodges,
                song_name
            )
            
            if position:
                print(f"🏆 Posición en el ranking: #{position}")
            
            # Mostrar leaderboard
            self._show_leaderboard(
                new_score=result,
                player_name=player_name
            )
    
    def _get_player_name(self):
        """Obtiene nombre del jugador mediante input visual"""
        # Por simplicidad, usar nombre por defecto
        # En una versión completa, implementar input de texto en pantalla
        return "Player"
    
    def _show_leaderboard(self, new_score=None, player_name="Player"):
        """Muestra la tabla de puntuaciones"""
        self.leaderboard.show(new_score, player_name)
    
    def _show_options(self):
        """Muestra pantalla de opciones (placeholder)"""
        # TODO: Implementar pantalla de opciones completa
        print("⚙️ Opciones (en desarrollo)")
    
    def _print_session_stats(self):
        """Imprime estadísticas de la sesión"""
        if self.session_stats['games_played'] > 0:
            avg_score = self.session_stats['total_score'] / self.session_stats['games_played']
            
            print(f"""
╔════════════════════════════════════════════════════════════╗
║              ESTADÍSTICAS DE LA SESIÓN                     ║
╠════════════════════════════════════════════════════════════╣
║  Partidas jugadas: {self.session_stats['games_played']}
║  Puntuación total: {self.session_stats['total_score']:,}
║  Mejor puntuación: {self.session_stats['best_score']:,}
║  Promedio: {avg_score:,.0f}
║  Tiempo total: {self.session_stats['total_time']:.1f}s
╚════════════════════════════════════════════════════════════╝
""")
    
    def cleanup(self):
        """Limpia recursos antes de salir"""
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.quit()
        print("\n👋 ¡Gracias por jugar Rayman Shinobi!\n")

def main():
    """Función principal con manejo de errores"""
    try:
        app = GameApplication()
        app.run()
        app.cleanup()
    except KeyboardInterrupt:
        print("\n⚠️ Juego interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            pygame.quit()
        except:
            pass
        sys.exit()

if __name__ == '__main__':
    main()