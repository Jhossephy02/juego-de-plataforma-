import pygame,os
from src.settings import WIDTH,HEIGHT,FPS
from src.entities.player import Player
from src.world.parallax import Parallax
class Game:
 def __init__(self,screen,clock): self.screen=screen;self.clock=clock;base=os.path.dirname(os.path.dirname(__file__))
 layers=[('sky','sky.png',0.01),('mountains','mountains.png',0.03),('mid','mid1.png',0.05),('mid','mid2.png',0.07),('foreground','fg1.png',0.1),('foreground','fg2.png',0.13)]
 self.layers=[Parallax(base,f,l,s) for f,l,s in layers]
 self.player=Player((200,300));self.gy=HEIGHT-80
 def run(self):
  while True:
   dt=self.clock.get_time()
   e=pygame.event.get()
   for ev in e:
    if ev.type==pygame.QUIT or (ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE): return
   keys=pygame.key.get_pressed(); self.player.update(keys,self.gy)
   for ly in self.layers: ly.update(dt)
   self.screen.fill((0,0,0))
   for ly in self.layers: ly.draw(self.screen)
   pygame.draw.rect(self.screen,(80,60,40),(0,self.gy,WIDTH,HEIGHT-self.gy))
   self.screen.blit(self.player.image,self.player.rect)
   pygame.display.flip(); self.clock.tick(FPS)