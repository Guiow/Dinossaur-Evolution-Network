"""Motor do jogo"""
import random
from game.config import *

class GameEngine:
    """Motor principal do jogo"""
    
    def __init__(self):
        """Inicializa motor do jogo"""
        from game.obstacle import Obstacle
        self.Obstacle = Obstacle
        
        self.obstacles = []
        self.score = 0
        self.speed = INITIAL_SPEED
        self.distance_since_last_obstacle = 0
        # Distância inicial maior para dar tempo de começar
        self.next_obstacle_distance = 400
        
    def reset(self):
        """Reinicia o jogo"""
        self.obstacles = []
        self.score = 0
        self.speed = INITIAL_SPEED
        self.distance_since_last_obstacle = 0
        self.next_obstacle_distance = 400
        
    def update(self):
        """Atualiza estado do jogo"""
        # Atualiza velocidade gradualmente
        if self.speed < MAX_SPEED:
            self.speed += SPEED_INCREMENT
            
        # Atualiza score
        self.score += 1
        
        # Atualiza obstáculos existentes
        for obstacle in self.obstacles:
            obstacle.update(self.speed)
            
        # Remove obstáculos fora da tela
        self.obstacles = [obs for obs in self.obstacles if not obs.off_screen()]
        
        # Cria novos obstáculos
        self.distance_since_last_obstacle += self.speed
        
        if self.distance_since_last_obstacle >= self.next_obstacle_distance:
            # TAMANHOS ORIGINAIS DOS RETÂNGULOS VERMELHOS
            height = random.randint(40, 70)  # Altura original: 40-70
            width = random.randint(20, 35)   # Largura original: 20-35
            obstacle = self.Obstacle(SCREEN_WIDTH + 50, height, width)
            self.obstacles.append(obstacle)
            
            self.distance_since_last_obstacle = 0
            # FREQUÊNCIA ORIGINAL: 250-450 pixels entre obstáculos
            self.next_obstacle_distance = random.randint(250, 450)
            
    def get_next_obstacle(self):
        """Retorna o próximo obstáculo mais próximo"""
        if not self.obstacles:
            return None
            
        # Obstáculos à frente do dinossauro
        ahead_obstacles = [obs for obs in self.obstacles if obs.x > 50]
        
        if not ahead_obstacles:
            return None
            
        return min(ahead_obstacles, key=lambda obs: obs.x)
        
    def check_collision(self, dino):
        """Verifica colisão com dinossauro"""
        dino_rect = dino.get_rect()
        
        for obstacle in self.obstacles:
            obstacle_rect = obstacle.get_rect()
            
            if dino_rect.colliderect(obstacle_rect):
                return True
                
        return False
