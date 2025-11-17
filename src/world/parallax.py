import pygame,os
class Parallax:
 def __init__(self,base,folder,file,speed):
  self.img=pygame.image.load(os.path.join(base,'assets','world','layers',folder,file)).convert_alpha();self.speed=speed;self.x=0
 def update(self,dt): self.x-=self.speed*dt; w=self.img.get_width();
  if self.x<=-w: self.x=0
 def draw(self,sc): sc.blit(self.img,(self.x,0));sc.blit(self.img,(self.x+self.img.get_width(),0))