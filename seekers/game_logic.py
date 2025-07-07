from __future__ import annotations

from .seekers_types import *
from . import draw

import typing


def tick(players: typing.Iterable[Player], camps: list[Camp], goals: list[Goal],
         animations: list[draw.Animation], world: World, config: Config,
         goal_score_callback: typing.Callable[[Camp], ...] | None = None):
    seekers = [s for p in players for s in p.seekers.values()]

    for s in seekers:
        if s.is_disabled:
            s.disabled_counter -= 1

    # compute magnetic forces and move goals
    for g in goals:
        g.acceleration = Vector(0, 0)

    for p in players:
        num_negative = 0
        num_positive = 0

        for s in p.seekers.values():
            if s.is_disabled:
                continue

            if s.magnet == 1:
                num_positive += 1
            elif s.magnet == -1:
                num_negative += 1

        positive_force = config.global_total_magnet_resources / num_positive if num_positive != 0 else 0
        negative_force = config.global_total_magnet_resources / num_negative if num_negative != 0 else 0
        for s in p.seekers.values():
            if s.is_disabled:
                s._num_magnet = 0
                continue

            if s.magnet == 1:
                s._num_magnet = num_positive
                force = positive_force
            elif s.magnet == -1:
                s._num_magnet = num_negative
                force = -negative_force
            else:
                s._num_magnet = 0
                continue

            for g in goals:
                # F = m * a
                F = world.magnetic_force(s.position, g.position) * force * -g.polarity * config.goal_thrust

                g.acceleration += F / config.goal_mass
                s.acceleration -= F / config.seeker_mass

    for g in goals:
        g.move(world)

    # move and recover seekers
    for s in seekers:
        if s.is_disabled:
            thrust = 0
        else:
            thrust = config.seeker_thrust
            if s.magnet:
                thrust /= 1 / config.seeker_magnet_slowdown / s._num_magnet

        s.acceleration = world.torus_direction(s.position, s.target) * thrust

        s.move(world)

    # handle collisions
    # noinspection PyTypeChecker
    physicals = seekers + goals
    for i, phys1 in enumerate(physicals):
        j = i + 1
        while j < len(physicals):
            phys2 = physicals[j]

            d = world.torus_difference(phys2.position, phys1.position).squared_length()

            min_dist = phys1.radius + phys2.radius

            if d < min_dist ** 2:
                if isinstance(phys1, Seeker) and isinstance(phys2, Seeker):
                    m1 = phys1._num_magnet
                    m2 = phys2._num_magnet

                    if m1 == m2 == 0:
                        seeker_1_count = 0.5 * config.seeker_disabled_time
                        seeker_2_count = 0.5 * config.seeker_disabled_time
                    elif m1 == 0:
                        seeker_1_count = 0
                        seeker_2_count = config.seeker_disabled_time
                    elif m2 == 0:
                        seeker_1_count = config.seeker_disabled_time
                        seeker_2_count = 0
                    else:
                        seeker_1_count = config.seeker_disabled_time * (m1 + m2) / m1
                        seeker_2_count = config.seeker_disabled_time * (m1 + m2) / m2

                    if not phys1.is_disabled:
                        phys1.disabled_counter = seeker_1_count
                    if not phys2.is_disabled:
                        phys2.disabled_counter = seeker_2_count

                    Seeker.collision(phys1, phys2, world)
                else:
                    Physical.collision(phys1, phys2, world)

            j += 1

    # handle goals and scoring
    for i, g in enumerate(goals):
        for camp in camps:
            if camp.contains(g.position):
                if g.owner == camp.owner:
                    g.time_owned += 1
                else:
                    if g.time_owned == 0:
                        g.owner = camp.owner
                        g.time_owned += 1
                    else:
                        g.time_owned -= 1

            if g.time_owned >= g.scoring_time:
                goal_scored(camp.owner, i, goals, animations, world)
                if goal_score_callback is not None:
                    goal_score_callback(camp)

                break

    # advance animations
    for i, animation in enumerate(animations):
        animation.age += 1

        if animation.age >= animation.duration:
            animations.pop(i)


def goal_scored(player: Player, goal_index: int, goals: list[Goal], animations: list[draw.Animation], world: World):
    player.score += 1

    goal = goals[goal_index]

    animations.append(draw.ScoreAnimation(goal.position, player.color, goal.radius))

    goal.position = world.random_position()
    goal.owner = None
    goal.time_owned = 0
