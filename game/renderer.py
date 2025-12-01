"""Renderização gráfica com painel de estatísticas melhorado"""
import pygame
from game.config import *

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        
        # Fontes mais legíveis
        try:
            self.font_large = pygame.font.SysFont('arial', 28, bold=True)
            self.font_medium = pygame.font.SysFont('arial', 24, bold=True)
            self.font_small = pygame.font.SysFont('arial', 20, bold=False)
        except:
            self.font_large = pygame.font.Font(None, 32)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 24)
        
        self.base_width = SCREEN_WIDTH
        self.base_height = SCREEN_HEIGHT
        self.game_surface = pygame.Surface((self.base_width, self.base_height))
        
        self.update_scale()
        
    def update_scale(self):
        """Atualiza escala e posição baseado no tamanho da tela"""
        screen_width, screen_height = self.screen.get_size()
        
        scale_x = screen_width / self.base_width
        scale_y = screen_height / self.base_height
        self.scale = min(scale_x, scale_y)
        
        self.scaled_width = int(self.base_width * self.scale)
        self.scaled_height = int(self.base_height * self.scale)
        
        self.offset_x = (screen_width - self.scaled_width) // 2
        self.offset_y = (screen_height - self.scaled_height) // 2
        
    def draw_game(self, game, dinos, generation, best_fitness):
        """Desenha o estado completo do jogo com escala"""
        if self.screen.get_size() != (self.offset_x * 2 + self.scaled_width, 
                                       self.offset_y * 2 + self.scaled_height):
            self.update_scale()
        
        self.screen.fill((20, 20, 35))
        
        # === FUNDO CINZA CLARO ===
        self.game_surface.fill((245, 245, 245))  # Cinza muito claro (quase branco)
        
        # === CHÃO ===
        ground_y = GROUND_Y + 50
        
        # Terra (marrom)
        ground_rect = pygame.Rect(0, ground_y, self.base_width, 
                                 self.base_height - ground_y)
        pygame.draw.rect(self.game_surface, (194, 154, 108), ground_rect)
        
        # Camada de grama no topo (verde)
        grass_rect = pygame.Rect(0, ground_y, self.base_width, 12)
        pygame.draw.rect(self.game_surface, (76, 153, 76), grass_rect)
        
        # Linha de contorno da grama (verde escuro)
        pygame.draw.line(self.game_surface, (60, 120, 60), 
                        (0, ground_y), (self.base_width, ground_y), 2)
        
        # === OBSTÁCULOS (cactos) ===
        for obstacle in game.obstacles:
            obstacle.draw(self.game_surface)
            
        # === DINOSSAUROS ===
        alive_count = 0
        for dino in dinos:
            if dino.alive:
                dino.draw(self.game_surface)
                alive_count += 1
                
        # === PAINEL DE INFORMAÇÕES ===
        self._draw_info_panel(generation, alive_count, len(dinos), 
                             game.score, best_fitness, game.speed)
        
        # Escala e desenha
        scaled_surface = pygame.transform.scale(self.game_surface, 
                                                (self.scaled_width, self.scaled_height))
        self.screen.blit(scaled_surface, (self.offset_x, self.offset_y))
        
        # Bordas
        if self.offset_x > 0 or self.offset_y > 0:
            if self.offset_x > 0:
                pygame.draw.rect(self.screen, (50, 50, 70), 
                               (0, 0, self.offset_x, self.screen.get_height()))
                pygame.draw.rect(self.screen, (50, 50, 70), 
                               (self.offset_x + self.scaled_width, 0, 
                                self.offset_x, self.screen.get_height()))
            
            if self.offset_y > 0:
                pygame.draw.rect(self.screen, (50, 50, 70), 
                               (0, 0, self.screen.get_width(), self.offset_y))
                pygame.draw.rect(self.screen, (50, 50, 70), 
                               (0, self.offset_y + self.scaled_height, 
                                self.screen.get_width(), self.offset_y))
            
            pygame.draw.rect(self.screen, (100, 150, 200), 
                           (self.offset_x, self.offset_y, 
                            self.scaled_width, self.scaled_height), 3)
        
    def _draw_info_panel(self, generation, alive, total, score, best_fitness, speed):
        """Desenha painel de informações no canto direito superior"""
        panel_width = 260
        panel_height = 190
        
        panel_x = self.base_width - panel_width - 10
        panel_y = 10
        
        # Fundo semi-transparente
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.fill((245, 245, 250))
        panel_surface.set_alpha(235)
        self.game_surface.blit(panel_surface, (panel_x, panel_y))
        
        # Borda do painel
        pygame.draw.rect(self.game_surface, (80, 80, 100), 
                        (panel_x, panel_y, panel_width, panel_height), 3, border_radius=5)
        
        # Título do painel
        title_text = self.font_large.render("ESTATISTICAS", True, (40, 60, 100))
        self.game_surface.blit(title_text, (panel_x + 15, panel_y + 10))
        
        # Linha separadora
        pygame.draw.line(self.game_surface, (150, 150, 170), 
                        (panel_x + 10, panel_y + 45), 
                        (panel_x + panel_width - 10, panel_y + 45), 2)
        
        y_offset = panel_y + 55
        line_spacing = 27
        
        # Geração
        gen_label = self.font_small.render("Geracao:", True, (60, 60, 60))
        gen_value = self.font_medium.render(str(generation), True, (20, 100, 180))
        self.game_surface.blit(gen_label, (panel_x + 15, y_offset))
        self.game_surface.blit(gen_value, (panel_x + 150, y_offset - 2))
        y_offset += line_spacing
        
        # Vivos
        alive_percent = alive / total if total > 0 else 0
        if alive_percent > 0.5:
            alive_color = (0, 150, 0)
        elif alive_percent > 0.2:
            alive_color = (200, 150, 0)
        else:
            alive_color = (200, 0, 0)
            
        alive_label = self.font_small.render("Vivos:", True, (60, 60, 60))
        alive_value = self.font_medium.render(f"{alive}/{total}", True, alive_color)
        self.game_surface.blit(alive_label, (panel_x + 15, y_offset))
        self.game_surface.blit(alive_value, (panel_x + 150, y_offset - 2))
        y_offset += line_spacing
        
        # Score
        score_label = self.font_small.render("Score:", True, (60, 60, 60))
        score_value = self.font_medium.render(str(score), True, (50, 50, 50))
        self.game_surface.blit(score_label, (panel_x + 15, y_offset))
        self.game_surface.blit(score_value, (panel_x + 150, y_offset - 2))
        y_offset += line_spacing
        
        # Melhor Fitness
        fitness_label = self.font_small.render("Melhor:", True, (60, 60, 60))
        fitness_value = self.font_medium.render(str(int(best_fitness)), True, (220, 100, 0))
        self.game_surface.blit(fitness_label, (panel_x + 15, y_offset))
        self.game_surface.blit(fitness_value, (panel_x + 150, y_offset - 2))
        y_offset += line_spacing
        
        # Velocidade
        speed_label = self.font_small.render("Velocidade:", True, (60, 60, 60))
        speed_value = self.font_medium.render(f"{speed:.1f}", True, (50, 50, 50))
        self.game_surface.blit(speed_label, (panel_x + 15, y_offset))
        self.game_surface.blit(speed_value, (panel_x + 150, y_offset - 2))
