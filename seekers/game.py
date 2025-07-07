from __future__ import annotations

import collections
import glob
import logging
import os
import random
import typing
import pygame


from .seekers_types import *
from . import colors, sequential_probability_ratio_test
from . import draw
from . import game_logic


class GameFullError(Exception): ...


class SeekersGame:
    """A Seekers game. Manages the game logic, players, the gRPC server and graphics."""

    def __init__(self, local_ai_locations: typing.Iterable[str], config: Config,
                 debug: bool = True, scale: float = 1):
        self._logger = logging.getLogger("SeekersGame")

        self._logger.debug(f"Config: {config}")

        self.config = config
        self.debug = debug

        self.players = self.load_local_players(local_ai_locations)

        self.world = World(*self.config.map_dimensions)
        self.goals = []
        self.camps = []

        self.renderer = draw.GameRenderer(
            self
        )
        self.scale = scale
        self.animations = []
        self.paused = False

        self.sprt = None

        self.ticks = 0

    def start(self):
        """Start the game. Run the mainloop and block until the game is over."""
        self._logger.info(f"Starting game. (Seed: {self.config.global_seed}, Players: {len(self.players)})")

        self.clock = pygame.time.Clock()

        random.seed(self.config.global_seed)

        assert self.config.global_goals % 2 == 0

        # initialize goals
        self.goals = [
            Goal.from_config(get_id("Goal"), self.world.random_position(), 1, self.config)
            for _ in range(self.config.global_goals // 2)
        ] + [
            Goal.from_config(get_id("Goal"), self.world.random_position(), -1, self.config)
            for _ in range(self.config.global_goals // 2)
        ]

        # initialize players
        for p in self.players.values():
            p.seekers = {
                (id_ := get_id("Seeker")): Seeker.from_config(p, id_, self.world.random_position(), self.config)
                for _ in range(self.config.global_seekers)
            }
            p.color = self.get_new_player_color(p)

        # set up camps
        self.camps = self.world.generate_camps(self.players.values(), self.config)

        # prepare graphics
        self.renderer.init(self.players.values(), self.goals)

        return self.mainloop()

    def mainloop(self):
        """Start the game. Block until the game is over."""
        random.seed(self.config.global_seed)
        running = True

        if self.config.global_playtime == -1 and len(self.players) == 2:
            self._logger.info("Stopping game when both alpha and beta < 0.01")
            self.sprt = sequential_probability_ratio_test.SPRT(p0=0.505, p1=0.495, alpha=0.05, beta=0.05)

            player1, player2 = self.players.values()

            def callback(camp: Camp):
                if camp.owner is player1:
                    self.sprt.update(1)
                else:
                    self.sprt.update(0)
        else:
            self._logger.info(f"Stopping game when ticks exceed {self.config.global_playtime}")
            callback = None

        try:
            while running:
                # self._logger.debug(f"Tick {self.ticks:_}")

                # perform game logic
                for _ in range(self.config.global_speed):
                    # end game if tournament_length has been reached
                    if self.sprt is None:
                        if self.ticks >= self.config.global_playtime:
                            running = False
                            break
                    else:
                        if self.sprt.finished:
                            running = False

                            if player1.score > player2.score:
                                return 1, 0
                            else:
                                return 0, 1

                        if self.ticks > 1_000_000:
                            return .5, .5

                    if not self.paused:
                        for player in self.players.values():
                            # self._logger.debug(f"Polling AI for player {player.name}")
                            player.poll_ai(self.world, self.goals, self.players,
                                           self.ticks, self.debug)

                        game_logic.tick(self.players.values(), self.camps, self.goals, self.animations, self.world, self.config, callback)

                        self.ticks += 1

                # draw graphics
                running &= self.renderer.draw(self.players.values(), self.camps, self.goals, self.animations, self.clock)

                self.clock.tick(self.config.global_fps)

        finally:
            self._logger.info(f"Game over. (Ticks: {self.ticks:_})")

            self.print_scores()

            self.renderer.close()

    @staticmethod
    def load_local_players(ai_locations: typing.Iterable[str]) -> dict[str, Player]:
        """Return the players found in the given directories or files."""
        out: dict[str, Player] = {}

        for location in ai_locations:
            if os.path.isdir(location):
                for filename in glob.glob(os.path.join(location, "ai*.py")):
                    player = LocalPlayer.from_file(filename)
                    out |= {player.id: player}
            elif os.path.isfile(location):
                player = LocalPlayer.from_file(location)
                out |= {player.id: player}
            else:
                raise Exception(f"Invalid AI location: {location!r} is neither a file nor a directory.")

        return out

    def print_scores(self):
        for player in sorted(self.players.values(), key=lambda p: p.score, reverse=True):
            print(f"{player.score} P.:\t{player.name}")

    def get_new_player_color(self, player: Player) -> colors.Color:
        old_colors = [p.color for p in self.players.values() if p.color is not None]

        preferred = (
            colors.string_hash_color(player.name) if player.preferred_color is None else player.preferred_color
        )

        return colors.pick_new(old_colors, preferred, threshold=self.config.global_color_threshold)

    @property
    def seekers(self) -> collections.ChainMap[str, Seeker]:
        return collections.ChainMap(*(p.seekers for p in self.players.values()))
