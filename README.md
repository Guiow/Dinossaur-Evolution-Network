# PigAI – Evolução de Agentes no Jogo do Dinossauro

Projeto desenvolvido para a disciplina de **Redes Neurais** da **UESB**, apresentando uma simulação de agentes treinados com **algoritmos evolutivos** para jogar uma versão personalizada do clássico jogo do dinossauro.

O personagem principal é o **PigAI**, um porco que aprende a desviar dos obstáculos por meio de uma rede neural evolutiva.

## Objetivo

Demonstrar o uso de algoritmos evolutivos para treinar redes neurais simples, observando como a população melhora geração após geração até alcançar um bom desempenho no jogo.

## Como executar

1. Clone o repositório: 
    - **git clone https://github.com/seu-usuario/redes-neurais-evolutivas.git**
    - **cd redes-neurais-evolutivas**

2. Instale as dependências: **pip install -r requirements.txt**

3. Execute o projeto: **python main.py**

A interface permite iniciar um novo treinamento ou continuar um progresso salvo anteriormente.

## Estrutura básica

- **main.py** — Início da aplicação.
- **training.py** — Execução do algoritmo evolutivo.
- **ai/** — Rede neural e lógica evolutiva.
- **game/** — Mecânicas do jogo e obstáculos.
- **ui/** — Interface gráfica.
