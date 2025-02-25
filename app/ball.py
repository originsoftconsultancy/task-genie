import pygame
import math

# Initialize Pygame
pygame.init()

# Screen setup
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing Ball in Spinning Hexagon")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Hexagon parameters
hex_radius = 300
num_sides = 6
original_vertices = []
for i in range(num_sides):
    angle = math.radians(i * 60)
    x = hex_radius * math.cos(angle)
    y = hex_radius * math.sin(angle)
    original_vertices.append((x, y))

# Ball parameters
ball_radius = 15
ball_pos = [0.0, 0.0]
ball_vel = [5.0, 0.0]
gravity = 0.5
friction = 0.99
cor = 0.8  # Coefficient of restitution

# Rotation parameters
rotation_angle = 0.0
rotation_speed = math.radians(1)

# Center of screen
center = (width // 2, height // 2)

clock = pygame.time.Clock()
running = True


def rotate_point(point, angle):
    x, y = point
    return (
        x * math.cos(angle) - y * math.sin(angle),
        x * math.sin(angle) + y * math.cos(angle)
    )


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update rotation angle
    rotation_angle += rotation_speed

    # Apply physics
    ball_vel[1] += gravity
    ball_vel[0] *= friction
    ball_vel[1] *= friction
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Rotate hexagon vertices
    rotated_vertices = [rotate_point(v, rotation_angle)
                        for v in original_vertices]

    # Collision detection and response
    for i in range(num_sides):
        p0 = rotated_vertices[i]
        p1 = rotated_vertices[(i+1) % num_sides]

        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        length = math.hypot(dx, dy)

        if length == 0:
            continue

        normal = (-dy/length, dx/length)
        tangent = (dx/length, dy/length)

        # Vector from p0 to ball
        vec = (ball_pos[0] - p0[0], ball_pos[1] - p0[1])
        distance = vec[0] * normal[0] + vec[1] * normal[1]

        if distance > ball_radius:
            continue

        projection = vec[0] * tangent[0] + vec[1] * tangent[1]
        if projection < 0 or projection > length:
            continue

        closest_x = p0[0] + projection * tangent[0]
        closest_y = p0[1] + projection * tangent[1]

        # Wall velocity at collision point
        wall_vel = (-rotation_speed * closest_y, rotation_speed * closest_x)

        # Relative velocity
        rel_vel = (ball_vel[0] - wall_vel[0], ball_vel[1] - wall_vel[1])
        vn = rel_vel[0] * normal[0] + rel_vel[1] * normal[1]

        if vn >= 0:
            continue

        # Collision response
        vt = rel_vel[0] * tangent[0] + rel_vel[1] * tangent[1]
        new_vn = -cor * vn
        rel_vel_new = (new_vn * normal[0] + vt * tangent[0],
                       new_vn * normal[1] + vt * tangent[1])

        ball_vel[0] = wall_vel[0] + rel_vel_new[0]
        ball_vel[1] = wall_vel[1] + rel_vel_new[1]

        # Position correction
        penetration = ball_radius - distance
        ball_pos[0] += penetration * normal[0]
        ball_pos[1] += penetration * normal[1]
        break

    # Draw everything
    screen.fill(BLACK)

    # Draw hexagon
    hex_points = [(center[0] + x, center[1] + y) for x, y in rotated_vertices]
    pygame.draw.lines(screen, WHITE, True, hex_points, 2)

    # Draw ball
    pygame.draw.circle(screen, RED,
                       (int(center[0] + ball_pos[0]),
                        int(center[1] + ball_pos[1])),
                       ball_radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
