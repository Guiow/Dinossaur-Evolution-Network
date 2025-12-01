"""Classe de obstáculos"""
import pygame
import random
from game.config import *

class Obstacle:
    def __init__(self, x):
        self.x = x
        cactus = random.choice(CACTUS_TYPES)
        self.width = cactus[0]
        self.height = cactus[1]
        self.y = GROUND_Y + 50 - self.height
        
    def update(self, speed):
        """Move o obstáculo para a esquerda"""
        self.x -= speed
        
    def is_off_screen(self):
        """Verifica se saiu da tela"""
        return self.x + self.width < 0
        
    def get_rect(self):
        """Retorna o retângulo de colisão"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        """Desenha o obstáculo"""
        pygame.draw.rect(screen, RED, self.get_rect())
