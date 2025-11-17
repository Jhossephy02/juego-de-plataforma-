import pygame
from src.settings import GRAVITY
class Player(pygame.sprite.Sprite):
 def __init__(self,pos): super().__init__();self.image=pygame.image.load('assets/player/idle/Idle.png');self.rect=self.image.get_rect(topleft=pos);self.vel=pygame.math.Vector2(0,0);self.speed=5;self.on_ground=False
 def update(self,keys,gy):
  self.vel.x=0
  if keys[pygame.K_LEFT]: self.vel.x=-self.speed
  if keys[pygame.K_RIGHT]: self.vel.x=self.speed
  if keys[pygame.K_SPACE] and self.on_ground: self.vel.y=-12;self.on_ground=False
  self.vel.y+=GRAVITY
  self.rect.x+=self.vel.x; self.rect.y+=self.vel.y
  if self.rect.bottom>=gy: self.rect.bottom=gy;self.vel.y=0;self.on_ground=True