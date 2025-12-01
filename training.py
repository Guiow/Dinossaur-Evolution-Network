"""Modo de treinamento com botões de controle"""
import pygame
import numpy as np
from game.config import *
from game.engine import GameEngine
from game.renderer import Renderer
from ai.evolutionary_algorithm import EvolutionaryAlgorithm
from ai.neural_network import NeuralNetwork
from ai.population import Agent
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

def load_population_from_model(ea, model_data):
    """Carrega população de um modelo"""
    best_brain = NeuralNetwork(ea.input_size, ea.hidden_size, ea.output_size)
    best_brain.set_weights(model_data['weights'])
    
    new_agents = []
    
    for i in range(ea.elite_count):
        new_agents.append(Agent(best_brain.copy()))
    
    while len(new_agents) < ea.population_size:
        mutated_brain = best_brain.copy()
        weights = mutated_brain.get_weights()
        mutation_mask = np.random.rand(len(weights)) < 0.3
        mutations = np.random.randn(len(weights)) * 0.4
        weights += mutation_mask * mutations
        mutated_brain.set_weights(weights)
        new_agents.append(Agent(mutated_brain))
    
    ea.population.agents = new_agents

def training_mode(app, model_data, start_generation):
    """Executa treinamento com botões de controle"""
    # Inicializa EA
    ea = EvolutionaryAlgorithm(
        population_size=POPULATION_SIZE,
        input_size=5,
        hidden_size=8,
        output_size=2,
        mutation_rate=0.15,
        mutation_strength=0.3,
        elite_ratio=0.1
    )
    
    if model_data:
        load_population_from_model(ea, model_data)
        ea.generation = start_generation
    
    app.session_manager.start_new_session(start_generation)
    
    renderer = Renderer(app.screen)
    
    # Botões de controle (fixos no canto inferior)
    screen_width, screen_height = app.screen.get_size()
    
    # Calcula posições dos botões considerando a área de jogo escalada
    button_width = 200
    button_height = 50
    button_spacing = 10
    button_y = screen_height - button_height - 10
    
    save_exit_button = Button(10, button_y, button_width, button_height,
                              "SALVAR E SAIR", (50, 150, 100), (70, 180, 130))
    exit_no_save_button = Button(button_width + button_spacing + 10, button_y, 
                                 button_width, button_height,
                                 "SAIR SEM SALVAR", (200, 50, 50), (230, 70, 70))
    
    running = True
    exit_action = None  # None, 'save', 'no_save'
    
    try:
        while running:
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_action = 'save'
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # ESC = salvar e sair
                        exit_action = 'save'
                        running = False
                    elif event.key == pygame.K_F11:
                        app.toggle_fullscreen()
                        renderer.screen = app.screen
                        renderer.update_scale()
                        # Atualiza posições dos botões
                        screen_width, screen_height = app.screen.get_size()
                        button_y = screen_height - button_height - 10
                        save_exit_button.rect.y = button_y
                        exit_no_save_button.rect.y = button_y
                
                # Verifica cliques nos botões
                if save_exit_button.handle_event(event):
                    exit_action = 'save'
                    running = False
                
                if exit_no_save_button.handle_event(event):
                    # Confirma antes de sair sem salvar
                    if confirm_no_save(app):
                        exit_action = 'no_save'
                        running = False
            
            # Simulação da geração
            game = GameEngine()
            population = ea.get_current_population()
            
            while not population.all_dead() and running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit_action = 'save'
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            exit_action = 'save'
                            running = False
                        elif event.key == pygame.K_F11:
                            app.toggle_fullscreen()
                            renderer.screen = app.screen
                            renderer.update_scale()
                            screen_width, screen_height = app.screen.get_size()
                            button_y = screen_height - button_height - 10
                            save_exit_button.rect.y = button_y
                            exit_no_save_button.rect.y = button_y
                    
                    if save_exit_button.handle_event(event):
                        exit_action = 'save'
                        running = False
                    
                    if exit_no_save_button.handle_event(event):
                        if confirm_no_save(app):
                            exit_action = 'no_save'
                            running = False
                        
                game.update()
                
                for agent in population.get_alive_agents():
                    state = get_game_state(agent.dino, game)
                    agent.think(state)
                    agent.update()
                    
                    if game.check_collision(agent.dino):
                        agent.dino.alive = False
                        
                # Renderiza jogo
                renderer.draw_game(
                    game, [a.dino for a in population.agents],
                    ea.generation, 
                    ea.best_fitness_history[-1] if ea.best_fitness_history else 0
                )
                
                # Desenha botões sobre a tela
                save_exit_button.draw(app.screen)
                exit_no_save_button.draw(app.screen)
                
                pygame.display.flip()
                app.clock.tick(FPS)
            
            if not running:
                break
                
            # Estatísticas
            best_fitness = population.get_best_fitness()
            avg_fitness = sum(a.get_fitness() for a in population.agents) / len(population.agents)
            best_agent = ea.get_best_agent()
            
            # Atualiza sessão
            app.session_manager.update_session(ea.generation, best_fitness, avg_fitness, best_agent.brain)
            
            # Evolui
            ea.evolve()
            
    finally:
        # Ação de saída
        if exit_action == 'save':
            best_agent = ea.get_best_agent()
            app.session_manager.end_session(best_agent.brain)
            print("\n✓ Sessao salva com sucesso!")
        elif exit_action == 'no_save':
            # Cancela sessão sem salvar
            app.session_manager.current_session_data = None
            app.session_manager.current_session_id = None
            print("\n⚠ Sessao descartada (nao salva)")

def confirm_no_save(app):
    """Diálogo de confirmação para sair sem salvar"""
    width, height = app.screen.get_size()
    
    dialog_width = 600
    dialog_height = 300
    dialog_x = (width - dialog_width) // 2
    dialog_y = (height - dialog_height) // 2
    
    yes_button = Button(dialog_x + 50, dialog_y + 200, 200, 60,
                       "SIM", (200, 50, 50), (230, 70, 70))
    no_button = Button(dialog_x + 350, dialog_y + 200, 200, 60,
                      "NAO", (50, 150, 50), (70, 180, 70))
    
    running = True
    while running:
        # Desenha fundo
        app.draw_background()
        
        # Fundo do diálogo
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(app.screen, (40, 40, 60), dialog_rect, border_radius=15)
        pygame.draw.rect(app.screen, (200, 100, 100), dialog_rect, 5, border_radius=15)
        
        # Textos
        title_surf = app.subtitle_font.render("Sair sem salvar?", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(width // 2, dialog_y + 70))
        app.screen.blit(title_surf, title_rect)
        
        msg_surf = pygame.font.Font(None, 28).render("Todo o progresso sera perdido!", True, (255, 200, 100))
        msg_rect = msg_surf.get_rect(center=(width // 2, dialog_y + 130))
        app.screen.blit(msg_surf, msg_rect)
        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            
            if yes_button.handle_event(event):
                return True
            if no_button.handle_event(event):
                return False
        
        yes_button.draw(app.screen)
        no_button.draw(app.screen)
        
        pygame.display.flip()
        app.clock.tick(60)
    
    return False
