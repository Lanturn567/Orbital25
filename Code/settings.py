import pygame
from pygame.math import Vector2 as vector
from sys import exit

WINDOW_WIDTH, WINDOW_HEIGHT = 740, 493
TILE_SIZE = 64
ANIMATION_SPEED = 6
BATTLE_OUTLINE_WIDTH = 4

COLORS = {
    'white': '#f4fefa',
    'pure white': '#ffffff',
    'dark': '#2b292c',
    'light': '#c8c8c8',
    'gray': '#3a373b',
    'gold': '#ffd700',
    'light-gray': '#4b484d',
    'fire': '#f8a060',
    'water': '#50b0d8',
    'plant': '#64a990',
    'black': '#000000',
    'red': '#f03131',
    'blue': '#66d7ee',
    'normal': '#ffffff',
    'dark white': '#f0f0f0'
}

WORLD_LAYERS = {
    'water': 0,
    'bg': 1,
    'shadow': 2,
    'main': 3,
    'top': 4
}

BATTLE_POSITIONS = {
    'left': {'top': (150, 100), 'center': (200, 250), 'bottom': (150, 400)},
    'right': {'top': (600, 100), 'center': (550, 250), 'bottom': (600, 400)}
}

BATTLE_LAYERS = {
    'outline': 0,
    'name': 1,
    'monster': 2,
    'effects': 3,
    'overlay': 4
}

BATTLE_CHOICES = {
    'full': {
        'fight': {'pos': vector(30, -60), 'icon': 'sword'},
        'defend': {'pos': vector(40, -20), 'icon': 'shield'},
        'switch': {'pos': vector(40, 20), 'icon': 'arrows'},
        'catch': {'pos': vector(30, 60), 'icon': 'hand'}},

    'limited': {
        'fight': {'pos': vector(30, -40), 'icon': 'sword'},
        'defend': {'pos': vector(40, 0), 'icon': 'shield'},
        'switch': {'pos': vector(30, 40), 'icon': 'arrows'}}
}