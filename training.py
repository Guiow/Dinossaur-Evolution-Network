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
    """Extrai estado do jogo COM MAIS INFORMAÇÕES"""
    obstacle = game.get_next_obstacle()
    
    if obstacle is None:
        return [1.0, 1.0, 1.0, 0.0, 0.0, 1.0]
    
    distance = (obstacle.x - dino.x) / SCREEN_WIDTH
    obstacle_height = obstacle.height / 100.0
    obstacle_width = obstacle.width / 100.0
    dino_y = dino.y / SCREEN_HEIGHT
    dino_velocity = (dino.velocity_y + 20) / 40.0
    
    # Está no chão? (velocidade = 0 significa no chão)
    on_ground = 1.0 if dino.velocity_y == 0 else 0.0
    
    return [distance, obstacle_height, obstacle_width, dino_y, dino_velocity, on_ground]


def load_population_from_model(ea, model_data):
    """Carrega população COM CONSERVAÇÃO DO COMPORTAMENTO"""
    best_brain = NeuralNetwork(ea.input_size, ea.hidden_size, ea.output_size)
    best_brain.set_weights(model_data['weights'])
    
    new_agents = []
    
    # 1 cópia EXATA
    new_agents.append(Agent(best_brain.copy()))
    
    # 60% da população: Mutação MUITO LEVE (conserva comportamento)
    num_conservative = int(ea.population_size * 0.6)
    for _ in range(num_conservative):
        mutated_brain = best_brain.copy()
        weights = mutated_brain.get_weights()
        
        # 10% genes, força 0.15
        mutation_mask = np.random.rand(len(weights)) < 0.1
        mutations = np.random.randn(len(weights)) * 0.15
        weights += mutation_mask * mutations
        
        mutated_brain.set_weights(weights)
        new_agents.append(Agent(mutated_brain))
    
    # 25% Mutação MODERADA
    num_moderate = int(ea.population_size * 0.25)
    for _ in range(num_moderate):
        if len(new_agents) >= ea.population_size:
            break
        mutated_brain = best_brain.copy()
        weights = mutated_brain.get_weights()
        
        # 25% genes, força 0.3
        mutation_mask = np.random.rand(len(weights)) < 0.25
        mutations = np.random.randn(len(weights)) * 0.3
        weights += mutation_mask * mutations
        
        mutated_brain.set_weights(weights)
        new_agents.append(Agent(mutated_brain))
    
    # 15% restante: Mutação FORTE (exploração)
    while len(new_agents) < ea.population_size:
        mutated_brain = best_brain.copy()
        weights = mutated_brain.get_weights()
        
        # 40% genes, força 0.5
        mutation_mask = np.random.rand(len(weights)) < 0.4
        mutations = np.random.randn(len(weights)) * 0.5
        weights += mutation_mask * mutations
        
        mutated_brain.set_weights(weights)
        new_agents.append(Agent(mutated_brain))
    
    ea.population.agents = new_agents


def randomize_agent_positions(population):
    """Randomiza posições X dos agentes (±15 pixels para não confundir)"""
    for agent in population.agents:
        x_offset = np.random.uniform(-15, 15)
        agent.dino.x = 50 + x_offset


def training_mode(app, model_data, start_generation):
    """Executa treinamento com botões de controle"""
    # AGORA USA 6 INPUTS (adicionou on_ground)
    ea = EvolutionaryAlgorithm(
        population_size=POPULATION_SIZE,
        input_size=6,
        hidden_size=10,
        output_size=2,
        mutation_rate=0.15,
        mutation_strength=0.25,
        elite_ratio=0.02,
        start_generation=start_generation
    )
    
    if model_data:
        print(f"\n✓ Carregando modelo da geração {model_data['generation']}")
        load_population_from_model(ea, model_data)
    
    app.session_manager.start_new_session(start_generation)
    
    renderer = Renderer(app.screen)
    
    # Botões de controle
    screen_width, screen_height = app.screen.get_size()
    button_width = 200
    button_height = 50
    button_spacing = 10
    button_y = screen_height - button_height - 10
    
    save_exit_button = Button(10, button_y, button_width, button_height,
                              "SALVAR E SAIR", (50, 150, 100), (70, 180, 130))
    exit_no_save_button = Button(button_width + button_spacing + 10, button_y, 
                                 button_width, button_height,
                                 "SAIR", (200, 50, 50), (230, 70, 70))
    
    running = True
    exit_action = None
    
    # RASTREIA O MELHOR DE TODOS OS TEMPOS
    all_time_best_brain = None
    all_time_best_fitness = 0
    
    try:
        while running:
            # Eventos
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
                    exit_action = 'no_save'
                    running = False
            
            # RANDOMIZA POSIÇÕES X NO INÍCIO DE CADA GERAÇÃO
            population = ea.get_current_population()
            randomize_agent_positions(population)
            
            # Simulação da geração
            game = GameEngine()
            
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
                        exit_action = 'no_save'
                        running = False
                        
                game.update()
                
                for agent in population.get_alive_agents():
                    state = get_game_state(agent.dino, game)
                    agent.think(state)
                    agent.update()
                    
                    # BÔNUS: Recompensa pequena por abaixar (incentiva usar essa ação)
                    if agent.dino.is_ducking:
                        agent.dino.fitness += 0.05
                    
                    if game.check_collision(agent.dino):
                        agent.dino.alive = False
                        
                # Renderiza jogo
                renderer.draw_game(
                    game, [a.dino for a in population.agents],
                    ea.generation,
                    ea.best_fitness_history[-1] if ea.best_fitness_history else 0
                )
                
                # Desenha botões
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
            
            # ATUALIZA O MELHOR DE TODOS OS TEMPOS
            if best_fitness > all_time_best_fitness:
                all_time_best_fitness = best_fitness
                all_time_best_brain = best_agent.brain.copy()
                print(f"   🏆 NOVO RECORDE! Fitness: {best_fitness:.0f}")
            
            # SALVA APENAS O MELHOR DE TODOS OS TEMPOS
            app.session_manager.update_session(
                ea.generation, 
                all_time_best_fitness,
                avg_fitness, 
                all_time_best_brain if all_time_best_brain else best_agent.brain
            )
            
            # Evolui
            ea.evolve()
            
    finally:
        if exit_action == 'save':
            if all_time_best_brain:
                app.session_manager.end_session(all_time_best_brain)
            else:
                best_agent = ea.get_best_agent()
                app.session_manager.end_session(best_agent.brain)
            print("\n✓ Sessao salva com sucesso!")
        elif exit_action == 'no_save':
            app.session_manager.current_session_data = None
            app.session_manager.current_session_id = None
            print("\n⚠ Sessao descartada (nao salva)")
