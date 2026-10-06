# A4
Assignment 4

A basketball game made with pygame. The ball goes back and forth between two hoops and you make it jump to score.

## 1. How to run it

Open Terminal and type these lines one at a time:

```
git clone https://github.com/bshultz-sva/A4.git
cd A4
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ball_jump.py
```

On Windows the activate line is `.venv\Scripts\activate` instead.

Controls: Space, Up arrow or W makes the ball jump. Esc quits.

## 2. How it works

```python
    # A basket counts when the ball's center drops down through the rim
    def check_basket(self, ball):
        falling_through = ball.prev_y < RIM_Y <= ball.y
        if falling_through and self.rim_start < ball.x < self.rim_end:
            self.score += 1
            self.flash = FPS // 2
            return True
        return False

    # A miss is the ball dropping past rim height on this hoop's half of the court, outside the rim
    def check_miss(self, ball):
        falling_past = ball.prev_y < RIM_Y <= ball.y
        if self.side == "left":
            on_this_side = ball.x < WIDTH // 2
        else:
            on_this_side = ball.x > WIDTH // 2
        in_rim = self.rim_start < ball.x < self.rim_end
        return falling_past and on_this_side and not in_rim

    # define player self
    def draw_standing(self, screen, font):
        x, feet = int(self.x), int(self.y)
        hip = feet - self.LEG
        shoulder = hip - self.TORSO
        head_y = shoulder - self.HEAD_RADIUS
```

## 3. Recording

video link - https://youtu.be/yBB0Bm97JbI

## 4. What I made better

What I changed about the code was the players teams colors from purple and yellow to blue and orange.

Changes since class:

- Two hoops, one at each edge of the court, with a scoreboard that counts baskets for each hoop
- Player number 8 on the right side, who follows the ball and tips in missed shots
- Player number 8's team colors changed from purple and yellow to blue and orange
- Player number 1 on the left side, in black with a white number
- When a shot misses on the left side, player number 1 falls on his butt, then gets back up
