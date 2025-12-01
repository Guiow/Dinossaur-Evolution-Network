"""Rede Neural Feedforward"""
import numpy as np


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        """
        Inicializa a rede neural
        input_size: número de entradas
        hidden_size: número de neurônios na camada oculta
        output_size: número de saídas
        """
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Inicialização aleatória dos pesos
        self.weights1 = np.random.randn(input_size, hidden_size) * 0.5
        self.bias1 = np.random.randn(hidden_size) * 0.5
        
        self.weights2 = np.random.randn(hidden_size, output_size) * 0.5
        self.bias2 = np.random.randn(output_size) * 0.5
        
    def relu(self, x):
        """Função de ativação ReLU"""
        return np.maximum(0, x)
        
    def sigmoid(self, x):
        """Função de ativação Sigmoid"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
        
    def forward(self, inputs):
        """
        Propagação forward
        inputs: array de entrada
        retorna: array de saída
        """
        # Camada oculta
        hidden = self.relu(np.dot(inputs, self.weights1) + self.bias1)
        
        # Camada de saída
        output = self.sigmoid(np.dot(hidden, self.weights2) + self.bias2)
        
        return output
        
    def get_weights(self):
        """Retorna todos os pesos em um único array"""
        return np.concatenate([
            self.weights1.flatten(),
            self.bias1.flatten(),
            self.weights2.flatten(),
            self.bias2.flatten()
        ])
        
    def set_weights(self, weights):
        """Define os pesos a partir de um array"""
        idx = 0
        
        # Weights1
        size = self.input_size * self.hidden_size
        self.weights1 = weights[idx:idx+size].reshape(self.input_size, self.hidden_size)
        idx += size
        
        # Bias1
        size = self.hidden_size
        self.bias1 = weights[idx:idx+size]
        idx += size
        
        # Weights2
        size = self.hidden_size * self.output_size
        self.weights2 = weights[idx:idx+size].reshape(self.hidden_size, self.output_size)
        idx += size
        
        # Bias2
        self.bias2 = weights[idx:]
        
    def copy(self):
        """Cria uma cópia da rede neural"""
        new_nn = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)
        new_nn.set_weights(self.get_weights().copy())
        return new_nn
