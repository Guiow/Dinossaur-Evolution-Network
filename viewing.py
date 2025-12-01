"""Modo de visualização com botão de voltar"""
import pygame
from game.config import *
from game.engine import GameEngine
from game.dino import Dino
from ai.neural_network import NeuralNetwork
from ui.gui_components import Button

def get_game_state(dino, game):
    """Extrai estado do jogo"""
    obstacle = game.get_next_obstacle()
    
    if obstacle is None:
        return [1.0, 1.0, 1.0, 0.0, 0.0]
    
    distance = (obstacle.x - dino.x) / SCREEN_WIDTH
    obstacle_height = obstacle.height / 100.0
    obstacle_width = obstacle.width / 100.0
    dino_y = dino.y / SCREEN_HEIGHT
    dino_velocity = (dino.velocity_y + 20) / 40.0
    
    return [distance, obstacle_height, obstacle_width, dino_y, dino_velocity]

class ViewingRenderer:
    """Renderizador para modo visualização"""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        
        self.base_width = SCREEN_WIDTH
        self.base_height = SCREEN_HEIGHT
        self.game_surface = pygame.Surface((self.base_width, self.base_height))
        
        self.update_scale()
        
    def update_scale(self):
        """Atualiza escala"""
        screen_width, screen_height = self.screen.get_size()
        
        scale_x = screen_width / self.base_width
        scale_y = screen_height / self.base_height
        self.scale = min(scale_x, scale_y)
        
        self.scaled_width = int(self.base_width * self.scale)
        self.scaled_height = int(self.base_height * self.scale)
        
        self.offset_x = (screen_width - self.scaled_width) // 2
        self.offset_y = (screen_height - self.scaled_height) // 2
        
    def draw(self, game, dino, stats):
        """Desenha o jogo"""
        current_size = self.screen.get_size()
        expected_size = (self.offset_x * 2 + self.scaled_width, 
                        self.offset_y * 2 + self.scaled_height)
        if current_size != expected_size:
            self.update_scale()
        
        self.screen.fill((20, 20, 35))
        self.game_surface.fill(WHITE)
        
        pygame.draw.line(self.game_surface, BLACK, (0, GROUND_Y + 50), 
                        (self.base_width, GROUND_Y + 50), 2)
        
        for obstacle in game.obstacles:
            obstacle.draw(self.game_surface)
            
        dino.draw(self.game_surface)
        
        texts = [
            f"Score: {stats['score']}",
            f"Melhor: {stats['best_score']}",
            f"Media: {stats['avg_score']:.0f}",
            f"Jogos: {stats['games_played']}",
            f"Fitness Treino: {stats['training_fitness']}"
        ]
        
        y = 10
        for text in texts:
            surface = self.font.render(text, True, BLACK)
            self.game_surface.blit(surface, (10, y))
            y += 35
        
        scaled_surface = pygame.transform.scale(self.game_surface, 
                                                (self.scaled_width, self.scaled_height))
        self.screen.blit(scaled_surface, (self.offset_x, self.offset_y))
        
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

def viewing_mode(app, model_data):
    """Assistir IA jogando com botão de voltar"""
    brain = NeuralNetwork(
        model_data['input_size'],
        model_data['hidden_size'],
        model_data['output_size']
    )
    brain.set_weights(model_data['weights'])
    
    dino = Dino()
    game = GameEngine()
    renderer = ViewingRenderer(app.screen)
    
    # Botão de voltar
    screen_width, screen_height = app.screen.get_size()
    back_button = Button(10, screen_height - 60, 200, 50,
                        "VOLTAR", (100, 100, 100), (130, 130, 130))
    
    running = True
    games_played = 0
    best_score = 0
    total_score = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                app.toggle_fullscreen()
                renderer.screen = app.screen
                renderer.update_scale()
                screen_width, screen_height = app.screen.get_size()
                back_button.rect.y = screen_height - 60
            
            if back_button.handle_event(event):
                running = False
                
        if dino.alive:
            state = get_game_state(dino, game)
            output = brain.forward(state)
            
            if output[0] > 0.5:
                dino.jump()
            elif output[1] > 0.5:
                dino.duck()
            else:
                dino.stand()
                
            game.update()
            dino.update()
            
            if game.check_collision(dino):
                dino.alive = False
                games_played += 1
                total_score += game.score
                
                if game.score > best_score:
                    best_score = game.score
        else:
            pygame.time.wait(1000)
            dino = Dino()
            game.reset()
        
        stats = {
            'score': game.score,
            'best_score': best_score,
            'avg_score': total_score / games_played if games_played > 0 else 0,
            'games_played': games_played,
            'training_fitness': int(model_data['fitness'])
        }
        
        renderer.draw(game, dino, stats)
        
        # Desenha botão sobre tudo
        back_button.draw(app.screen)
        
        pygame.display.flip()
        app.clock.tick(FPS)
