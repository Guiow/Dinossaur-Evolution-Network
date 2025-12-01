"""Classe do porquinho com camisa de time aleatória"""
import pygame
import random
from game.config import *


class Dino:
    def __init__(self):
        self.x = DINO_X
        self.y = GROUND_Y
        # HITBOX ORIGINAL - NÃO MUDA
        self.width = 40
        self.height = 50
        self.velocity_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.fitness = 0
        self.alive = True
        
        # Cores do porquinho
        self.color_pink = (255, 182, 193)
        self.color_dark_pink = (200, 120, 140)
        self.color_snout = (255, 200, 210)
        self.color_eye = (0, 0, 0)
        
        # Escolhe camisa aleatória de um time
        self._choose_random_shirt()
        
    def _choose_random_shirt(self):
        """Escolhe uma camisa de time aleatória"""
        shirts = [
            # Palmeiras (Verde e Branco)
            {'colors': [(0, 155, 58), (255, 255, 255)], 'stripes': 5},
            
            # Flamengo (Vermelho e Preto)
            {'colors': [(220, 20, 60), (0, 0, 0)], 'stripes': 5},
            
            # Corinthians (Branco e Preto)
            {'colors': [(255, 255, 255), (0, 0, 0)], 'stripes': 5},
            
            # São Paulo (Vermelho, Branco e Preto - horizontal)
            {'colors': [(220, 20, 60), (255, 255, 255), (0, 0, 0)], 'stripes': 6},
            
            # Santos (Branco e Preto - vertical fino)
            {'colors': [(255, 255, 255), (0, 0, 0)], 'stripes': 6},
            
            # Grêmio (Azul, Preto e Branco)
            {'colors': [(0, 102, 204), (0, 0, 0), (255, 255, 255)], 'stripes': 6},
            
            # Internacional (Vermelho)
            {'colors': [(220, 20, 60)], 'stripes': 1},
            
            # Vasco (Branco e Preto - faixa diagonal simulada)
            {'colors': [(255, 255, 255), (0, 0, 0)], 'stripes': 5},
            
            # Cruzeiro (Azul)
            {'colors': [(0, 76, 153)], 'stripes': 1},
            
            # Botafogo (Preto e Branco)
            {'colors': [(0, 0, 0), (255, 255, 255)], 'stripes': 5},
            
            # Atlético-MG (Preto e Branco)
            {'colors': [(0, 0, 0), (255, 255, 255)], 'stripes': 5},
            
            # Fluminense (Grená, Branco e Verde)
            {'colors': [(128, 0, 32), (255, 255, 255), (0, 102, 51)], 'stripes': 6},
            
            # Bahia (Azul, Vermelho e Branco)
            {'colors': [(0, 82, 147), (220, 20, 60), (255, 255, 255)], 'stripes': 6},
            
            # Athletico-PR (Vermelho e Preto)
            {'colors': [(220, 20, 60), (0, 0, 0)], 'stripes': 5},
            
            # Sport (Vermelho e Preto)
            {'colors': [(220, 20, 60), (0, 0, 0)], 'stripes': 5},
        ]
        
        chosen_shirt = random.choice(shirts)
        self.shirt_colors = chosen_shirt['colors']
        self.shirt_stripes = chosen_shirt['stripes']
        
    def jump(self):
        """Faz o porquinho pular"""
        if not self.is_jumping and not self.is_ducking:
            self.velocity_y = JUMP_VELOCITY
            self.is_jumping = True
            
    def duck(self):
        """Faz o porquinho abaixar"""
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
        """Atualiza física do porquinho"""
        if self.is_jumping:
            self.velocity_y += GRAVITY
            self.y += self.velocity_y
            
            if self.y >= GROUND_Y:
                self.y = GROUND_Y
                self.velocity_y = 0
                self.is_jumping = False
                
        self.fitness += 1
        
    def get_rect(self):
        """Retorna o retângulo de colisão (HITBOX ORIGINAL)"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        """Desenha o porquinho com camisa do time"""
        if not self.alive:
            # Se morto, desenha semi-transparente
            self._draw_pig(screen, alpha=128)
        else:
            self._draw_pig(screen, alpha=255)
            
        # DEBUG: Desenhar hitbox (descomente para visualizar)
        # pygame.draw.rect(screen, (255, 0, 0), self.get_rect(), 2)
    
    def _draw_pig(self, screen, alpha=255):
        """Desenha o porquinho com camisa"""
        x, y = self.x, self.y
        
        if self.is_ducking:
            self._draw_ducking_pig(screen, x, y, alpha)
        else:
            self._draw_standing_pig(screen, x, y, alpha)
    
    def _draw_standing_pig(self, screen, x, y, alpha):
        """Desenha porquinho em pé com camisa do time"""
        # === PERNAS (atrás da camisa) ===
        leg1 = pygame.Rect(x + 8, y + 38, 6, 12)
        pygame.draw.rect(screen, self.color_pink, leg1, border_radius=2)
        pygame.draw.rect(screen, self.color_dark_pink, leg1, 1, border_radius=2)
        
        leg2 = pygame.Rect(x + 20, y + 38, 6, 12)
        pygame.draw.rect(screen, self.color_pink, leg2, border_radius=2)
        pygame.draw.rect(screen, self.color_dark_pink, leg2, 1, border_radius=2)
        
        # Cascos
        pygame.draw.rect(screen, self.color_dark_pink, (x + 8, y + 48, 6, 2))
        pygame.draw.rect(screen, self.color_dark_pink, (x + 20, y + 48, 6, 2))
        
        # === CAMISA COM LISTRAS DO TIME ===
        shirt_rect = pygame.Rect(x + 5, y + 18, 30, 22)
        
        # Se camisa tem apenas 1 cor (sem listras)
        if len(self.shirt_colors) == 1:
            pygame.draw.rect(screen, self.shirt_colors[0], shirt_rect, border_radius=3)
        else:
            # Listras verticais
            stripe_width = 30 // self.shirt_stripes
            for i in range(self.shirt_stripes):
                stripe_x = x + 5 + i * stripe_width
                stripe_color = self.shirt_colors[i % len(self.shirt_colors)]
                stripe = pygame.Rect(stripe_x, y + 18, stripe_width, 22)
                pygame.draw.rect(screen, stripe_color, stripe)
        
        # Contorno da camisa
        pygame.draw.rect(screen, self.color_dark_pink, shirt_rect, 2, border_radius=3)
        
        # === CABEÇA (rosa, acima da camisa) ===
        head_center = (x + 23, y + 12)
        pygame.draw.circle(screen, self.color_pink, head_center, 10)
        pygame.draw.circle(screen, self.color_dark_pink, head_center, 10, 2)
        
        # === FOCINHO ===
        snout = pygame.Rect(x + 26, y + 13, 10, 7)
        pygame.draw.ellipse(screen, self.color_snout, snout)
        pygame.draw.ellipse(screen, self.color_dark_pink, snout, 1)
        
        # Narinas
        pygame.draw.circle(screen, self.color_dark_pink, (x + 30, y + 15), 1)
        pygame.draw.circle(screen, self.color_dark_pink, (x + 30, y + 17), 1)
        
        # === OLHO ===
        eye_center = (x + 21, y + 10)
        pygame.draw.circle(screen, self.color_eye, eye_center, 3)
        pygame.draw.circle(screen, (255, 255, 255), (x + 22, y + 9), 1)
        
        # === ORELHA ===
        ear_points = [
            (x + 16, y + 5),
            (x + 14, y + 2),
            (x + 19, y + 7)
        ]
        pygame.draw.polygon(screen, self.color_pink, ear_points)
        pygame.draw.polygon(screen, self.color_dark_pink, ear_points, 1)
        
        # === RABINHO ===
        tail_points = [
            (x + 3, y + 24),
            (x, y + 22),
            (x - 2, y + 24),
            (x, y + 26),
            (x + 2, y + 26)
        ]
        pygame.draw.lines(screen, self.color_dark_pink, False, tail_points, 2)
        
        # === BRAÇOS ===
        arm = pygame.Rect(x + 12, y + 28, 4, 6)
        pygame.draw.rect(screen, self.color_pink, arm, border_radius=2)
        pygame.draw.rect(screen, self.color_dark_pink, arm, 1, border_radius=2)
    
    def _draw_ducking_pig(self, screen, x, y, alpha):
        """Desenha porquinho agachado com camisa"""
        # === PERNAS DOBRADAS ===
        leg1 = pygame.Rect(x + 8, y + 22, 8, 6)
        pygame.draw.rect(screen, self.color_pink, leg1, border_radius=2)
        pygame.draw.rect(screen, self.color_dark_pink, leg1, 1, border_radius=2)
        
        leg2 = pygame.Rect(x + 20, y + 22, 8, 6)
        pygame.draw.rect(screen, self.color_pink, leg2, border_radius=2)
        pygame.draw.rect(screen, self.color_dark_pink, leg2, 1, border_radius=2)
        
        # === CAMISA COM LISTRAS ===
        shirt_rect = pygame.Rect(x + 4, y + 10, 32, 14)
        
        if len(self.shirt_colors) == 1:
            pygame.draw.rect(screen, self.shirt_colors[0], shirt_rect, border_radius=3)
        else:
            stripe_width = 32 // self.shirt_stripes
            for i in range(self.shirt_stripes):
                stripe_x = x + 4 + i * stripe_width
                stripe_color = self.shirt_colors[i % len(self.shirt_colors)]
                stripe = pygame.Rect(stripe_x, y + 10, stripe_width, 14)
                pygame.draw.rect(screen, stripe_color, stripe)
        
        pygame.draw.rect(screen, self.color_dark_pink, shirt_rect, 2, border_radius=3)
        
        # === CABEÇA ===
        head_center = (x + 28, y + 8)
        pygame.draw.circle(screen, self.color_pink, head_center, 8)
        pygame.draw.circle(screen, self.color_dark_pink, head_center, 8, 2)
        
        # === FOCINHO ===
        snout = pygame.Rect(x + 32, y + 8, 8, 6)
        pygame.draw.ellipse(screen, self.color_snout, snout)
        pygame.draw.ellipse(screen, self.color_dark_pink, snout, 1)
        
        pygame.draw.circle(screen, self.color_dark_pink, (x + 36, y + 10), 1)
        pygame.draw.circle(screen, self.color_dark_pink, (x + 36, y + 12), 1)
        
        # === OLHO ===
        eye_center = (x + 26, y + 6)
        pygame.draw.circle(screen, self.color_eye, eye_center, 2)
        pygame.draw.circle(screen, (255, 255, 255), (x + 27, y + 5), 1)
        
        # === ORELHA ===
        ear_points = [
            (x + 22, y + 3),
            (x + 20, y + 1),
            (x + 24, y + 5)
        ]
        pygame.draw.polygon(screen, self.color_pink, ear_points)
        pygame.draw.polygon(screen, self.color_dark_pink, ear_points, 1)
        
        # === RABINHO ===
        tail_points = [
            (x + 2, y + 14),
            (x - 1, y + 12),
            (x - 2, y + 15),
            (x, y + 16)
        ]
        pygame.draw.lines(screen, self.color_dark_pink, False, tail_points, 2)
