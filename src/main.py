import pygame
from src.settings import WIDTH,HEIGHT
from src.game import Game
from src.ui.menu import run_menu

def main():
 pygame.init();screen=pygame.display.set_mode((WIDTH,HEIGHT));clock=pygame.time.Clock()
 while True:
  act=run_menu(screen,clock)
  if act=='quit': break
  Game(screen,clock).run()
 pygame.quit()

if __name__=='__main__': main()