import random
import math
import game_framework
import game_world

from pico2d import *

# zombie Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# zombie Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

ANIM_FRAMES = {'Walk': 10, 'dead': 12}

class Zombie:
    images = None

    def load_images(self):
        if Zombie.images is None:
            Zombie.images = {}
            for name, count in ANIM_FRAMES.items():
                Zombie.images[name] = [load_image("./zombie/" + name + " (%d).png" % i) for i in range(1, count + 1)]

    def __init__(self):
        self.x, self.y = random.randint(1600 - 800, 1600), 150
        self.load_images()
        self.frame = random.randint(0, 9)
        self.dir = random.choice([-1, 1])
        self.scale = 1.0
        self.shrink = False
        self.state = 'Walk'

    def get_bb(self):
        hw = 100 * self.scale
        hh = 100 * self.scale
        return self.x - hw, self.y - hh, self.x + hw, self.y + hh

    def update(self):
        if self.state == 'dead':
            inc = FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
            self.frame = min(self.frame + inc, len(Zombie.images['dead']) - 1)
            if int(self.frame) >= len(Zombie.images['dead']) - 1:
                game_world.remove_object(self)
            return
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(Zombie.images['Walk'])
        self.x += RUN_SPEED_PPS * self.dir * game_framework.frame_time
        if self.x > 1600:
            self.dir = -1
        elif self.x < 800:
            self.dir = 1
        self.x = clamp(800, self.x, 1600)

    def draw(self):
        if self.state == 'dead':
            img = Zombie.images['dead'][int(self.frame)]
            img.draw(self.x, self.y, 200 * self.scale, 200 * self.scale)
        else:
            img = Zombie.images['Walk'][int(self.frame)]
            if self.dir < 0:
                img.composite_draw(0, 'h', self.x, self.y, 200 * self.scale, 200 * self.scale)
            else:
                img.draw(self.x, self.y, 200 * self.scale, 200 * self.scale)
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'zombie:ball':
            if self.state == 'dead':
                return
            fired = getattr(other, 'fired', False)
            on_ground = hasattr(other, 'y') and other.y <= 65
            if not fired or on_ground:
                return
            if not self.shrink:
                bottom = self.y - 100 * self.scale
                self.scale *= 0.5
                self.y = bottom + 100 * self.scale
                self.shrink = True
                game_world.remove_object(other)

            else:
                self.state = 'dead'
                self.frame = 0
                game_world.remove_object(other)
