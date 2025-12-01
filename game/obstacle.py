"""Obstáculo do jogo - Cacto"""
import pygame
from game.config import GROUND_Y

class Obstacle:
    """Obstáculo em forma de cacto que o dinossauro deve evitar"""
    
    def __init__(self, x, height, width):
        """Inicializa obstáculo com posição e dimensões"""
        self.x = x
        self.height = height
        self.width = width
        self.y = GROUND_Y + 50 - height  # Posicionado no chão
        self.speed = 0
        
        # Cores do cacto
        self.color_green = (60, 140, 60)      # Verde principal
        self.color_dark = (40, 100, 40)       # Verde escuro
        self.color_light = (80, 160, 80)      # Verde claro (detalhes)
        
    def get_rect(self):
        """Retorna hitbox retangular para colisão"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self, game_speed):
        """Atualiza posição do obstáculo"""
        self.x -= game_speed
        
    def draw(self, surface):
        """Desenha cacto (visual) - hitbox permanece retangular"""
        x, y = self.x, self.y
        w, h = self.width, self.height
        
        # === CORPO PRINCIPAL DO CACTO (tronco vertical) ===
        trunk_width = int(w * 0.6)
        trunk_x = x + (w - trunk_width) // 2
        trunk = pygame.Rect(trunk_x, y, trunk_width, h)
        pygame.draw.rect(surface, self.color_green, trunk, border_radius=3)
        
        # Listras verticais no tronco (detalhes)
        stripe_x = trunk_x + trunk_width // 3
        pygame.draw.line(surface, self.color_dark, 
                        (stripe_x, y + 2), (stripe_x, y + h - 2), 1)
        stripe_x2 = trunk_x + 2 * trunk_width // 3
        pygame.draw.line(surface, self.color_dark, 
                        (stripe_x2, y + 2), (stripe_x2, y + h - 2), 1)
        
        # === BRAÇOS DO CACTO (se for alto o suficiente) ===
        if h > 30:
            # Braço esquerdo (terço superior)
            arm_left_height = int(h * 0.25)
            arm_left_y = y + int(h * 0.3)
            arm_left_width = int(w * 0.4)
            
            # Parte horizontal do braço esquerdo
            arm_left_h = pygame.Rect(trunk_x - arm_left_width + 4, 
                                     arm_left_y + arm_left_height - 6, 
                                     arm_left_width, 6)
            pygame.draw.rect(surface, self.color_green, arm_left_h, border_radius=2)
            
            # Parte vertical do braço esquerdo (dobra para cima)
            arm_left_v = pygame.Rect(trunk_x - arm_left_width + 4, 
                                     arm_left_y, 
                                     6, arm_left_height)
            pygame.draw.rect(surface, self.color_green, arm_left_v, border_radius=2)
            
            # Contorno do braço esquerdo
            pygame.draw.rect(surface, self.color_dark, arm_left_h, 1, border_radius=2)
            pygame.draw.rect(surface, self.color_dark, arm_left_v, 1, border_radius=2)
        
        if h > 35:
            # Braço direito (meio do cacto)
            arm_right_height = int(h * 0.28)
            arm_right_y = y + int(h * 0.45)
            arm_right_width = int(w * 0.4)
            
            # Parte horizontal do braço direito
            arm_right_h = pygame.Rect(trunk_x + trunk_width - 4, 
                                      arm_right_y + arm_right_height - 6, 
                                      arm_right_width, 6)
            pygame.draw.rect(surface, self.color_green, arm_right_h, border_radius=2)
            
            # Parte vertical do braço direito (dobra para cima)
            arm_right_v = pygame.Rect(trunk_x + trunk_width + arm_right_width - 10, 
                                      arm_right_y, 
                                      6, arm_right_height)
            pygame.draw.rect(surface, self.color_green, arm_right_v, border_radius=2)
            
            # Contorno do braço direito
            pygame.draw.rect(surface, self.color_dark, arm_right_h, 1, border_radius=2)
            pygame.draw.rect(surface, self.color_dark, arm_right_v, 1, border_radius=2)
        
        # === ESPINHOS (pequenos detalhes) ===
        # Espinhos no tronco
        num_spikes = max(3, h // 12)
        for i in range(num_spikes):
            spike_y = y + 5 + (h - 10) * i // num_spikes
            # Espinho esquerdo
            spike_left = [(trunk_x, spike_y), 
                         (trunk_x - 3, spike_y), 
                         (trunk_x, spike_y + 3)]
            pygame.draw.polygon(surface, self.color_dark, spike_left)
            
            # Espinho direito
            spike_right = [(trunk_x + trunk_width, spike_y), 
                          (trunk_x + trunk_width + 3, spike_y), 
                          (trunk_x + trunk_width, spike_y + 3)]
            pygame.draw.polygon(surface, self.color_dark, spike_right)
        
        # === TOPO DO CACTO (arredondado) ===
        top_rect = pygame.Rect(trunk_x, y - 2, trunk_width, 6)
        pygame.draw.ellipse(surface, self.color_light, top_rect)
        pygame.draw.ellipse(surface, self.color_dark, top_rect, 1)
        
        # === CONTORNO PRINCIPAL ===
        pygame.draw.rect(surface, self.color_dark, trunk, 2, border_radius=3)
        
        # DEBUG: Desenhar hitbox (descomente para visualizar)
        # pygame.draw.rect(surface, (255, 0, 0, 100), self.get_rect(), 2)
        
    def off_screen(self):
        """Verifica se obstáculo saiu da tela"""
        return self.x < -self.width
