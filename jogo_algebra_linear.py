import math
import sys
import numpy as np
import pygame

# ============================================================
# JOGO DE PLATAFORMA 2D
# Álgebra Linear aplicada a Jogos
#
# Dependências:
#   pip install pygame numpy
#
# Controles:
#   A / D ou setas: mover
#   W / Espaço: pular
#   R: reiniciar
#   ESC: sair
#
# Conceitos de Álgebra Linear presentes:
#   - vetores em R^2
#   - base canônica
#   - soma de vetores
#   - multiplicação por escalar
#   - norma e distância
#   - normalização
#   - produto interno
#   - matriz de rotação
#   - transformação linear
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1000, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Álgebra Linear - Platform Hunter")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 22)
title_font = pygame.font.Font(None, 36)

# ------------------------------------------------------------
# Mundo
# ------------------------------------------------------------

WORLD_WIDTH = 2400
WORLD_HEIGHT = 900
GRAVITY = 1200.0

# Base canônica de R^2:
E1 = np.array([1.0, 0.0])
E2 = np.array([0.0, 1.0])

# ------------------------------------------------------------
# Plataformas
# Cada plataforma: x, y, largura, altura
# ------------------------------------------------------------

platforms = [
    pygame.Rect(0, 540, 700, 60),
    pygame.Rect(780, 470, 260, 40),
    pygame.Rect(1120, 390, 260, 40),
    pygame.Rect(1450, 500, 300, 40),
    pygame.Rect(1780, 410, 280, 40),
    pygame.Rect(2120, 520, 280, 60),
    pygame.Rect(900, 650, 300, 35),
    pygame.Rect(1320, 700, 280, 35),
]

goal_rect = pygame.Rect(2320, 440, 30, 80)

# ------------------------------------------------------------
# Cores
# ------------------------------------------------------------

BG = (25, 30, 42)
PLATFORM_COLOR = (85, 105, 130)
PLAYER_COLOR = (70, 180, 255)
ENEMY_COLOR = (235, 80, 90)
TEXT_COLOR = (235, 240, 245)
VISION_COLOR = (240, 190, 70)
GOAL_COLOR = (90, 220, 120)
SHIELD_COLOR = (130, 230, 255)
PROJECTILE_COLOR = (255, 230, 80)

# ------------------------------------------------------------
# Funções de Álgebra Linear
# ------------------------------------------------------------

def normalize(v):
    """Retorna v / ||v||. Para vetor nulo, retorna o próprio vetor."""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v.copy()
    return v / norm


def rotation_matrix(theta):
    """Matriz de rotação 2D."""
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([
        [c, -s],
        [s,  c]
    ], dtype=float)


def transform_points(points, position, angle, scale=1.0):
    """
    Aplica escala, rotação e translação aos pontos locais.
    A transformação linear é feita por matrizes; a translação
    é aplicada depois.
    """
    S = np.array([
        [scale, 0.0],
        [0.0, scale]
    ])

    R = rotation_matrix(angle)
    A = R @ S

    result = []
    for point in points:
        p = np.array(point, dtype=float)
        world = A @ p + position
        result.append(tuple(world))
    return result


# ------------------------------------------------------------
# Classe Escudo Orbital (Álgebra Linear: Rotações e Afim)
# ------------------------------------------------------------

