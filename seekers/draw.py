from __future__ import annotations

import abc
import logging
import typing
import math

import pygame
from pygame.transform import scale

from .colors import *
from .seekers_types import *
from . import game
from . import sequential_probability_ratio_test


class Animation(abc.ABC):
    duration: float

    def __init__(self):
        self.age = 0

    @abc.abstractmethod
    def draw(self, renderer: GameRenderer):
        ...


class ScoreAnimation(Animation):
    duration = 40

    def __init__(self, position: Vector, color: Color, radius: float):
        super().__init__()
        self.position = position
        self.color = color
        self.radius = radius

    def draw(self, renderer: GameRenderer):
        t = self.age / self.duration
        r = self.radius + 50 * t

        renderer.draw_circle(self.color, self.position, int(r), 1)


class GameRenderer:
    def __init__(self, game_: game.SeekersGame):
        pygame.font.init()
        self.font = pygame.font.SysFont(["Cascadia Code", "Fira Code", "Consolas", "monospace"], 20)
        self.background_color = (0, 0, 30)

        self.player_name_images = {}
        self.screen = None

        self.game = game_
        self.seeker_display_mode: int = 0

        self.world = World(self.config.map_width, self.config.map_height)

    @property
    def config(self):
        return self.game.config

    def init(self, players: typing.Iterable[Player], goals: list[Goal]):
        pygame.init()

        for p in players:
            name = p.name
            self.player_name_images[p.id] = self.font.render(name, True, p.color)

        self._screen = pygame.display.set_mode(
            (self.config.map_dimensions[0] // self.game.scale, self.config.map_dimensions[1] // self.game.scale)
        )
        self.screen = pygame.Surface(self.config.map_dimensions)
        pygame.display.set_caption("Seekers")

    def draw_torus(self, func: typing.Callable[[Vector], typing.Any], p1: Vector, p2: Vector):
        func(p1)

        if p2.x > self.config.map_width:
            func(p1 + Vector(-self.config.map_width, 0))

        if p1.x < 0:
            func(p1 + Vector(self.config.map_width, 0))

        if p2.y > self.config.map_height:
            func(p1 + Vector(0, -self.config.map_height))

        if p1.y < 0:
            func(p1 + Vector(0, self.config.map_height))

    def draw_text(self, text: str, color: Color, pos: Vector, center=True):
        dx, dy = self.font.size(text)
        adj_pos = pos - Vector(dx, dy) / 2 if center else pos
        self.screen.blit(self.font.render(text, True, color), tuple(adj_pos))

        # no torus drawing for text

    def draw_circle(self, color: Color, center: Vector, radius: float, width: int = 0):
        r = Vector(radius, radius)

        self.draw_torus(
            lambda pos: pygame.draw.circle(self.screen, color, tuple(pos + r), radius, width),
            center - r, center + r
        )

    def draw_line(self, color: Color, start: Vector, end: Vector, width: int = 1):
        self.draw_torus(
            lambda pos: pygame.draw.line(self.screen, color, tuple(start), tuple(end), width),
            start, end
        )

    def draw_rect(self, color: Color, p1: Vector, p2: Vector, width: int = 0):
        self.draw_torus(
            lambda pos: pygame.draw.rect(self.screen, color, pygame.Rect(tuple(pos), tuple(p2 - p1)), width),
            p1, p2
        )

    def draw(self, players: typing.Collection[Player], camps: typing.Iterable[Camp], goals: typing.Iterable[Goal],
             animations: list[Animation], clock: pygame.time.Clock):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_s:
                    self.seeker_display_mode += 1
                    self.seeker_display_mode %= 3
                elif e.key == pygame.K_SPACE:
                    self.game.paused = not self.game.paused
                elif e.key == pygame.K_UP:
                    self.config.global_speed += 1
                    logging.getLogger(self.__class__.__name__).info(f"Speed: {self.config.global_speed}")
                elif e.key == pygame.K_DOWN:
                    self.config.global_speed = max(0, self.config.global_speed - 1)
                    logging.getLogger(self.__class__.__name__).info(f"Speed: {self.config.global_speed}")

        # clear screen
        self.screen.fill(self.background_color)

        # draw camps
        for camp in camps:
            self.draw_rect(camp.owner.color, camp.top_left, camp.bottom_right, 5)

        # draw goals
        for goal in goals:
            if goal.polarity == 1:
                color = (
                    interpolate_color((255, 255, 255), goal.owner.color,
                                      min(1.0, (goal.time_owned / goal.scoring_time) ** 2))
                    if goal.owner else (255, 255, 255)
                )
                self.draw_circle(color, goal.position, goal.radius + 2)
                # self.draw_circle((255, 255, 255), goal.position, goal.radius, width=2)
                self.draw_text("+", (0, 0, 0), goal.position, True)
            else:
                color = (
                    interpolate_color((0, 0, 0), goal.owner.color,
                                      min(1.0, (goal.time_owned / goal.scoring_time) ** 2))
                    if goal.owner else (0, 0, 0)
                )
                self.draw_circle(color, goal.position, goal.radius + 2)
                self.draw_circle((255, 255, 255), goal.position, goal.radius + 2, width=1)
                self.draw_text("-", (255, 255, 255), goal.position, True)

        # draw jet streams
        for player in players:
            for seeker in player.seekers.values():
                a = seeker.acceleration
                if not seeker.is_disabled and a.squared_length() > 0:
                    self.draw_jet_stream(seeker, -a)

        # draw seekers
        for player in players:
            for i, seeker in enumerate(player.seekers.values()):
                if self.seeker_display_mode == 1:
                    debug_str = str(i)
                elif self.seeker_display_mode == 2:
                    if seeker.is_disabled:
                        debug_str = {1: '+', -1: '-', 0: ""}[seeker.magnet]
                    else:
                        if seeker.magnet == 0:
                            debug_str = ""
                        else:
                            debug_str = f"{ {1: '+', -1: '-'}[seeker.magnet] }{self.config.global_total_magnet_resources - seeker._num_magnet + 1}"
                else:
                    debug_str = ""

                self.draw_seeker(seeker, player, debug_str)

            for debug_drawing in player.debug_drawings:
                debug_drawing.draw(self)

        # draw animations
        for animation in animations:
            animation.draw(self)

        # draw information (player's scores, etc.)
        self.draw_information(players, Vector(10, 10), clock)

        # update display
        self._screen.blit(pygame.transform.scale(self.screen, self._screen.get_rect().size), (0, 0))

        pygame.display.flip()

        return True

    def draw_seeker(self, seeker: Seeker, player: Player, debug_str: str):
        color = player.color
        if seeker.is_disabled:
            color = interpolate_color(color, [0, 0, 0], 0.5)

        self.draw_circle(color, seeker.position, seeker.radius, width=0)
        self.draw_halo(seeker, color)

        self.draw_text(debug_str, (0, 0, 0), seeker.position)

    def draw_halo(self, seeker: Seeker, color: Color):
        adjpos = seeker.position
        if seeker.is_disabled:
            return

        mu = abs(math.sin((int(pygame.time.get_ticks() / 30) % 50) / 50 * 2 * math.pi)) ** 2
        self.draw_circle(interpolate_color(color, [0, 0, 0], mu), adjpos, 3 + seeker.radius, 3)

        if not seeker.magnet:
            return

        d = 100 // seeker._num_magnet

        for o in range(0, d + 10, 10):
            mu = (int(-seeker.magnet * pygame.time.get_ticks() / d * 5 + o) % d)
            self.draw_circle(interpolate_color(color, self.background_color, mu / d), adjpos, mu + seeker.radius, 2)

    def draw_jet_stream(self, seeker: Seeker, direction: Vector):
        length = seeker.radius * 3
        adjpos = seeker.position

        self.draw_line((255, 255, 255), adjpos, adjpos + direction * length)

    def draw_information(self, players: typing.Collection[Player], pos: Vector, clock: pygame.time.Clock):
        # draw fps
        if self.game.sprt is not None:
            alpha, beta = self.game.sprt.get_h01_probs()
            text = f"FPS: {clock.get_fps():.1f} SPRT: P(H0)={alpha:.3%} P(H1)={beta:.3%}"
        else:
            text = f"FPS: {clock.get_fps():.1f}"

        text = text + {0: "", 1: ", displaying Indexes", 2: ", displaying Magnet"}[self.seeker_display_mode]

        if self.game.paused:
            text = text + " (PAUSED)"

        self.draw_text(text, (250, 250, 250), pos, center=False)

        dx = Vector(40, 0)
        dy = Vector(0, 30)
        pos += dy
        for p in players:
            self.draw_text(str(p.score), p.color, pos, center=False)
            self.screen.blit(self.player_name_images[p.id], tuple(pos + dx))
            pos += dy

    @staticmethod
    def close():
        pygame.quit()
