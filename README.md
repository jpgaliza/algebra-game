# Platform Hunter - Álgebra Linear Aplicada a Jogos 2D

Projeto de jogo de plataforma 2D desenvolvido em Python utilizando **Pygame** e **NumPy**, com foco na aplicação prática de conceitos de **Álgebra Linear** no desenvolvimento de jogos.

---

## 🎮 Sobre o Jogo

O jogador controla um personagem que deve navegar pelo cenário de plataformas, evitar ser detectado e capturado por um inimigo inteligente que utiliza cálculos vetoriais para visão e perseguição, e alcançar o objetivo (bandeira verde) ao final da fase.

### Controles
- **A / D** ou **Setas Esquerda/Direita**: Movimentar horizontalmente
- **W / Espaço / Seta Cima**: Pular
- **R**: Reiniciar o jogo
- **ESC**: Sair do jogo

---

## 📐 Conceitos de Álgebra Linear Aplicados

Este projeto serve como demonstração prática dos seguintes tópicos matemáticos:

### 1. Espaço Vetorial $\mathbb{R}^2$ e Base Canônica
- O mundo e a tela são tratados como o espaço euclidiano $\mathbb{R}^2$.
- São definidos os vetores da base canônica:
  $$\mathbf{e}_1 = \begin{bmatrix} 1 \\ 0 \end{bmatrix}, \quad \mathbf{e}_2 = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$$
- $\mathbf{e}_1$ orienta o eixo horizontal e $\mathbf{e}_2$ orienta o eixo vertical.

### 2. Vetores de Estado e Cinemática
- **Posição e Velocidade:** Posição $\mathbf{p} \in \mathbb{R}^2$ e velocidade $\mathbf{v} \in \mathbb{R}^2$.
- **Gravidade como Vetor:** $\mathbf{g} = [0, 1200]^T$.
- **Integração no Tempo (Método de Euler):**
  $$\mathbf{v}(t + \Delta t) = \mathbf{v}(t) + \mathbf{g} \Delta t$$
  $$\mathbf{p}(t + \Delta t) = \mathbf{p}(t) + \mathbf{v}(t) \Delta t$$

### 3. Vetor Deslocamento e Distância Euclidiana (Norma)
- O vetor que liga o inimigo ao centro do jogador é obtido pela diferença vetorial:
  $$\mathbf{d} = \mathbf{p}_{\text{jogador}} - \mathbf{p}_{\text{inimigo}}$$
- A distância euclidiana é dada pela norma $L_2$:
  $$\|\mathbf{d}\| = \sqrt{d_x^2 + d_y^2} = \text{np.linalg.norm}(\mathbf{d})$$

### 4. Normalização e Versores (Vetores Unitários)
- Para obter a direção pura de perseguição desacoplada da distância:
  $$\mathbf{\hat{u}} = \frac{\mathbf{d}}{\|\mathbf{d}\|}, \quad \text{onde } \|\mathbf{\hat{u}}\| = 1$$
- A velocidade de perseguição é dada por multiplicação por escalar:
  $$\mathbf{v}_{\text{inimigo}} = v_{\text{max}} \cdot \mathbf{\hat{u}}$$

### 5. Produto Interno e Campo de Visão (Field of View - FOV)
- O produto escalar entre a direção para onde o inimigo olha ($\mathbf{f}$) e o vetor unitário em direção ao jogador ($\mathbf{\hat{u}}$) fornece o cosseno do ângulo $\theta$ entre eles:
  $$\mathbf{f} \cdot \mathbf{\hat{u}} = \|\mathbf{f}\| \|\mathbf{\hat{u}}\| \cos\theta = \cos\theta$$
- O jogador é detectado no cone de visão se e somente se:
  $$\|\mathbf{d}\| \le \text{distância\_visão} \quad \text{e} \quad \mathbf{f} \cdot \mathbf{\hat{u}} \ge \cos(\theta_{\text{abertura}})$$

### 6. Matrizes de Transformação Linear (Escala e Rotação)
- A geometria do inimigo é definida em coordenadas locais e transformada para coordenadas de mundo através de:
  $$R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}, \quad S(s) = \begin{bmatrix} s & 0 \\ 0 & s \end{bmatrix}$$
  $$\mathbf{p}_{\text{mundo}} = (R \cdot S) \mathbf{p}_{\text{local}} + \mathbf{p}_{\text{inimigo}}$$

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10 ou superior
- Pip

### Instalação das dependências
```bash
pip install pygame numpy
```

### Executando o jogo
```bash
python jogo_algebra_linear.py
```
