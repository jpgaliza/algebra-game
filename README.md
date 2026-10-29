# Platform Hunter - Álgebra Linear Aplicada a Jogos 2D

Projeto de jogo de plataforma 2D desenvolvido em Python utilizando **Pygame** e **NumPy**, com foco na aplicação prática e visual de conceitos fundamentais de **Álgebra Linear** no desenvolvimento de jogos digitais.

---

## 🎮 Sobre o Jogo

O jogador controla um personagem que deve navegar pelo cenário de plataformas, evitar ser detectado e capturado por um inimigo inteligente provido de campo de visão cônico vetorial, e alcançar a bandeira verde de chegada.

O jogo conta com funcionalidades estendidas de combate e defesa totalmente fundamentadas em Álgebra Linear:
- **Escudo Orbital Protetor**: Orbes em rotação paramétrica afim que repelem o inimigo por impacto de vetor normal.
- **Mira e Disparo de Projéteis**: Cálculo em tempo real do versor unitário em direção ao cursor do mouse.
- **Física de Ricochete Especular**: Projéteis rebatem em plataformas aplicando a fórmula de reflexão vetorial com produto interno e normais de superfície.

### Controles
| Tecla / Ação | Função |
| :--- | :--- |
| **A / D** ou **Setas** | Movimentar horizontalmente |
| **W / Espaço / Seta Cima** | Pular |
| **Botão Esquerdo do Mouse** | Mirar e disparar projéteis |
| **R** | Reiniciar a partida |
| **ESC** | Sair do jogo |

---

## 📊 Matriz de Correlação: Matemática vs. Código-Fonte

A tabela a seguir correlaciona diretamente os conceitos teóricos de Álgebra Linear com sua implementação exata em [`jogo_algebra_linear.py`](jogo_algebra_linear.py):

