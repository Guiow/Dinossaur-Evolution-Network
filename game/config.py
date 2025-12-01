"""Configurações globais do jogo"""

# Dimensões base do jogo (será escalado automaticamente para tela cheia)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# Física do jogo
GRAVITY = 1.2
JUMP_VELOCITY = -18
GROUND_Y = 300
DINO_X = 100

# Velocidade do jogo
INITIAL_SPEED = 30
SPEED_INCREMENT = 0.001
MAX_SPEED = 100

# Obstáculos
OBSTACLE_MIN_GAP = 200
OBSTACLE_MAX_GAP = 400
CACTUS_TYPES = [(20, 40), (30, 50), (40, 60)]  # (largura, altura)

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# FPS
FPS = 60

# População
POPULATION_SIZE = 50
