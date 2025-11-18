import pygame

pygame.init()

# Fonty
font20 = pygame.font.Font('freesansbold.ttf', 20)
font_large = pygame.font.Font('freesansbold.ttf', 50)
font_medium = pygame.font.Font('freesansbold.ttf', 30)
font_small = pygame.font.Font('freesansbold.ttf', 24)

# Barvy
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
COLOR_BG = (20, 20, 20)

# Screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

clock = pygame.time.Clock()
FPS = 60


# -------------------------------------------------------------
# STRIKER
# -------------------------------------------------------------
class Striker:
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.geekRect = pygame.Rect(posx, posy, width, height)
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    def display(self):
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    def update(self, yFac):
        self.posy += self.speed * yFac
        if self.posy <= 0:
            self.posy = 0
        elif self.posy + self.height >= HEIGHT:
            self.posy = HEIGHT - self.height
        self.geekRect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def displayScore(self, text, score, x, y, color):
        t = font20.render(text + str(score), True, color)
        rect = t.get_rect(center=(x, y))
        screen.blit(t, rect)

    def getRect(self):
        return self.geekRect


# -------------------------------------------------------------
# BALL
# -------------------------------------------------------------
class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac = 1
        self.yFac = -1
        self.ball = pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)
        self.firstTime = 1

    def display(self):
        self.ball = pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)

    def update(self):
        self.posx += self.speed * self.xFac
        self.posy += self.speed * self.yFac

        if self.posy <= 0 or self.posy >= HEIGHT:
            self.yFac *= -1

        if self.posx <= 0 and self.firstTime:
            self.firstTime = 0
            return 1
        elif self.posx >= WIDTH and self.firstTime:
            self.firstTime = 0
            return -1
        return 0

    def reset(self):
        self.posx = WIDTH // 2
        self.posy = HEIGHT // 2
        self.xFac *= -1
        self.firstTime = 1

    def hit(self):
        self.xFac *= -1

    def getRect(self):
        return self.ball


