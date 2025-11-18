# src/main.py - Punto de entrada principal corregido

import pygame
import sys
from src.settings import WIDTH, HEIGHT, TITLE, FPS
from src.ui.menu import run_menu
from src.ui.music_selector import MusicSelector
from src.ui.difficulty_selector import DifficultySelector
from src.game import Game

class GameApplication:
    """Aplicación principal del juego"""
    
    def __init__(self):
        # Inicializar Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Configurar ventana
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        
        # Cargar icono (si existe)
        try:
            icon = pygame.image.load('assets/icon.png')
            pygame.display.set_icon(icon)
        except:
            pass
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        
        # Estado
        self.running = True
        self.current_music = None
        self.current_difficulty = 'normal'
        
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
   ✓ Efectos visuales y partículas
   ✓ Sistema de combo y puntuación
   ✓ Soporte para múltiples formatos de audio

🎮 Controles:
   • ESPACIO / ↑ / W : Saltar (doble salto disponible)
   • ESC : Pausar / Volver al menú
   • R : Reiniciar (en Game Over)

🎵 Para empezar:
   1. Coloca archivos de música en la carpeta 'assets/music/'
   2. O carga un archivo desde el selector
   3. ¡Disfruta del ritmo!

""")
    
    def run(self):
        """Loop principal de la aplicación"""
        while self.running:
            # Mostrar menú principal
            action = run_menu(self.screen, self.clock)
            
            if action == 'quit':
                self.running = False
                break
            
            elif action == 'play':
                # Mostrar selector de música
                music_selector = MusicSelector(self.screen, self.clock)
                selected_music, next_action = music_selector.run()
                
                if next_action == 'quit':
                    self.running = False
                    break
                
                elif next_action == 'play' and selected_music:
                    # Mostrar selector de dificultad
                    difficulty_selector = DifficultySelector(self.screen, self.clock)
                    selected_difficulty = difficulty_selector.run()
                    
                    if selected_difficulty:
                        self.current_music = selected_music
                        self.current_difficulty = selected_difficulty
                        self.play_game()
    
    def play_game(self):
        """Inicia una sesión de juego"""
        if not self.current_music:
            print("❌ No hay música seleccionada")
            return
        
        # Crear y ejecutar el juego
        game = Game(
            self.screen, 
            self.clock, 
            self.current_music, 
            self.current_difficulty
        )
        result = game.run()
        
        # Procesar resultado
        if result == 'restart':
            # Reiniciar con la misma música y dificultad
            self.play_game()
        elif result == 'quit':
            self.running = False
        # Si es 'menu', volver al menú principal
    
    def cleanup(self):
        """Limpia recursos antes de salir"""
        pygame.mixer.quit()
        pygame.quit()
        print("\n👋 ¡Gracias por jugar!\n")

def main():
    """Función principal"""
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
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main()