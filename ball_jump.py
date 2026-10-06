import pygame

# --- Settings ---
WIDTH, HEIGHT = 800, 600
FPS = 60
GROUND_Y = HEIGHT - 50

BALL_RADIUS = 20
MOVE_SPEED = 5
JUMP_STRENGTH = 19
GRAVITY = 0.8

POLE_WIDTH = 10  # backboard/pole thickness at each screen edge
RIM_Y = GROUND_Y - 190  # height of the hoops
RIM_WIDTH = 90
BACKBOARD_HEIGHT = 90
NET_DEPTH = 45

PLAYER_NUMBER = 8
PLAYER_SPEED = 6
PLAYER_MIN_X = WIDTH // 2 + 20  # he patrols the right half of the court
PLAYER_MAX_X = WIDTH - POLE_WIDTH - RIM_WIDTH - 10
TIP_LEAD = 12  # frames between the ball's peak and it dropping to rim height
TIP_FRAMES = 30  # how long a tipped ball hangs before dropping through the rim

BG_COLOR = (135, 206, 235)
GROUND_COLOR = (80, 170, 80)
BALL_COLOR = (230, 110, 30)
POLE_COLOR = (90, 90, 90)
BACKBOARD_COLOR = (250, 250, 250)
RIM_COLOR = (220, 60, 20)
NET_COLOR = (255, 255, 255)
TEXT_COLOR = (30, 30, 30)
SCOREBOARD_COLOR = (40, 40, 60)
SCOREBOARD_TEXT = (255, 220, 80)
SKIN_COLOR = (92, 58, 36)
JERSEY_COLOR = (0, 82, 180)
SHORTS_COLOR = (0, 58, 135)
JERSEY_TEXT = (255, 130, 20)
SHOE_COLOR = (245, 245, 245)


class Ball:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = GROUND_Y - BALL_RADIUS
        self.vx = MOVE_SPEED
        self.vy = 0
        self.on_ground = True
        self.tipped = False  # True while a tip-in is on its way to the rim

    def update(self):
        # Volley back and forth, bouncing off the poles at each edge
        self.x += self.vx
        left_limit = POLE_WIDTH + BALL_RADIUS
        right_limit = WIDTH - POLE_WIDTH - BALL_RADIUS
        if self.x <= left_limit:
            self.x = left_limit
            self.vx = abs(self.vx)
        elif self.x >= right_limit:
            self.x = right_limit
            self.vx = -abs(self.vx)

        # Gravity
        self.prev_y = self.y
        self.vy += GRAVITY
        self.y += self.vy

        # Land on the ground
        if self.y >= GROUND_Y - BALL_RADIUS:
            self.y = GROUND_Y - BALL_RADIUS
            self.vy = 0
            self.on_ground = True
            if self.tipped:
                self.end_tip()

    def jump(self):
        if self.on_ground:
            self.vy = -JUMP_STRENGTH
            self.on_ground = False

    def tip_toward(self, target_x):
        # Pop the ball back up so it comes down through the rim at target_x
        self.tipped = True
        self.vy = -GRAVITY * TIP_FRAMES / 2
        self.vx = (target_x - self.x) / TIP_FRAMES

    def end_tip(self):
        # Back to the normal volley, heading away from the right hoop
        self.tipped = False
        self.vx = -MOVE_SPEED

    def draw(self, screen):
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(screen, BALL_COLOR, pos, BALL_RADIUS)
        # Basketball seams
        pygame.draw.line(screen, TEXT_COLOR, (pos[0] - BALL_RADIUS, pos[1]), (pos[0] + BALL_RADIUS, pos[1]), 2)
        pygame.draw.line(screen, TEXT_COLOR, (pos[0], pos[1] - BALL_RADIUS), (pos[0], pos[1] + BALL_RADIUS), 2)


class Hoop:
    def __init__(self, side):
        self.side = side  # "left" or "right"
        if side == "left":
            self.board_x = 0
            self.rim_start = POLE_WIDTH
            self.rim_end = POLE_WIDTH + RIM_WIDTH
        else:
            self.board_x = WIDTH - POLE_WIDTH
            self.rim_start = WIDTH - POLE_WIDTH - RIM_WIDTH
            self.rim_end = WIDTH - POLE_WIDTH
        self.score = 0
        self.flash = 0  # frames left to light up after a basket

    def check_basket(self, ball):
        # A basket counts when the ball's center drops down through the rim
        falling_through = ball.prev_y < RIM_Y <= ball.y
        if falling_through and self.rim_start < ball.x < self.rim_end:
            self.score += 1
            self.flash = FPS // 2
            return True
        return False

    def check_miss(self, ball):
        # A miss is the ball dropping past rim height on this hoop's half of the court, outside the rim
        falling_past = ball.prev_y < RIM_Y <= ball.y
        if self.side == "left":
            on_this_side = ball.x < WIDTH // 2
        else:
            on_this_side = ball.x > WIDTH // 2
        in_rim = self.rim_start < ball.x < self.rim_end
        return falling_past and on_this_side and not in_rim

    def draw(self, screen):
        # Pole and backboard
        pygame.draw.rect(screen, POLE_COLOR, (self.board_x, RIM_Y, POLE_WIDTH, GROUND_Y - RIM_Y))
        pygame.draw.rect(screen, BACKBOARD_COLOR, (self.board_x, RIM_Y - BACKBOARD_HEIGHT, POLE_WIDTH, BACKBOARD_HEIGHT + 10))

        # Net: lines from the rim narrowing toward the bottom
        for i in range(5):
            top_x = self.rim_start + i * RIM_WIDTH / 4
            bottom_x = self.rim_start + RIM_WIDTH * 0.2 + i * RIM_WIDTH * 0.6 / 4
            pygame.draw.line(screen, NET_COLOR, (top_x, RIM_Y), (bottom_x, RIM_Y + NET_DEPTH), 2)
        pygame.draw.line(screen, NET_COLOR, (self.rim_start + RIM_WIDTH * 0.2, RIM_Y + NET_DEPTH),
                         (self.rim_end - RIM_WIDTH * 0.2, RIM_Y + NET_DEPTH), 2)

        # Rim (glows yellow right after a basket)
        rim_color = SCOREBOARD_TEXT if self.flash > 0 else RIM_COLOR
        pygame.draw.line(screen, rim_color, (self.rim_start, RIM_Y), (self.rim_end, RIM_Y), 5)
        if self.flash > 0:
            self.flash -= 1