# -------------------------------------------------------------
# MENU
# -------------------------------------------------------------
def menu():
    player_name = ""
    input_active = False
    mode = "PVP"

    COLOR_ACTIVE = (0, 200, 0)
    COLOR_PASSIVE = (180, 180, 180)
    COLOR_BUTTON = (60, 60, 60)
    COLOR_BUTTON_HOVER = (100, 100, 100)

    while True:
        screen.fill(COLOR_BG)

        title = font_large.render("PONG", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        # Input box
        label = font_small.render("Jméno hráče:", True, WHITE)
        screen.blit(label, (WIDTH // 2 - 150, 150))

        input_rect = pygame.Rect(WIDTH // 2 - 150, 190, 300, 45)
        pygame.draw.rect(screen, COLOR_ACTIVE if input_active else COLOR_PASSIVE, input_rect, border_radius=6)

        name_text = font_small.render(player_name, True, WHITE)
        screen.blit(name_text, (input_rect.x + 10, input_rect.y + 10))

        # Mode buttons
        mode_label = font_small.render("Režim hry:", True, WHITE)
        screen.blit(mode_label, (WIDTH // 2 - 150, 260))

        pvp_button = pygame.Rect(WIDTH // 2 - 150, 300, 300, 40)
        bot_button = pygame.Rect(WIDTH // 2 - 150, 350, 300, 40)

        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if mode == "PVP" else COLOR_BUTTON, pvp_button, border_radius=6)
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if mode == "BOT" else COLOR_BUTTON, bot_button, border_radius=6)

        screen.blit(font_small.render("Hráč vs Hráč", True, WHITE), (pvp_button.x + 80, pvp_button.y + 8))
        screen.blit(font_small.render("Hráč vs Bot", True, WHITE), (bot_button.x + 95, bot_button.y + 8))

        # Start button
        start_button = pygame.Rect(WIDTH // 2 - 100, 430, 200, 50)
        mouse = pygame.mouse.get_pos()
        pygame.draw.rect(screen,
                         (0, 150, 0) if start_button.collidepoint(mouse) else (0, 110, 0),
                         start_button, border_radius=8)

        screen.blit(font_medium.render("START", True, WHITE),
                    (start_button.x + 45, start_button.y + 5))

        # Quit button
        quit_button = pygame.Rect(WIDTH // 2 - 100, 500, 200, 50)
        pygame.draw.rect(screen,
                         (180, 0, 0) if quit_button.collidepoint(mouse) else (140, 0, 0),
                         quit_button, border_radius=8)

        screen.blit(font_medium.render("UKONČIT", True, WHITE),
                    (quit_button.x + 20, quit_button.y + 5))

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False

                if pvp_button.collidepoint(event.pos):
                    mode = "PVP"
                if bot_button.collidepoint(event.pos):
                    mode = "BOT"

                if start_button.collidepoint(event.pos) and player_name != "":
                    return mode, player_name

                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    quit()

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 12:
                    player_name += event.unicode

        pygame.display.update()


# -------------------------------------------------------------
# GAME LOOP
# -------------------------------------------------------------
def main(mode, player_name):
    running = True

    geek1 = Striker(20, 0, 10, 100, 10, GREEN)
    geek2 = Striker(WIDTH - 30, 0, 10, 100, 10, GREEN)
    ball = Ball(WIDTH // 2, HEIGHT // 2, 7, 7, WHITE)

    listOfGeeks = [geek1, geek2]

    geek1Score, geek2Score = 0, 0
    geek1YFac, geek2YFac = 0, 0

    # ---- TLAČÍTKA VE HŘE ----
    pause_button = pygame.Rect(WIDTH - 300, 10, 90, 40)
    menu_button = pygame.Rect(WIDTH - 200, 10, 90, 40)
    quit_button = pygame.Rect(WIDTH - 100, 10, 90, 40)

    while running:
        screen.fill(BLACK)

        mouse = pygame.mouse.get_pos()

        # GUI TLAČÍTKA
        pygame.draw.rect(screen, (60, 60, 60) if not menu_button.collidepoint(mouse) else (100, 100, 100), menu_button, border_radius=6)
        pygame.draw.rect(screen, (140, 0, 0) if not quit_button.collidepoint(mouse) else (180, 0, 0), quit_button, border_radius=6)

        screen.blit(font_small.render("MENU", True, WHITE), (menu_button.x + 12, menu_button.y + 10))
        screen.blit(font_small.render("QUIT", True, WHITE), (quit_button.x + 18, quit_button.y + 10))

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.collidepoint(event.pos):
                    return  # návrat do menu
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    quit()
                if pause_button.collidepoint(event.pos):
                    result = pause_screen()
                    if result == "menu":
                        return  # návrat do menu
                    # "continue" = nic

            # Player controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    geek1YFac = -1
                if event.key == pygame.K_s:
                    geek1YFac = 1

                if mode == "PVP":
                    if event.key == pygame.K_UP:
                        geek2YFac = -1
                    if event.key == pygame.K_DOWN:
                        geek2YFac = 1

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_w, pygame.K_s):
                    geek1YFac = 0
                if mode == "PVP" and event.key in (pygame.K_UP, pygame.K_DOWN):
                    geek2YFac = 0

        # BOT AI
        if mode == "BOT":
            if ball.posy < geek2.posy + geek2.height // 2:
                geek2YFac = -1
            elif ball.posy > geek2.posy + geek2.height // 2:
                geek2YFac = 1
            else:
                geek2YFac = 0

        # Collision
        for geek in listOfGeeks:
            if pygame.Rect.colliderect(ball.getRect(), geek.getRect()):
                ball.hit()

        # Update
        geek1.update(geek1YFac)
        geek2.update(geek2YFac)
        point = ball.update()

        if point == -1:
            geek1Score += 1
        elif point == 1:
            geek2Score += 1

        if point:
            ball.reset()

        # Draw
        geek1.display()
        geek2.display()
        ball.display()

        # ---------------------- DOLNÍ LIŠTA -------------------------

        # Pozadí lišty
        status_bar_height = 50
        pygame.draw.rect(screen, (25, 25, 25), (0, HEIGHT - status_bar_height, WIDTH, status_bar_height))

        # Oddělovací linka
        pygame.draw.line(screen, (60, 60, 60), (0, HEIGHT - status_bar_height), (WIDTH, HEIGHT - status_bar_height), 2)

        # Texty lišty
        left_text = font_small.render(f"{player_name}: {geek1Score}", True, WHITE)
        mode_text = font_small.render(f"Režim: {mode}", True, WHITE)
        ball_speed_text = font_small.render(f"Rychlost: {ball.speed}", True, WHITE)
        right_text = font_small.render(f"GEEK_2: {geek2Score}", True, WHITE)

        # Umístění textů
        screen.blit(left_text, (20, HEIGHT - 35))  # vlevo
        screen.blit(mode_text, (WIDTH // 2 - 120, HEIGHT - 35))  # střed
        screen.blit(ball_speed_text, (WIDTH // 2 + 20, HEIGHT - 35))  # střed vedle režimu
        screen.blit(right_text, (WIDTH - right_text.get_width() - 20, HEIGHT - 35))  # vpravo

        pygame.display.update()
        clock.tick(FPS)

def pause_screen():
    paused = True

    # Tlačítka
    continue_btn = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 - 40, 240, 50)
    menu_btn = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 20, 240, 50)
    quit_btn = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 80, 240, 50)

    while paused:
        screen.fill((0, 0, 0))
        overlay = font_large.render("PAUZA", True, WHITE)
        screen.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 - 130))

        mouse = pygame.mouse.get_pos()

        # Tlačítka s hover efektem
        pygame.draw.rect(screen, (70, 110, 70) if continue_btn.collidepoint(mouse) else (40, 90, 40), continue_btn, border_radius=8)
        pygame.draw.rect(screen, (70, 70, 120) if menu_btn.collidepoint(mouse) else (40, 40, 90), menu_btn, border_radius=8)
        pygame.draw.rect(screen, (160, 0, 0) if quit_btn.collidepoint(mouse) else (110, 0, 0), quit_btn, border_radius=8)

        screen.blit(font_medium.render("POKRAČOVAT", True, WHITE), (continue_btn.x + 20, continue_btn.y + 8))
        screen.blit(font_medium.render("MENU", True, WHITE), (menu_btn.x + 75, menu_btn.y + 8))
        screen.blit(font_medium.render("UKONČIT", True, WHITE), (quit_btn.x + 60, quit_btn.y + 8))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_btn.collidepoint(event.pos):
                    return "continue"
                if menu_btn.collidepoint(event.pos):
                    return "menu"
                if quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    quit()

        pygame.display.update()
        clock.tick(30)

# -------------------------------------------------------------
# RUN
# -------------------------------------------------------------
if __name__ == "__main__":
    while True:
        mode, player_name = menu()
        main(mode, player_name)
