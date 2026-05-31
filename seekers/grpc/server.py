from __future__ import annotations

import copy
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from .converters import *
from .stubs.org.seekers.grpc.service.seekers_pb2 import *
from .stubs.org.seekers.grpc.service.seekers_pb2_grpc import *

from .. import game


class GrpcSeekersServicer(SeekersServicer):
    def __init__(self, seekers_game: game.SeekersGame, game_start_event: threading.Event):
        self._logger = logging.getLogger(self.__class__.__name__)

        self.game = seekers_game
        self.game_start_event = game_start_event

        self.current_status: CommandResponse | None = None
        # the right thing here would be a Condition, but I found that too complicated
        self.next_game_tick_event = threading.Event()
        self.players_by_token: dict[str, game.Player] = {}

    def new_tick(self):
        """Invalidate the cached game status. Called by SeekersGame."""
        # self._logger.debug("New tick!")

        self.generate_status()

        self.next_game_tick_event.set()
        self.next_game_tick_event.clear()

    def generate_status(self):
        self.current_status = CommandResponse(
            players=[player_to_grpc(p) for p in self.game.players.values()],
            camps=[camp_to_grpc(c) for c in self.game.camps],
            seekers=[seeker_to_grpc(s) for s in self.game.seekers.values()],
            goals=[goal_to_grpc(goal) for goal in self.game.goals],

            passed_playtime=self.game.ticks,
            seekers_changed=0
        )

    def Command(self, request: CommandRequest, context: grpc.ServicerContext) -> CommandResponse | None:
        # self._logger.debug("Waiting for game start event.")
        self.game_start_event.wait()

        for command in request.commands:
            try:
                seeker = self.game.seekers[command.seeker_id]
            except KeyError:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Seeker with id {command.seeker_id!r} not found in the game.")
                return

            # check if seeker is owned by player
            # noinspection PyTypeChecker
            if (
                not isinstance(seeker.owner, seekers.GrpcClientPlayer)
                or (seeker.owner.id != self.players_by_token[request.token].id)
            ):
                context.abort(
                    grpc.StatusCode.PERMISSION_DENIED,
                    f"Seeker with id {command.seeker_id!r} (owner player id: {seeker.owner.id!r}) "
                    f"is not owned by token {request.token!r}."
                )
                return

            seeker.target = vector_to_seekers(command.target)
            seeker.magnet.strength = command.magnet

        # wait for next game tick except if no commands were sent
        if request.commands:
            # noinspection PyUnboundLocalVariable
            seeker.owner.was_updated[request.token].set()

            # self._logger.debug(f"Waiting for next game tick.")
            self.next_game_tick_event.wait()
            # self._logger.debug(f"Got event for next game tick. Sending status.")

            command_response = copy.copy(self.current_status)
            command_response.seekers_changed = len(request.commands)
            return command_response
        else:
            # self._logger.debug(
            #     "Got CommandRequest with no commands. Not waiting for next game tick to generate status.")
            if self.current_status is None:
                self.generate_status()
            return self.current_status

    def join_game(self, name: str, color: seekers.Color | None) -> tuple[str, str]:
        # # add the player with a new name if the requested name is already taken
        # _requested_name = name
        # i = 2
        # while _requested_name in {p.name for p in self.game.players.values()}:
        #     _requested_name = f"{name} ({i})"
        #     i += 1

        # create new player
        new_token = seekers.get_id("Token")
        player = seekers.GrpcClientPlayer(
            # token=new_token,
            id=name,
            name=name,
            score=0,
            seekers={},
            preferred_color=color
        )
        from seekers.game import GameFullError

        assert not self.game.camps, GameFullError("Game must not be running to add a player.")

        if len(self.game.players) >= self.game.config.global_players:
            raise GameFullError(
                f"Game full. Cannot add more players. Max player count is {self.game.config.global_players}."
            )

        self.game.players[player.id] = player
        self.players_by_token[new_token] = player

        self._logger.info(f"Player {player.name!r} joined the game. ({player.id})")

        return new_token, player.id

    def Join(self, request: JoinRequest, context) -> JoinResponse | None:
        self._logger.debug(f"Received JoinRequest: {request.name=} {request.color=}")

        if request.name is None:
            return context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Player name is mandatory.")

        requested_name = request.name.strip()

        if not requested_name:
            return context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                                 f"Requested name must not be empty or only consist of whitespace.")

        if requested_name not in self.game.players:
            color = color_to_seekers(request.color) if request.color is not None else None

            # add player to game
            try:
                new_token, player_id = self.join_game(requested_name, color)
            except game.GameFullError:
                context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, "Game is full.")
                return

            return JoinResponse(token=new_token, player_id=player_id, sections=config_to_grpc(self.game.config))

        else:
            player = self.game.players[requested_name]

            new_token = seekers.get_id("Token")
            self.players_by_token[new_token] = player
            return JoinResponse(token=new_token, player_id=requested_name, sections=config_to_grpc(self.game.config))


class GrpcSeekersServer:
    """A wrapper around the GrpcSeekersServicer that handles the gRPC server."""

    def __init__(self, seekers_game: game.SeekersGame, address: str = "localhost:7777"):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.game_start_event = threading.Event()

        self.server = grpc.server(ThreadPoolExecutor(thread_name_prefix="GrpcSeekersServicer"))
        self.servicer = GrpcSeekersServicer(seekers_game, self.game_start_event)
        add_SeekersServicer_to_server(self.servicer, self.server)

        self._is_running = False
        self._address = address

    def start_server(self):
        if self._is_running:
            return

        self._logger.info(f"Starting server on {self._address!r}")
        self.server.add_insecure_port(self._address)
        self.server.start()
        self._is_running = True

    def start_game(self):
        self.game_start_event.set()

    def stop(self):
        self.server.stop(None)
        self.new_tick()

    def new_tick(self):
        self.servicer.new_tick()
