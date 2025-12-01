"""Gerenciamento da população de agentes"""
import numpy as np
from game.dino import Dino
from ai.neural_network import NeuralNetwork


class Agent:
    def __init__(self, neural_network):
        self.dino = Dino()
        self.brain = neural_network
        
    def think(self, inputs):
        """
        Processa entradas e decide ação
        inputs: estado do jogo
        """
        output = self.brain.forward(inputs)
        
        # Decodifica ação
        # output[0] > 0.5: pular
        # output[1] > 0.5: abaixar
        
        if output[0] > 0.5:
            self.dino.jump()
        elif output[1] > 0.5:
            self.dino.duck()
        else:
            self.dino.stand()
            
    def update(self):
        """Atualiza o dinossauro"""
        self.dino.update()
        
    def get_fitness(self):
        """Retorna fitness do agente"""
        return self.dino.fitness


class Population:
    def __init__(self, size, input_size, hidden_size, output_size):
        """Cria população inicial"""
        self.size = size
        self.agents = []
        
        for _ in range(size):
            nn = NeuralNetwork(input_size, hidden_size, output_size)
            self.agents.append(Agent(nn))
            
    def get_alive_agents(self):
        """Retorna agentes ainda vivos"""
        return [agent for agent in self.agents if agent.dino.alive]
        
    def all_dead(self):
        """Verifica se todos morreram"""
        return len(self.get_alive_agents()) == 0
        
    def get_best_fitness(self):
        """Retorna o melhor fitness da população"""
        if not self.agents:
            return 0
        return max(agent.get_fitness() for agent in self.agents)