| Conceito Matemático | Notação / Expressão | Trecho / Função | Linhas no Código |
| :--- | :--- | :--- | :--- |
| **Base Canônica de $\mathbb{R}^2$** | $\mathbf{e}_1 = [1, 0]^T$, $\mathbf{e}_2 = [0, 1]^T$ | Constantes globais | [L53–L54](jogo_algebra_linear.py#L53-L54) |
| **Normalização de Vetores** | $\mathbf{\hat{v}} = \frac{\mathbf{v}}{\|\mathbf{v}\|}$ | `normalize(v)` | [L92–L97](jogo_algebra_linear.py#L92-L97) |
| **Matriz de Rotação 2D** | $R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}$ | `rotation_matrix(theta)` | [L100–L107](jogo_algebra_linear.py#L100-L107) |
| **Transformações Afins Locais** | $\mathbf{p}_{\text{mundo}} = R \cdot S \cdot \mathbf{p}_{\text{local}} + \mathbf{t}$ | `transform_points(...)` | [L110–L129](jogo_algebra_linear.py#L110-L129) |
| **Rotação Paramétrica no Tempo (Escudo)** | $\mathbf{p}_{\text{orbe}} = \mathbf{p} + R(\omega t + \phi)\mathbf{r}_0$ | `OrbitalShield.get_orb_positions` | [L148–L163](jogo_algebra_linear.py#L148-L163) |
| **Impulso por Vetor Normal** | $\mathbf{\hat{n}} = \frac{\mathbf{d}}{\|\mathbf{d}\|}, \quad \Delta\mathbf{v} = k \mathbf{\hat{n}}$ | `OrbitalShield.check_enemy_collision` | [L165–L186](jogo_algebra_linear.py#L165-L186) |
| **Subtração Vetorial e Versor de Mira** | $\mathbf{d} = \mathbf{p}_{\text{alvo}} - \mathbf{p}_{\text{origem}}, \ \mathbf{\hat{u}} = \frac{\mathbf{d}}{\|\mathbf{d}\|}$ | `Projectile.__init__` | [L195–L215](jogo_algebra_linear.py#L195-L215) |
| **Reflexão Especular (Ricochete)** | $\mathbf{v}' = \mathbf{v} - 2(\mathbf{v} \cdot \mathbf{\hat{n}})\mathbf{\hat{n}}$ | `Projectile.check_platform_collision` | [L241–L294](jogo_algebra_linear.py#L241-L294) |
| **Cinemática e Método de Euler** | $\mathbf{p}_{t+dt} = \mathbf{p}_t + \mathbf{v}dt, \ \mathbf{v}_{t+dt} = \mathbf{v}_t + \mathbf{g}dt$ | `Player.update` | [L348–L356](jogo_algebra_linear.py#L348-L356) |
| **Vetor Distância Euclidiana (Norma)** | $\|\mathbf{d}\| = \sqrt{d_x^2 + d_y^2}$ | `Enemy.update` | [L425–L432](jogo_algebra_linear.py#L425-L432) |
| **Produto Interno e Campo de Visão** | $\mathbf{f} \cdot \mathbf{\hat{u}} = \cos\theta \ge \cos(\theta_{\text{limite}})$ | `Enemy.update` | [L434–L443](jogo_algebra_linear.py#L434-L443) |
| **Desenho com Transformação Matricial** | $R(\theta) \cdot \text{vértices} + \mathbf{p}_{\text{inimigo}}$ | `draw_enemy` | [L483–L505](jogo_algebra_linear.py#L483-L505) |

---

## 📐 Detalhamento Teórico dos Conceitos

### 1. Espaço Vetorial $\mathbb{R}^2$ e Base Canônica
O cenário do jogo é modelado sobre o plano euclidiano bidimensional. Os eixos ortogonais fundamentais são representados pelos vetores unitários da base canônica:
$$\mathbf{e}_1 = \begin{bmatrix} 1 \\ 0 \end{bmatrix} \quad (\text{eixo horizontal } X), \qquad \mathbf{e}_2 = \begin{bmatrix} 0 \\ 1 \end{bmatrix} \quad (\text{eixo vertical } Y)$$

Qualquer direção ou posição pode ser expressa como combinação linear $\mathbf{v} = v_x \mathbf{e}_1 + v_y \mathbf{e}_2$.

### 2. Campo de Visão (FOV) com Produto Interno
Para determinar se o jogador está visível para o inimigo, evita-se o cálculo computacionalmente custoso de funções trigonométricas inversas ($\arccos$). Em vez disso, utiliza-se a relação fundamental do produto escalar:
$$\mathbf{f} \cdot \mathbf{\hat{u}} = \|\mathbf{f}\| \|\mathbf{\hat{u}}\| \cos\theta$$

Como tanto o vetor de visão frontal do inimigo ($\mathbf{f}$) quanto o vetor de direção até o jogador ($\mathbf{\hat{u}}$) são **normalizados** ($\|\mathbf{f}\| = \|\mathbf{\hat{u}}\| = 1$), a equação simplifica-se para:
$$\mathbf{f} \cdot \mathbf{\hat{u}} = \cos\theta$$

Para um campo de visão cônico com semi-ângulo $\theta_{\text{max}} = 40^\circ$:
$$\text{Visível} \iff \mathbf{f} \cdot \mathbf{\hat{u}} \ge \cos(40^\circ) \quad \text{e} \quad \|\mathbf{d}\| \le \text{distância\_máxima}$$

### 3. Matrizes de Rotação e Transformações Afins
O inimigo e o escudo orbital utilizam matrizes de rotação no plano:
$$R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}$$

- **Escudo Orbital:** Rotaciona continuamente os vetores radiais dos orbes defasados por $\frac{2\pi}{N}$ radianos:
  $$\mathbf{p}_{\text{orbe}, i} = \mathbf{p}_{\text{jogador}} + R\left(\omega t + \frac{2\pi i}{N}\right) \begin{bmatrix} r \\ 0 \end{bmatrix}$$
- **Vértices do Inimigo:** Definidos em coordenadas locais relativas à sua origem e transformados para coordenadas do mundo via:
  $$\mathbf{p}_{\text{mundo}} = R(\theta) \cdot S(s) \cdot \mathbf{p}_{\text{local}} + \mathbf{p}_{\text{inimigo}}$$

### 4. Mira com Versores e Disparo
Ao clicar na tela, a coordenada de tela do mouse é convertida para o mundo pela translação com o vetor da câmera:
$$\mathbf{p}_{\text{mouse\_mundo}} = \mathbf{p}_{\text{mouse\_tela}} + \begin{bmatrix} \text{camera\_x} \\ 0 \end{bmatrix}$$
Obtém-se o vetor deslocamento $\mathbf{d} = \mathbf{p}_{\text{mouse\_mundo}} - \mathbf{p}_{\text{jogador\_centro}}$ e seu respectivo versor:
$$\mathbf{\hat{u}} = \frac{\mathbf{d}}{\|\mathbf{d}\|}$$
A velocidade vetorial do projétil é obtida por multiplicação escalar: $\mathbf{v} = v_{\text{tiro}} \cdot \mathbf{\hat{u}}$.

### 5. Reflexão Vetorial Especular (Ricochete)
Quando o projétil atinge uma plataforma, sua velocidade incidente $\mathbf{v}$ decompõe-se ortogonalmente em relação à normal $\mathbf{\hat{n}}$ da superfície (obtida a partir dos vetores canônicos $\pm\mathbf{e}_1, \pm\mathbf{e}_2$):
- Componente normal (projeção ortogonal): $\mathbf{v}_{\perp} = (\mathbf{v} \cdot \mathbf{\hat{n}})\mathbf{\hat{n}}$
- Componente tangencial: $\mathbf{v}_{\parallel} = \mathbf{v} - (\mathbf{v} \cdot \mathbf{\hat{n}})\mathbf{\hat{n}}$

A reflexão inverte exclusivamente a componente normal, mantendo a componente tangencial:
$$\mathbf{v}' = \mathbf{v}_{\parallel} - \mathbf{v}_{\perp} = \mathbf{v} - 2(\mathbf{v} \cdot \mathbf{\hat{n}})\mathbf{\hat{n}}$$

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.10 ou superior
- Pip instalado

### Instalação das dependências
```bash
# Recomendado (compatível com todas as versões do Python e macOS Apple Silicon):
pip install pygame-ce numpy

# Ou a versão tradicional do pygame:
pip install pygame numpy
```

### Executando o jogo
```bash
python jogo_algebra_linear.py
```