class OrbitalShield:
    def __init__(self, num_orbs=2, radius=55.0, angular_speed=3.0):
        self.num_orbs = num_orbs
        self.radius = radius
        self.angular_speed = angular_speed  # omega em radianos/segundo
        self.angle = 0.0
        self.orb_radius = 8.0

    def update(self, dt):
        # theta(t + dt) = theta(t) + omega * dt
        self.angle = (self.angle + self.angular_speed * dt) % (2.0 * math.pi)

    def get_orb_positions(self, center_pos):
        """
        Calcula as posições no espaço do mundo para cada orbe usando:
        p_orbe = center_pos + R(theta_i) @ [radius, 0]
        """
        positions = []
        base_vector = np.array([self.radius, 0.0], dtype=float)

        for i in range(self.num_orbs):
            # Defasagem angular uniforme: 2 * pi * i / N
            theta_i = self.angle + (2.0 * math.pi * i / self.num_orbs)
            R = rotation_matrix(theta_i)
            # Transformação afim: rotação da base + translação para o centro
            orb_world_pos = center_pos + R @ base_vector
            positions.append(orb_world_pos)
        return positions

    def check_enemy_collision(self, enemy, center_pos):
        """
        Verifica colisão entre os orbes e o inimigo através do cálculo de
        distância euclidiana (norma de vetor diferença).
        Se colidir, empurra o inimigo usando o vetor normal de impacto.
        """
        orb_positions = self.get_orb_positions(center_pos)
        collided = False

        for orb_pos in orb_positions:
            diff = enemy.pos - orb_pos
            dist = np.linalg.norm(diff)
            min_dist = self.orb_radius + 20.0  # raio aproximado do inimigo

            if 0 < dist < min_dist:
                # Vetor normal unitário de impacto: n = diff / ||diff||
                impact_normal = diff / dist
                # Aplica impulso vetorial no inimigo (empurrão)
                enemy.pos += impact_normal * (min_dist - dist + 15.0)
                enemy.velocity += impact_normal * 280.0
                collided = True

        return collided


# ------------------------------------------------------------
# Classe Projétil (Álgebra Linear: Vetor Direção, Versor e Cinemática)
# ------------------------------------------------------------

class Projectile:
    def __init__(self, start_pos, target_pos, speed=650.0):
        self.pos = np.array(start_pos, dtype=float)
        self.speed = speed
        self.radius = 5.0
        self.alive = True
        self.max_lifetime = 3.0  # segundos
        self.lifetime = 0.0

        # Vetor diferença (alvo - origem)
        direction = target_pos - self.pos
        dist = np.linalg.norm(direction)

        # Versor unitário: u = d / ||d||
        if dist > 0:
            self.direction_unit = direction / dist
        else:
            self.direction_unit = np.array([1.0, 0.0])

        # Velocidade vetorial: v = speed * u
        self.velocity = self.speed * self.direction_unit

    def update(self, dt):
        self.lifetime += dt
        if self.lifetime >= self.max_lifetime:
            self.alive = False

        # Integração cinemática linear: p(t + dt) = p(t) + v * dt
        self.pos += self.velocity * dt

        # Destrói se sair do mundo
        if (self.pos[0] < 0 or self.pos[0] > WORLD_WIDTH or
                self.pos[1] < 0 or self.pos[1] > WORLD_HEIGHT):
            self.alive = False

    def check_enemy_hit(self, enemy):
        """Verifica se o projétil atingiu o inimigo por distância euclidiana."""
        diff = enemy.pos - self.pos
        dist = np.linalg.norm(diff)
        if dist <= self.radius + 20.0:  # raio de colisão do inimigo
            self.alive = False
            enemy.reset()  # Reinicia o inimigo
            return True
        return False

    def check_platform_collision(self, platforms):
        """Colisão simples com plataformas (destrói o projétil ao colidir)."""
        rect = pygame.Rect(
            int(self.pos[0] - self.radius),
            int(self.pos[1] - self.radius),
            int(self.radius * 2),
            int(self.radius * 2)
        )
        for platform in platforms:
            if rect.colliderect(platform):
                self.alive = False
                break


# ------------------------------------------------------------
# Classe Jogador
# ------------------------------------------------------------

