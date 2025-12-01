"""Motor principal do jogo"""
import random
from game.config import *
from game.dino import Dino
from game.obstacle import Obstacle

class GameEngine:
    def __init__(self):
        self.reset()
        
    def reset(self):
        """Reseta o estado do jogo"""
        self.speed = INITIAL_SPEED
        self.obstacles = []
        self.distance_to_next_obstacle = random.randint(300, 500)
        self.score = 0
        
    def update(self):
        """Atualiza o estado do jogo"""
        # Incrementa velocidade gradualmente
        self.speed = min(self.speed + SPEED_INCREMENT, MAX_SPEED)
        self.score += 1
        
        # Atualiza obstáculos existentes
        for obstacle in self.obstacles:
            obstacle.update(self.speed)
            
        # Remove obstáculos que saíram da tela
        self.obstacles = [obs for obs in self.obstacles if not obs.is_off_screen()]
        
        # Adiciona novos obstáculos
        self.distance_to_next_obstacle -= self.speed
        if self.distance_to_next_obstacle <= 0:
            self.obstacles.append(Obstacle(SCREEN_WIDTH))
            self.distance_to_next_obstacle = random.randint(OBSTACLE_MIN_GAP, OBSTACLE_MAX_GAP)
            
    def check_collision(self, dino):
        """Verifica colisão entre dinossauro e obstáculos"""
        dino_rect = dino.get_rect()
        for obstacle in self.obstacles:
            if dino_rect.colliderect(obstacle.get_rect()):
                return True
        return False
        
    def get_next_obstacle(self):
        """Retorna o próximo obstáculo relevante"""
        for obstacle in self.obstacles:
            if obstacle.x + obstacle.width > DINO_X:
                return obstacle
        return None
