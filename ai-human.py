from seekers import *
import seekers.draw
import seekers.debug_drawing
# import keyboard
import math
import pygame

# pygame.init()

__color__ = (200, 130, 130)

renderer = None
animations = []
clock = pygame.time.Clock()

def decide(own_seekers: list[Seeker], other_seekers: list[Seeker], all_seekers: list[Seeker], goals: list[Goal],
           other_players: list[Player], own_camp: Camp, camps: list[Camp], world: World, passed_time: float):
    global renderer

    own_seekers[0].owner.color = (200, 130, 130)

    for player in other_players:
        player.color = (200, 100, 0)

    if renderer is None:
        class Config(seekers.Config):
            map_height = world.height
            map_width = world.width

        renderer = seekers.draw.GameRenderer(Config.__new__(Config), debug_mode=True)
        renderer.init([own_seekers[0].owner, *other_players], [])

    pygame.event.pump()

    keys = pygame.key.get_pressed()

    s1 = own_seekers[0]

    s1.target = Vector()

    if keys[pygame.K_w]:    s1.target += Vector(0, -1)
    if keys[pygame.K_a]:    s1.target += Vector(-1, 0)
    if keys[pygame.K_s]:    s1.target += Vector(0, 1)
    if keys[pygame.K_d]:    s1.target += Vector(1, 0)
    if keys[pygame.K_j]:    s1.magnet.set_attractive()
    elif keys[pygame.K_k]:  s1.magnet.set_repulsive()
    else:                   s1.magnet.disable()

    s1.target = s1.target * 20 + s1.position

    renderer.draw(players=[own_seekers[0].owner, *other_players], camps=camps, goals=goals, animations=animations, clock=clock)
    for s in own_seekers:
        s.owner.debug_drawings = [seekers.debug_drawing.CircleDebugDrawing(s.position, s.radius + 2, (255, 0, 0))]
    for s in other_seekers:
        s.owner.debug_drawings = [seekers.debug_drawing.CircleDebugDrawing(s.position, s.radius + 2, (255, 0, 0))]
    s1.owner.debug_drawings = [seekers.debug_drawing.CircleDebugDrawing(s1.position, s1.radius + 2, (0, 0, 255))]

    # return s1
    return own_seekers