class Player:
    def __init__(self):
        self.shield = OrbitalShield(num_orbs=2, radius=55.0, angular_speed=3.0)
        self.reset()

    def reset(self):
        self.pos = np.array([120.0, 450.0], dtype=float)
        self.velocity = np.array([0.0, 0.0], dtype=float)
        self.width = 36
        self.height = 50
        self.speed = 260.0
        self.jump_speed = -600.0
        self.on_ground = False

    @property
    def rect(self):
        return pygame.Rect(
            int(self.pos[0]),
            int(self.pos[1]),
            self.width,
            self.height
        )

    @property
    def center(self):
        return self.pos + np.array([
            self.width / 2,
            self.height / 2
        ])

    def update(self, dt, keys):
        # Vetor de movimento horizontal.
        move = 0.0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move += 1.0

        self.velocity[0] = move * self.speed

        if (keys[pygame.K_w] or keys[pygame.K_SPACE]
                or keys[pygame.K_UP]) and self.on_ground:
            self.velocity[1] = self.jump_speed
            self.on_ground = False

        # Gravidade como vetor.
        gravity = np.array([0.0, GRAVITY])
        self.velocity += gravity * dt

        # Atualização de posição:
        # p(t + dt) = p(t) + v * dt
        self.pos += self.velocity * dt

        self._resolve_collisions()

        # Limites horizontais do mundo.
        self.pos[0] = max(0, min(self.pos[0], WORLD_WIDTH - self.width))

        # Queda fora do mundo.
        if self.pos[1] > WORLD_HEIGHT:
            self.reset()

        # Atualiza a rotação do escudo orbital
        self.shield.update(dt)

    def _resolve_collisions(self):
        rect = self.rect
        self.on_ground = False

        # Colisão vertical simplificada.
        for platform in platforms:
            if rect.colliderect(platform):
                previous_bottom = self.pos[1] + self.height - self.velocity[1] / FPS

                # Pousando sobre a plataforma.
                if self.velocity[1] >= 0 and previous_bottom <= platform.top + 8:
                    self.pos[1] = platform.top - self.height
                    self.velocity[1] = 0
                    self.on_ground = True
                    rect = self.rect

                # Batendo na parte inferior.
                elif self.velocity[1] < 0 and self.pos[1] >= platform.bottom - 5:
                    self.pos[1] = platform.bottom
                    self.velocity[1] = 0
                    rect = self.rect


# ------------------------------------------------------------
# Classe Inimigo
# ------------------------------------------------------------

class Enemy:
    def __init__(self):
        self.reset()

    def reset(self):
        self.pos = np.array([560.0, 455.0], dtype=float)
        self.velocity = np.array([0.0, 0.0], dtype=float)
        self.max_speed = 115.0
        self.vision_distance = 420.0

        # Campo de visão de 80 graus.
        self.fov_half_angle = math.radians(40.0)
        self.fov_threshold = math.cos(self.fov_half_angle)

        # Direção inicial: o jogador começa à esquerda do inimigo,
        # então o inimigo começa olhando para a esquerda.
        self.forward = np.array([-1.0, 0.0], dtype=float)

        # Ângulo usado na transformação matricial.
        self.angle = math.pi

    @property
    def rect(self):
        return pygame.Rect(
            int(self.pos[0] - 20),
            int(self.pos[1] - 20),
            40,
            40
        )

    def update(self, player, dt):
        # Vetor do inimigo até o jogador.
        direction = player.center - self.pos

        distance = np.linalg.norm(direction)

        if distance > 0:
            direction_unit = direction / distance
        else:
            direction_unit = np.zeros(2)

        # Produto interno entre direção para frente
        # e direção do alvo.
        dot = float(np.dot(self.forward, direction_unit))

        # Decide se o jogador está dentro do campo de visão.
        can_see_player = (
            distance <= self.vision_distance
            and dot >= self.fov_threshold
        )

        if can_see_player:
            # O inimigo persegue o jogador.
            self.velocity = self.max_speed * direction_unit

            # O ângulo acompanha a direção.
            self.angle = math.atan2(
                direction_unit[1],
                direction_unit[0]
            )

            # Atualiza o vetor forward usando rotação.
            self.forward = rotation_matrix(self.angle) @ E1
        else:
            # Patrulha simples para a esquerda.
            # O vetor forward precisa corresponder ao sentido da patrulha.
            self.velocity = np.array([-50.0, 0.0])

            self.angle = math.pi
            self.forward = -E1

        self.pos += self.velocity * dt

        # Mantém o inimigo em uma região jogável.
        self.pos[0] = max(120, min(self.pos[0], 900))

        # Se encostar no jogador, o jogo reinicia.
        if self.rect.colliderect(player.rect):
            player.reset()
            self.reset()

        return distance, dot, can_see_player


