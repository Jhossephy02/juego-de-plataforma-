# src/world/parallax.py - Sistema de parallax para fondo animado

import pygame
import os

class Parallax:
    """Capa de parallax para fondos con efecto de profundidad"""
    
    def __init__(self, base, folder, file, speed):
        """
        Inicializa una capa de parallax
        
        Args:
            base: Ruta base del proyecto
            folder: Carpeta de la capa (sky, mountains, etc)
            file: Nombre del archivo de imagen
            speed: Velocidad de desplazamiento (menor = más lento)
        """
        # Cargar imagen
        image_path = os.path.join(base, 'assets', 'world', 'layers', folder, file)
        
        try:
            self.img = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            # Crear imagen placeholder si no existe
            print(f"⚠️ Imagen no encontrada: {image_path}")
            self.img = self._create_placeholder(folder)
        
        self.speed = speed
        self.x = 0
    
    def _create_placeholder(self, folder):
        """Crea una imagen placeholder según el tipo de capa"""
        width = 1280
        height = 720
        
        # Colores según el tipo de capa
        colors = {
            'sky': (100, 150, 200),
            'mountains': (80, 100, 120),
            'mid': (60, 80, 100),
            'foreground': (40, 60, 80)
        }
        
        color = colors.get(folder, (100, 100, 100))
        
        # Crear superficie
        surface = pygame.Surface((width, height))
        surface.fill(color)
        
        # Agregar algún detalle visual
        for i in range(0, width, 100):
            lighter = tuple(min(c + 20, 255) for c in color)
            pygame.draw.rect(surface, lighter, (i, 0, 50, height))
        
        return surface
    
    def update(self, dt):
        """
        Actualiza la posición de la capa
        
        Args:
            dt: Delta time en milisegundos
        """
        self.x -= self.speed * dt
        
        # Resetear posición cuando sale de pantalla
        w = self.img.get_width()
        if self.x <= -w:
            self.x = 0
    
    def draw(self, screen):
        """
        Dibuja la capa de parallax con repetición
        
        Args:
            screen: Surface de pygame donde dibujar
        """
        # Dibujar primera imagen
        screen.blit(self.img, (self.x, 0))
        
        # Dibujar segunda imagen para seamless loop
        screen.blit(self.img, (self.x + self.img.get_width(), 0))