"""Renderização gráfica com suporte a escala dinâmica"""
import pygame
from game.config import *

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        
        # Dimensões base do jogo (resolução de referência)
        self.base_width = SCREEN_WIDTH
        self.base_height = SCREEN_HEIGHT
        
        # Cria superfície virtual do jogo
        self.game_surface = pygame.Surface((self.base_width, self.base_height))
        
        # Calcula escala e offset para centralizar
        self.update_scale()
        
    def update_scale(self):
        """Atualiza escala e posição baseado no tamanho da tela"""
        screen_width, screen_height = self.screen.get_size()
        
        # Calcula escala mantendo proporção
        scale_x = screen_width / self.base_width
        scale_y = screen_height / self.base_height
        self.scale = min(scale_x, scale_y)  # Usa menor escala para manter proporção
        
        # Calcula dimensões escaladas
        self.scaled_width = int(self.base_width * self.scale)
        self.scaled_height = int(self.base_height * self.scale)
        
        # Calcula offset para centralizar
        self.offset_x = (screen_width - self.scaled_width) // 2
        self.offset_y = (screen_height - self.scaled_height) // 2
        
    def draw_game(self, game, dinos, generation, best_fitness):
        """Desenha o estado completo do jogo com escala"""
        # Verifica se tamanho da tela mudou
        if self.screen.get_size() != (self.offset_x * 2 + self.scaled_width, 
                                       self.offset_y * 2 + self.scaled_height):
            self.update_scale()
        
        # Limpa tela principal com cor de fundo
        self.screen.fill((20, 20, 35))
        
        # Desenha na superfície virtual (resolução base)
        self.game_surface.fill(WHITE)
        
        # Desenha chão
        pygame.draw.line(self.game_surface, BLACK, (0, GROUND_Y + 50), 
                        (self.base_width, GROUND_Y + 50), 2)
        
        # Desenha obstáculos
        for obstacle in game.obstacles:
            obstacle.draw(self.game_surface)
            
        # Desenha dinossauros vivos
        alive_count = 0
        for dino in dinos:
            if dino.alive:
                dino.draw(self.game_surface)
                alive_count += 1
                
        # Informações na superfície virtual
        self._draw_info(generation, alive_count, len(dinos), 
                       game.score, best_fitness, game.speed)
        
        # Escala e desenha na tela principal
        scaled_surface = pygame.transform.scale(self.game_surface, 
                                                (self.scaled_width, self.scaled_height))
        self.screen.blit(scaled_surface, (self.offset_x, self.offset_y))
        
        # Desenha bordas se houver espaço extra
        if self.offset_x > 0 or self.offset_y > 0:
            # Bordas laterais
            if self.offset_x > 0:
                pygame.draw.rect(self.screen, (50, 50, 70), 
                               (0, 0, self.offset_x, self.screen.get_height()))
                pygame.draw.rect(self.screen, (50, 50, 70), 
                               (self.offset_x + self.scaled_width, 0, 
                                self.offset_x, self.screen.get_height()))
            
            # Bordas superior/inferior
            if self.offset_y > 0:
                pygame.draw.rect(self.screen, (50, 50, 70), 
                               (0, 0, self.screen.get_width(), self.offset_y))
                pygame.draw.rect(self.screen, (50, 50, 70), 
                               (0, self.offset_y + self.scaled_height, 
                                self.screen.get_width(), self.offset_y))
            
            # Moldura decorativa
            pygame.draw.rect(self.screen, (100, 150, 200), 
                           (self.offset_x, self.offset_y, 
                            self.scaled_width, self.scaled_height), 3)
        
    def _draw_info(self, generation, alive, total, score, best_fitness, speed):
        """Desenha informações do treinamento na resolução base"""
        texts = [
            f"Geração: {generation}",
            f"Vivos: {alive}/{total}",
            f"Score: {score}",
            f"Melhor Fitness: {int(best_fitness)}",
            f"Velocidade: {speed:.1f}"
        ]
        
        y = 10
        for text in texts:
            surface = self.font.render(text, True, BLACK)
            self.game_surface.blit(surface, (10, y))
            y += 40