class Player:
    """Number 8, who hangs around the right hoop and tips in missed shots."""

    LEG = 40
    TORSO = 42
    HEAD_RADIUS = 11

    def __init__(self):
        self.x = PLAYER_MAX_X
        self.y = GROUND_Y  # feet
        self.vy = 0
        self.on_ground = True

    def update(self, ball):
        # Shadow the ball so he is underneath it when a shot comes off
        target = max(PLAYER_MIN_X, min(PLAYER_MAX_X, ball.x))
        if abs(target - self.x) <= PLAYER_SPEED:
            self.x = target
        elif target > self.x:
            self.x += PLAYER_SPEED
        else:
            self.x -= PLAYER_SPEED

        self.vy += GRAVITY
        self.y += self.vy
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            # Timed to peak just as the ball drops to rim height
            self.vy = -GRAVITY * TIP_LEAD
            self.on_ground = False

    def draw(self, screen, font):
        x, feet = int(self.x), int(self.y)
        hip = feet - self.LEG
        shoulder = hip - self.TORSO
        head_y = shoulder - self.HEAD_RADIUS

        # Legs and shoes
        for dx in (-7, 7):
            pygame.draw.line(screen, SKIN_COLOR, (x + dx, hip), (x + dx, feet - 4), 7)
            pygame.draw.rect(screen, SHOE_COLOR, (x + dx - 6, feet - 6, 14, 6), border_radius=3)

        # Arms: down at his sides, or stretched up for the tip while airborne
        for dx in (-13, 13):
            if self.on_ground:
                hand = (x + dx * 1.3, shoulder + 34)
            else:
                hand = (x + dx * 0.6, shoulder - 34)
            pygame.draw.line(screen, SKIN_COLOR, (x + dx, shoulder + 4), hand, 6)

        # Shorts, jersey and number
        pygame.draw.rect(screen, SHORTS_COLOR, (x - 13, hip - 4, 26, 18), border_radius=3)
        pygame.draw.rect(screen, JERSEY_COLOR, (x - 13, shoulder, 26, self.TORSO - 2), border_radius=4)
        number = font.render(str(PLAYER_NUMBER), True, JERSEY_TEXT)
        screen.blit(number, number.get_rect(center=(x, shoulder + self.TORSO // 2 - 2)))

        # Head
        pygame.draw.circle(screen, SKIN_COLOR, (x, head_y), self.HEAD_RADIUS)


def draw_scoreboard(screen, font, small_font, left_hoop, right_hoop):
    board = pygame.Rect(WIDTH // 2 - 170, 10, 340, 70)
    pygame.draw.rect(screen, SCOREBOARD_COLOR, board, border_radius=10)
    for hoop, center_x in ((left_hoop, board.left + 85), (right_hoop, board.right - 85)):
        label = small_font.render(f"{hoop.side.upper()} HOOP", True, NET_COLOR)
        screen.blit(label, label.get_rect(center=(center_x, board.top + 20)))
        score = font.render(str(hoop.score), True, SCOREBOARD_TEXT)
        screen.blit(score, score.get_rect(center=(center_x, board.top + 48)))
    pygame.draw.line(screen, NET_COLOR, (board.centerx, board.top + 10), (board.centerx, board.bottom - 10), 2)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Jump")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 44)
    small_font = pygame.font.SysFont(None, 24)
    ball = Ball()
    hoops = [Hoop("left"), Hoop("right")]
    player = Player()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    ball.jump()
                elif event.key == pygame.K_ESCAPE:
                    running = False

        was_rising = ball.vy < 0
        ball.update()
        player.update(ball)

        # As a shot peaks on his side, number 8 goes up for the rebound
        if was_rising and ball.vy >= 0 and ball.x + ball.vx * TIP_LEAD > WIDTH // 2:
            player.jump()

        for hoop in hoops:
            if hoop.check_basket(ball):
                if ball.tipped:
                    ball.end_tip()
            elif hoop.side == "right" and not ball.tipped and hoop.check_miss(ball):
                # Missed on the right: number 8 tips it in
                player.jump()
                ball.tip_toward((hoop.rim_start + hoop.rim_end) / 2)

        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        for hoop in hoops:
            hoop.draw(screen)
        player.draw(screen, small_font)
        ball.draw(screen)
        draw_scoreboard(screen, font, small_font, *hoops)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
