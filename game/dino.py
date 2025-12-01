"""Classe do dinossauro"""
import pygame
from game.config import *

class Dino:
    def __init__(self):
        self.x = DINO_X
        self.y = GROUND_Y
        self.width = 40
        self.height = 50
        self.velocity_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.fitness = 0
        self.alive = True
        
    def jump(self):
        """Faz o dinossauro pular"""
        if not self.is_jumping and not self.is_ducking:
            self.velocity_y = JUMP_VELOCITY
            self.is_jumping = True
            
    def duck(self):
        """Faz o dinossauro abaixar"""
        if not self.is_jumping:
            self.is_ducking = True
            self.height = 30
            self.y = GROUND_Y + 20
            
    def stand(self):
        """Volta à posição normal"""
        self.is_ducking = False
        self.height = 50
        self.y = GROUND_Y
        
    def update(self):
        """Atualiza física do dinossauro"""
        if self.is_jumping:
            self.velocity_y += GRAVITY
            self.y += self.velocity_y
            
            if self.y >= GROUND_Y:
                self.y = GROUND_Y
                self.velocity_y = 0
                self.is_jumping = False
                
        self.fitness += 1
        
    def get_rect(self):
        """Retorna o retângulo de colisão"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        """Desenha o dinossauro"""
        color = GREEN if self.alive else RED
        pygame.draw.rect(screen, color, self.get_rect())
