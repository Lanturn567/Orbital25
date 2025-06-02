from Code.settings import *
from Code.support import *
from Code.game_data import *
from Code.game_data import POKEMON_DATA
import pygame
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_OPEN_SOUND_PATH = os.path.join(BASE_DIR, "../Audio/Menu/menu_open.mp3")
MENU_CLICK_SOUND_PATH = os.path.join(BASE_DIR, "../Audio/Menu/menu_click.mp3")
MENU_SELECT_SOUND_PATH = os.path.join(BASE_DIR, "../Audio/Menu/menu_select.mp3")


class Menu:
    _instance = None

    def __new__(cls, pokemon, fonts, pokemon_frames):
        if cls._instance is None:
            cls._instance = super(Menu, cls).__new__(cls)
        return cls._instance

    def __init__(self, pokemon, fonts, pokemon_frames):
        if hasattr(self, '_initialized') and self._initialized:
            return  # Skip re-initialization

        self._initialized = True
        self.display_surface = pygame.display.get_surface()
        self.fonts = fonts
        self.pokemon = pokemon
        self.frame_index = 0

        # sounds
        self.open_sound = pygame.mixer.Sound(MENU_OPEN_SOUND_PATH)
        self.open_sound.set_volume(0.3)
        self.click_sound = pygame.mixer.Sound(MENU_CLICK_SOUND_PATH)
        self.click_sound.set_volume(0.2)
        self.select_sound = pygame.mixer.Sound(MENU_SELECT_SOUND_PATH)
        self.select_sound.set_volume(0.25)

        # tint surface
        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_surf.set_alpha(200)

        # frames
        self.icon_frames = pokemon_frames['icons']
        self.pokemon_frames = pokemon_frames['pokemon']
        self.ui_frames = pokemon_frames['ui']

        # dimensions
        self.main_rect = pygame.Rect(0, 0, WINDOW_WIDTH * 0.7, WINDOW_HEIGHT * 0.8)
        self.main_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

        # list
        self.visible_items = 6
        self.list_width = self.main_rect.width * 0.35
        self.item_height = self.main_rect.height / self.visible_items
        self.index = 0
        self.selected_index = None

        # max values
        self.max_stats = {}
        for data in POKEMON_DATA.values():
            for stat, value in data['stats'].items():
                if stat != 'element':
                    if stat not in self.max_stats:
                        self.max_stats[stat] = value
                    else:
                        self.max_stats[stat] = value if value > self.max_stats[stat] else self.max_stats[stat]
        self.max_stats['health'] = self.max_stats.pop('max_health')
        self.max_stats['energy'] = self.max_stats.pop('max_energy')

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and not self.prev_keys[pygame.K_UP]:
            self.index -= 1
            self.click_sound.play()
        if keys[pygame.K_DOWN] and not self.prev_keys[pygame.K_DOWN]:
            self.index += 1
            self.click_sound.play()
        if keys[pygame.K_SPACE] and not self.prev_keys[pygame.K_SPACE]:
            self.select_sound.play()
            if self.selected_index != None:
                selected_pokemon = self.pokemon[self.selected_index]
                current_pokemon = self.pokemon[self.index]
                self.pokemon[self.index] = selected_pokemon
                self.pokemon[self.selected_index] = current_pokemon
                self.selected_index = None
            else:
                self.selected_index = self.index

        self.index = self.index % len(self.pokemon)
        self.prev_keys = keys

    def display_list(self):
        offset = 0 if self.index < self.visible_items else -(self.index - self.visible_items + 1) * self.item_height

        # pokemon scrollbar
        for index, pokemon in self.pokemon.items():
            # colors
            bg_color = COLORS['gray'] if self.index != index else COLORS['light']
            text_color = COLORS['white'] if self.selected_index != index else COLORS['gold']

            top = self.main_rect.top + index * self.item_height + offset
            item_rect = pygame.Rect(self.main_rect.left, top, self.list_width, self.item_height)

            # text
            text_surf = self.fonts['regular'].render(pokemon.name, False, text_color)
            text_rect = text_surf.get_rect(midleft=item_rect.midleft + vector(80, 0))

            # pokemon icons
            icon_surf = self.icon_frames[pokemon.name]
            icon_rect = icon_surf.get_rect(center=item_rect.midleft + vector(35, 0))

            if item_rect.colliderect(self.main_rect):
                # round corners
                if item_rect.collidepoint(self.main_rect.topleft):
                    pygame.draw.rect(self.display_surface, bg_color, item_rect, 0, 0, 12, 0, 0, 0)
                elif item_rect.collidepoint((self.main_rect.bottomleft[0] + 2, self.main_rect.bottomleft[1] - 2)):
                    pygame.draw.rect(self.display_surface, bg_color, item_rect, 0, 0, 0, 0, 12, 0)
                else:
                    pygame.draw.rect(self.display_surface, bg_color, item_rect)

                self.display_surface.blit(text_surf, text_rect)
                self.display_surface.blit(icon_surf, icon_rect)

        # lines
        for i in range(min(self.visible_items, len(self.pokemon))):
            height = self.main_rect.top + self.item_height * i
            left = self.main_rect.left
            right = self.main_rect.left + self.list_width
            pygame.draw.line(self.display_surface, COLORS['light-gray'], (left, height), (right, height))

        # shadow
        shadow_surf = pygame.Surface((3, self.main_rect.height))
        shadow_surf.set_alpha(100)
        self.display_surface.blit(shadow_surf, (self.main_rect.left + self.list_width - 3, self.main_rect.top))

    def display_main(self, dt):
        # pokemon data
        pokemon = self.pokemon[self.index]

        # main background
        rect = pygame.Rect(self.main_rect.left + self.list_width, self.main_rect.top,
                           self.main_rect.width - self.list_width, self.main_rect.height)
        pygame.draw.rect(self.display_surface, COLORS['dark'], rect, 0, 12, 0, 12, 0)

        # pokemon display
        top_rect = pygame.Rect(rect.topleft, (rect.width, rect.height * 0.4))
        pygame.draw.rect(self.display_surface, COLORS[pokemon.element], top_rect, 0, 0, 0, 12, 0)

        # pokemon animation
        self.frame_index += ANIMATION_SPEED * dt
        pokemon_surf = self.pokemon_frames[pokemon.name]['idle'][
            int(self.frame_index) % len(self.pokemon_frames[pokemon.name]['idle'])]
        pokemon_rect = pokemon_surf.get_rect(center=top_rect.center)
        self.display_surface.blit(pokemon_surf, pokemon_rect)

        # name
        name_surf = self.fonts['bold'].render(pokemon.name, False, COLORS['white'])
        name_rect = name_surf.get_rect(topleft=top_rect.topleft + vector(8, 8))
        self.display_surface.blit(name_surf, name_rect)

        # level
        level_surf = self.fonts['regular'].render(f'Lvl: {pokemon.level}', False, COLORS['white'])
        level_rect = level_surf.get_rect(bottomleft=top_rect.bottomleft + vector(8, -8))
        self.display_surface.blit(level_surf, level_rect)
        draw_bar(
            surface=self.display_surface,
            rect=pygame.Rect(level_rect.bottomleft, (100, 4)),
            value=pokemon.xp,
            max_value=pokemon.level_up,
            color=COLORS['white'],
            bg_color=COLORS['dark'])

        # element
        element_surf = self.fonts['regular'].render(pokemon.element, False, COLORS['white'])
        element_rect = element_surf.get_rect(bottomright=top_rect.bottomright + vector(-8, -8))
        self.display_surface.blit(element_surf, element_rect)

        # health and energy
        bar_data = {
            'width': rect.width * 0.45,
            'height': 30,
            'top': top_rect.bottom + rect.width * 0.03,
            'left_side': rect.left + rect.width / 4,
            'right_side': rect.left + rect.width * 3 / 4
        }

        healthbar_rect = pygame.Rect((0, 0), (bar_data['width'], bar_data['height']))
        healthbar_rect.midtop = (bar_data['left_side'], bar_data['top'])
        draw_bar(self.display_surface, healthbar_rect, pokemon.health, pokemon.get_stat('max_health'), COLORS['red'],
                 COLORS['black'], 2)
        hp_text = self.fonts['regular'].render(f"HP: {int(pokemon.health)}/{int(pokemon.get_stat('max_health'))}",
                                               False,
                                               COLORS['white'])
        hp_rect = hp_text.get_rect(midleft=healthbar_rect.midleft + vector(10, 0))
        self.display_surface.blit(hp_text, hp_rect)

        energybar_rect = pygame.Rect((0, 0), (bar_data['width'], bar_data['height']))
        energybar_rect.midtop = (bar_data['right_side'], bar_data['top'])
        draw_bar(self.display_surface, energybar_rect, pokemon.energy, pokemon.get_stat('max_energy'), COLORS['blue'],
                 COLORS['black'], 2)
        ep_text = self.fonts['regular'].render(f"EP: {int(pokemon.energy)}/{int(pokemon.get_stat('max_energy'))}",
                                               False,
                                               COLORS['white'])
        ep_rect = ep_text.get_rect(midleft=energybar_rect.midleft + vector(10, 0))
        self.display_surface.blit(ep_text, ep_rect)

        # info
        sides = {'left': healthbar_rect.left, 'right': energybar_rect.left}
        info_height = rect.bottom - healthbar_rect.bottom

        # stats
        stats_rect = pygame.Rect(sides['left'], healthbar_rect.bottom, healthbar_rect.width, info_height).inflate(0,
                                                                                                                  -60)
        stats_text_surf = self.fonts['regular'].render('Stats:', False, COLORS['white'])
        stats_text_rect = stats_text_surf.get_rect(bottomleft=stats_rect.topleft)
        stats_text_rect.y -= 5
        self.display_surface.blit(stats_text_surf, stats_text_rect)

        pokemon_stats = pokemon.get_stats()
        stat_height = stats_rect.height / len(pokemon_stats)

        for index, (stat, value) in enumerate(pokemon_stats.items()):
            single_stat_rect = pygame.Rect(stats_rect.left, stats_rect.top + index * stat_height, stats_rect.width,
                                           stat_height)

            # icon
            icon_surf = self.ui_frames[stat]
            icon_rect = icon_surf.get_rect(midleft=single_stat_rect.midleft + vector(5, 0))
            self.display_surface.blit(icon_surf, icon_rect)

            # text
            text_surf = self.fonts['regular'].render(stat, False, COLORS['white'])
            text_rect = text_surf.get_rect(topleft=icon_rect.topleft + vector(20, 0))
            self.display_surface.blit(text_surf, text_rect)

            # bar
            bar_rect = pygame.Rect((text_rect.left, text_rect.bottom + 2),
                                   (single_stat_rect.width - (text_rect.left - single_stat_rect.left), 4))
            draw_bar(self.display_surface, bar_rect, value, self.max_stats[stat] * pokemon.level, COLORS['white'],
                     COLORS['black'])

        # abilities
        ability_rect = stats_rect.copy()
        ability_rect.left = sides['right']
        ability_text_surf = self.fonts['regular'].render('Abilities:', False, COLORS['white'])
        ability_text_rect = ability_text_surf.get_rect(bottomleft=ability_rect.topleft)
        ability_text_rect.y -= 5
        self.display_surface.blit(ability_text_surf, ability_text_rect)

        for index, ability in enumerate(pokemon.get_abilities()):
            element = ATTACK_DATA[ability]['element']

            text_surf = self.fonts['small'].render(ability, False, COLORS['black'])
            x = ability_rect.left + index % 2 * ability_rect.width / 2
            y = 20 + ability_rect.top + int(index / 2) * (text_surf.get_height() + 20)
            rect = text_surf.get_rect(topleft=(x, y))
            pygame.draw.rect(self.display_surface, COLORS[element], rect.inflate(5, 5), 0, 4)
            self.display_surface.blit(text_surf, rect)

    def update(self, dt):
        self.input()
        self.display_surface.blit(self.tint_surf, (0, 0))
        self.display_list()
        self.display_main(dt)