"""Algoritmo Evolutivo REAL para treinar as redes neurais"""
import numpy as np
from ai.population import Population, Agent
from ai.neural_network import NeuralNetwork


class EvolutionaryAlgorithm:
    def __init__(self, population_size, input_size, hidden_size, output_size,
                 mutation_rate=0.2, mutation_strength=0.5, elite_ratio=0.1,
                 start_generation=1):
        """
        population_size: tamanho da população
        mutation_rate: probabilidade inicial de mutação
        mutation_strength: força inicial da mutação
        elite_ratio: proporção de elite preservada (top performers)
        start_generation: geração inicial (para continuar treinamento)
        """
        self.population_size = population_size
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        self.initial_mutation_rate = mutation_rate
        self.mutation_rate = mutation_rate
        self.initial_mutation_strength = mutation_strength
        self.mutation_strength = mutation_strength
        self.elite_count = max(2, int(population_size * elite_ratio))
        
        self.population = Population(population_size, input_size, 
                                     hidden_size, output_size)
        self.generation = start_generation
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.species_diversity = []
        
        print(f"\n🧬 Algoritmo Evolutivo Inicializado:")
        print(f"   População: {population_size}")
        print(f"   Elite: {self.elite_count} ({elite_ratio*100:.0f}%)")
        print(f"   Taxa de Mutação: {mutation_rate}")
        print(f"   Arquitetura: {input_size}-{hidden_size}-{output_size}")
        print(f"   Geração inicial: {start_generation}\n")
        
    def evolve(self):
        """
        Evolução CONSERVADORA: Preserva o que funciona, explora gradualmente
        """
        # Ordena população por fitness (melhor → pior)
        self.population.agents.sort(key=lambda x: x.get_fitness(), reverse=True)
        
        # Calcula estatísticas
        fitnesses = [agent.get_fitness() for agent in self.population.agents]
        best_fitness = fitnesses[0]
        avg_fitness = np.mean(fitnesses)
        
        self.best_fitness_history.append(best_fitness)
        self.avg_fitness_history.append(avg_fitness)
        
        # Calcula diversidade genética
        diversity = self._calculate_genetic_diversity()
        self.species_diversity.append(diversity)
        
        print(f"Gen {self.generation:3d} | "
              f"Melhor: {best_fitness:7.0f} | "
              f"Média: {avg_fitness:7.0f} | "
              f"Diversidade: {diversity:.3f} | "
              f"Mut: {self.mutation_rate:.3f}")
        
        # ===== ESTRATÉGIA CONSERVADORA =====
        best_parent_brain = self.population.agents[0].brain
        
        new_population = []
        
        # 1. UMA cópia EXATA do melhor (0% mutação)
        new_population.append(Agent(best_parent_brain.copy()))
        
        # 2. 60% da população: Mutação MUITO LEVE (apenas refinamento)
        # Esses são os filhos que vão MANTER o comportamento do pai
        num_conservative = int(self.population_size * 0.6)
        for _ in range(num_conservative):
            if len(new_population) >= self.population_size:
                break
            child_brain = best_parent_brain.copy()
            weights = child_brain.get_weights()
            
            # Apenas 10% dos genes mutam, com força 0.15
            mutation_mask = np.random.rand(len(weights)) < 0.1
            mutations = np.random.randn(len(weights)) * 0.15
            weights += mutation_mask * mutations
            
            child_brain.set_weights(weights)
            new_population.append(Agent(child_brain))
        
        # 3. 25% da população: Mutação MODERADA (exploração local)
        num_moderate = int(self.population_size * 0.25)
        for _ in range(num_moderate):
            if len(new_population) >= self.population_size:
                break
            child_brain = best_parent_brain.copy()
            weights = child_brain.get_weights()
            
            # 25% dos genes mutam, força 0.3
            mutation_mask = np.random.rand(len(weights)) < 0.25
            mutations = np.random.randn(len(weights)) * 0.3
            weights += mutation_mask * mutations
            
            child_brain.set_weights(weights)
            new_population.append(Agent(child_brain))
        
        # 4. 15% restante: Mutação FORTE (exploração)
        while len(new_population) < self.population_size:
            child_brain = best_parent_brain.copy()
            weights = child_brain.get_weights()
            
            # 40% dos genes mutam, força 0.5
            mutation_mask = np.random.rand(len(weights)) < 0.4
            mutations = np.random.randn(len(weights)) * 0.5
            weights += mutation_mask * mutations
            
            child_brain.set_weights(weights)
            new_population.append(Agent(child_brain))
        
        # ===== ATUALIZAÇÃO =====
        self.population.agents = new_population
        
        # Mutação adaptativa (agora mais conservadora)
        self._adaptive_mutation(best_fitness, avg_fitness, diversity)
        
        # Incrementa geração
        self.generation += 1
        
    def _fitness_proportionate_selection(self, fitnesses):
        """
        Seleção proporcional ao fitness (Roulette Wheel Selection)
        Indivíduos com maior fitness têm maior chance de serem selecionados
        """
        # Evita fitness negativo e adiciona offset
        min_fitness = min(fitnesses)
        adjusted_fitnesses = [f - min_fitness + 1 for f in fitnesses]
        
        total_fitness = sum(adjusted_fitnesses)
        
        if total_fitness == 0:
            # Se todos têm fitness 0, seleção uniforme
            return np.random.randint(0, len(fitnesses))
        
        # Probabilidades proporcionais ao fitness
        probabilities = [f / total_fitness for f in adjusted_fitnesses]
        
        # Seleciona índice baseado nas probabilidades
        selected_idx = np.random.choice(len(fitnesses), p=probabilities)
        
        return selected_idx
    
    def _tournament_selection(self, fitnesses, tournament_size=5):
        """
        Seleção por torneio (alternativa mais agressiva)
        """
        # Seleciona indivíduos aleatórios para o torneio
        tournament_indices = np.random.choice(
            len(fitnesses), 
            size=min(tournament_size, len(fitnesses)), 
            replace=False
        )
        
        # Retorna o melhor do torneio
        tournament_fitnesses = [fitnesses[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitnesses)]
        
        return winner_idx
        
    def _crossover(self, brain1, brain2):
        """
        Cruzamento genético REAL (múltiplos métodos)
        """
        child_brain = NeuralNetwork(self.input_size, self.hidden_size, 
                                     self.output_size)
        
        weights1 = brain1.get_weights()
        weights2 = brain2.get_weights()
        child_weights = np.zeros_like(weights1)
        
        # Método de crossover variado
        crossover_method = np.random.choice(['uniform', 'single_point', 'two_point', 'average'])
        
        if crossover_method == 'uniform':
            # Crossover uniforme: cada gene vem aleatoriamente de um dos pais
            mask = np.random.rand(len(weights1)) < 0.5
            child_weights = np.where(mask, weights1, weights2)
            
        elif crossover_method == 'single_point':
            # Crossover de ponto único
            point = np.random.randint(1, len(weights1))
            child_weights[:point] = weights1[:point]
            child_weights[point:] = weights2[point:]
            
        elif crossover_method == 'two_point':
            # Crossover de dois pontos
            point1 = np.random.randint(0, len(weights1) // 2)
            point2 = np.random.randint(len(weights1) // 2, len(weights1))
            
            child_weights[:point1] = weights1[:point1]
            child_weights[point1:point2] = weights2[point1:point2]
            child_weights[point2:] = weights1[point2:]
            
        elif crossover_method == 'average':
            # Média ponderada (blend crossover)
            alpha = np.random.uniform(0.3, 0.7)
            child_weights = alpha * weights1 + (1 - alpha) * weights2
        
        child_brain.set_weights(child_weights)
        return child_brain
        
    def _mutate(self, brain):
        """
        Mutação genética
        """
        weights = brain.get_weights()
        
        # Máscara de mutação
        mutation_mask = np.random.rand(len(weights)) < self.mutation_rate
        
        # Mutação gaussiana
        mutations = np.random.randn(len(weights)) * self.mutation_strength
        weights += mutation_mask * mutations
        
        brain.set_weights(weights)
    
    def _adaptive_mutation(self, best_fitness, avg_fitness, diversity):
        """
        Mutação adaptativa CONSERVADORA
        """
        # Se diversidade muito baixa, aumenta mutação (mas não muito)
        if diversity < 0.05:
            self.mutation_rate = min(0.3, self.mutation_rate * 1.1)
            self.mutation_strength = min(0.5, self.mutation_strength * 1.05)
            
        # Se está estagnado, aumenta mutação levemente
        elif len(self.best_fitness_history) > 10:
            recent_best = self.best_fitness_history[-10:]
            improvement = (recent_best[-1] - recent_best[0]) / (recent_best[0] + 1)
            
            if improvement < 0.05:  # Menos de 5% de melhoria em 10 gerações
                self.mutation_rate = min(0.25, self.mutation_rate * 1.05)
            else:
                # Está progredindo, diminui mutação gradualmente
                self.mutation_rate = max(0.05, self.mutation_rate * 0.98)
                self.mutation_strength = max(0.1, self.mutation_strength * 0.98)
    
    def _calculate_genetic_diversity(self):
        """
        Calcula diversidade genética da população
        Útil para detectar convergência prematura
        """
        if len(self.population.agents) < 2:
            return 1.0
        
        # Pega pesos de alguns indivíduos
        sample_size = min(10, len(self.population.agents))
        samples = np.random.choice(self.population.agents, sample_size, replace=False)
        
        weights_matrix = [agent.brain.get_weights() for agent in samples]
        
        # Calcula variância média dos pesos
        variance = np.var(weights_matrix, axis=0).mean()
        
        # Normaliza para [0, 1]
        diversity = min(1.0, variance / 0.5)
        
        return diversity
        
    def get_current_population(self):
        """Retorna população atual"""
        return self.population
    
    def get_best_agent(self):
        """Retorna o melhor agente da população atual"""
        return max(self.population.agents, key=lambda x: x.get_fitness())
    
    def restore_from_checkpoint(self, checkpoint_data):
        """
        Restaura o estado do algoritmo evolutivo a partir de um checkpoint
        """
        self.generation = checkpoint_data['generation']
        self.best_fitness_history = checkpoint_data['best_fitness_history']
        
        if 'avg_fitness_history' in checkpoint_data:
            self.avg_fitness_history = checkpoint_data['avg_fitness_history']
        if 'species_diversity' in checkpoint_data:
            self.species_diversity = checkpoint_data['species_diversity']
        
        # Recria população com os pesos salvos
        self.population.agents = []
        
        for weights in checkpoint_data['population_weights']:
            nn = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)
            nn.set_weights(weights)
            agent = Agent(nn)
            self.population.agents.append(agent)
        
        # Restaura fitness
        for i, fitness in enumerate(checkpoint_data['population_fitness']):
            self.population.agents[i].dino.fitness = fitness
            
        print(f"✓ Algoritmo evolutivo restaurado da geração {self.generation}")
        print(f"  Melhor fitness histórico: {max(self.best_fitness_history):.0f}")