# ------------------------------------------------------------
# Desenho do inimigo usando transformação matricial
# ------------------------------------------------------------

def draw_enemy(surface, enemy, camera_x):
    # Triângulo no sistema de coordenadas local.
    local_points = [
        (28, 0),
        (-18, -16),
        (-18, 16)
    ]

    # Transformação:
    # p_world = R(theta) S p_local + position
    world_points = transform_points(
        local_points,
        enemy.pos,
        enemy.angle,
        scale=1.0
    )

    screen_points = [
        (int(x - camera_x), int(y))
        for x, y in world_points
    ]

    pygame.draw.polygon(surface, ENEMY_COLOR, screen_points)


def draw_player(surface, player, camera_x):
    rect = player.rect.copy()
    rect.x -= int(camera_x)
    pygame.draw.rect(surface, PLAYER_COLOR, rect, border_radius=6)


def draw_shield(surface, player, camera_x):
    orb_positions = player.shield.get_orb_positions(player.center)
    for orb_pos in orb_positions:
        screen_x = int(orb_pos[0] - camera_x)
        screen_y = int(orb_pos[1])
        pygame.draw.circle(surface, SHIELD_COLOR, (screen_x, screen_y), int(player.shield.orb_radius))
        pygame.draw.circle(surface, (255, 255, 255), (screen_x, screen_y), int(player.shield.orb_radius - 3))


def draw_projectiles(surface, projectiles, camera_x):
    for p in projectiles:
        screen_x = int(p.pos[0] - camera_x)
        screen_y = int(p.pos[1])
        pygame.draw.circle(surface, PROJECTILE_COLOR, (screen_x, screen_y), int(p.radius))
        pygame.draw.circle(surface, (255, 255, 255), (screen_x, screen_y), int(p.radius - 2))


def draw_aim_line(surface, player, camera_x):
    mouse_screen = np.array(pygame.mouse.get_pos(), dtype=float)
    mouse_world = mouse_screen + np.array([camera_x, 0.0])
    diff = mouse_world - player.center
    dist = np.linalg.norm(diff)
    if dist > 0:
        unit = diff / dist
        start = (int(player.center[0] - camera_x), int(player.center[1]))
        end = (
            int(player.center[0] - camera_x + unit[0] * 55),
            int(player.center[1] + unit[1] * 55)
        )
        pygame.draw.line(surface, (200, 240, 255), start, end, 2)


def draw_platforms(surface, camera_x):
    for platform in platforms:
        rect = platform.copy()
        rect.x -= int(camera_x)
        pygame.draw.rect(surface, PLATFORM_COLOR, rect, border_radius=4)


def draw_goal(surface, camera_x):
    rect = goal_rect.copy()
    rect.x -= int(camera_x)

    pygame.draw.rect(surface, GOAL_COLOR, rect)

    # Bandeira simples.
    pygame.draw.line(
        surface,
        GOAL_COLOR,
        (rect.left, rect.top),
        (rect.left, rect.top - 60),
        4
    )

    pygame.draw.polygon(
        surface,
        GOAL_COLOR,
        [
            (rect.left + 2, rect.top - 58),
            (rect.left + 35, rect.top - 48),
            (rect.left + 2, rect.top - 38),
        ]
    )


