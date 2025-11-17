import pygame
from src.settings import WIDTH,HEIGHT
class Button:
 def __init__(self,r,t,f,bc,hc): self.rect=pygame.Rect(r);self.text=t;self.font=f;self.bc=bc;self.hc=hc
 def draw(self,s):
  m=pygame.mouse.get_pos();c=self.hc if self.rect.collidepoint(m) else self.bc
  pygame.draw.rect(s,c,self.rect,border_radius=12)
  txt=self.font.render(self.text,True,(0,0,0));s.blit(txt,txt.get_rect(center=self.rect.center))
 def clicked(self,e): m=pygame.mouse.get_pos();return any(ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1 and self.rect.collidepoint(m) for ev in e)

def run_menu(screen,clock):
 f=pygame.font.SysFont('arial',48,True);b=pygame.font.SysFont('arial',32,True)
 play=Button((WIDTH//2-100,HEIGHT//2-20,200,50),'JUGAR',b,(255,255,255),(200,230,255))
 quit=Button((WIDTH//2-100,HEIGHT//2+60,200,50),'SALIR',b,(255,255,255),(255,200,200))
 while True:
  e=pygame.event.get()
  for ev in e:
   if ev.type==pygame.QUIT: return 'quit'
  if play.clicked(e): return 'play'
  if quit.clicked(e): return 'quit'
  screen.fill((50,60,120))
  t=f.render('Rayman Shinobi',True,(255,255,255));screen.blit(t,t.get_rect(center=(WIDTH//2,HEIGHT//2-120)))
  play.draw(screen);quit.draw(screen)
  pygame.display.flip();clock.tick(60)