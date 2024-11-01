import pygame
import math

# Initialize constants
SECTOR_ANGLE = 45  # Each sector is 45 degrees (360/8)
STEP_SIZE = 20     # Calculate direction every 20 pixels
NUM_SECTORS = 8
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 400

# Function to calculate angle between two points
def calculate_angle(p1, p2):
    delta_y = p2[1] - p1[1]
    delta_x = p2[0] - p1[0]
    angle = math.degrees(math.atan2(delta_y, delta_x))
    if angle < 0:
        angle += 360  # Normalize angle to range [0, 360)
    return angle

# Determine sector from angle
def get_sector(angle):
    return int(angle // SECTOR_ANGLE) + 1  # Sectors range from 1 to 8

# Calculate similarity between two lists
def calculate_similarity(list1, list2):
    matches = sum(1 for a, b in zip(list1, list2) if a == b)
    similarity = (matches / max(len(list1), len(list2))) * 100
    return similarity

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Direction Drawing App")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
TEXT_COLOR = (0, 0, 0)

# Main loop variables
running = True
drawing1 = False
drawing2 = False
points1, directions1 = [], []
points2, directions2 = [], []

# Font for displaying text
font = pygame.font.Font(None, 30)

def draw_directions(points, directions, color):
    for i in range(1, len(points)):
        pygame.draw.line(screen, color, points[i-1], points[i], 2)
        angle = calculate_angle(points[i-1], points[i])
        sector = get_sector(angle)
        mid_point = ((points[i-1][0] + points[i][0]) / 2, (points[i-1][1] + points[i][1]) / 2)
        text_surface = font.render(str(sector), True, TEXT_COLOR)
        screen.blit(text_surface, (mid_point[0] + 5, mid_point[1] + 5))

# Main loop
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if event.pos[0] < WINDOW_WIDTH // 2:  # Left canvas
                    drawing1 = True
                    points1 = [event.pos]
                    directions1 = []
                else:  # Right canvas
                    drawing2 = True
                    points2 = [event.pos]
                    directions2 = []
        
        if event.type == pygame.MOUSEMOTION:
            if drawing1:
                new_point = event.pos
                if math.hypot(new_point[0] - points1[-1][0], new_point[1] - points1[-1][1]) >= STEP_SIZE:
                    points1.append(new_point)
                    angle = calculate_angle(points1[-2], new_point)
                    sector = get_sector(angle)
                    directions1.append(sector)

            if drawing2:
                new_point = event.pos
                if math.hypot(new_point[0] - points2[-1][0], new_point[1] - points2[-1][1]) >= STEP_SIZE:
                    points2.append(new_point)
                    angle = calculate_angle(points2[-2], new_point)
                    sector = get_sector(angle)
                    directions2.append(sector)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                if drawing1:
                    drawing1 = False
                else:
                    drawing2 = False

    # Draw current directions
    if points1:
        draw_directions(points1, directions1, RED)
    if points2:
        draw_directions(points2, directions2, BLUE)

    # Calculate similarity if both drawings are complete
    if not drawing1 and not drawing2 and directions1 and directions2:
        similarity = calculate_similarity(directions1, directions2)
        similarity_text = font.render(f"Similarity: {similarity:.2f}%", True, TEXT_COLOR)
        screen.blit(similarity_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 40))

    pygame.display.flip()

# Cleanup
pygame.quit()