def draw_vision(surface, enemy, camera_x, distance, dot, can_see):
    # Apenas uma visualização aproximada do campo de visão.
    # O cálculo matemático real está no método update().
    radius = min(enemy.vision_distance, 260)

    center = (
        int(enemy.pos[0] - camera_x),
        int(enemy.pos[1])
    )

    # Circunferência de detecção.
    pygame.draw.circle(
        surface,
        VISION_COLOR,
        center,
        int(radius),
        1
    )

    # Direção do inimigo.
    direction = enemy.forward * radius
    end = (
        int(center[0] + direction[0]),
        int(center[1] + direction[1])
    )

    pygame.draw.line(
        surface,
        VISION_COLOR,
        center,
        end,
        2
    )


def draw_hud(surface, player, enemy, distance, dot, can_see, projectiles_count):
    title = title_font.render(
        "Platform Hunter - Álgebra Linear",
        True,
        TEXT_COLOR
    )
    surface.blit(title, (18, 16))

    lines = [
        f"Player position = ({player.pos[0]:.1f}, {player.pos[1]:.1f})",
        f"Player velocity = ({player.velocity[0]:.1f}, {player.velocity[1]:.1f})",
        f"Enemy position  = ({enemy.pos[0]:.1f}, {enemy.pos[1]:.1f})",
        f"distance = {distance:.2f}",
        f"forward . direction_unit = {dot:.3f}",
        f"field of view = {'SIM' if can_see else 'NAO'}",
        f"Shield orbit angle = {math.degrees(player.shield.angle):.1f}° (R(θ) @ r_0)",
        f"Active projectiles = {projectiles_count} (v = s * u)",
        "A/D: mover | W/Espaco: pular | Clique Mouse: disparar | R: reiniciar",
    ]

    y = 58
    for line in lines:
        text = small_font.render(line, True, TEXT_COLOR)
        surface.blit(text, (18, y))
        y += 23


def draw_background(surface, camera_x):
    surface.fill(BG)

    # Grade para reforçar a interpretação das posições como vetores.
    grid_size = 50
    start_x = -(int(camera_x) % grid_size)

    for x in range(start_x, WIDTH, grid_size):
        pygame.draw.line(surface, (38, 44, 58), (x, 0), (x, HEIGHT), 1)

    for y in range(0, HEIGHT, grid_size):
        pygame.draw.line(surface, (38, 44, 58), (0, y), (WIDTH, y), 1)


# ------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------

def main():
    player = Player()
    enemy = Enemy()
    projectiles = []
    camera_x = 0.0

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    player.reset()
                    enemy.reset()
                    projectiles.clear()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Converte coordenadas da tela para o espaço do mundo: p_world = p_screen + [camera_x, 0]
                    mouse_screen = np.array(event.pos, dtype=float)
                    mouse_world = mouse_screen + np.array([camera_x, 0.0])
                    projectiles.append(Projectile(player.center, mouse_world))

        keys = pygame.key.get_pressed()

        player.update(dt, keys)
        player.shield.check_enemy_collision(enemy, player.center)

        # Atualiza projéteis
        for p in projectiles:
            p.update(dt)
            p.check_platform_collision(platforms)
            p.check_enemy_hit(enemy)
        projectiles = [p for p in projectiles if p.alive]

        distance, dot, can_see = enemy.update(player, dt)

        # Vitória.
        if player.rect.colliderect(goal_rect):
            player.reset()
            enemy.reset()
            projectiles.clear()

        # Câmera acompanha o jogador.
        camera_x = player.pos[0] - WIDTH * 0.35
        camera_x = max(0, min(camera_x, WORLD_WIDTH - WIDTH))

        # Desenho.
        draw_background(screen, camera_x)
        draw_platforms(screen, camera_x)
        draw_goal(screen, camera_x)
        draw_vision(screen, enemy, camera_x, distance, dot, can_see)
        draw_enemy(screen, enemy, camera_x)
        draw_player(screen, player, camera_x)
        draw_shield(screen, player, camera_x)
        draw_aim_line(screen, player, camera_x)
        draw_projectiles(screen, projectiles, camera_x)
        draw_hud(screen, player, enemy, distance, dot, can_see, len(projectiles))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
