import pygame
from Code.game_data import *
from Code.settings import *
from Code.sprites import (PokemonSprite, PokemonNamesprite, PokemonLevelSprite, PokemonStatsSprite,
                          BattleSprites, PokemonOutlineSprite, AttackSprite)
from Code.support import *
from Code.timer import Timer
from random import choice

class Battle:
    def __init__(self, player_pokemon, opponent_pokemon, pokemon_frames, bg_surf, fonts):
        # general
        self.display_surface = pygame.display.get_surface()
        self.bg_surf = bg_surf
        self.pokemon_frames = pokemon_frames
        self.fonts = fonts
        self.pokemon_data = {'player': player_pokemon, 'opponent': opponent_pokemon}

        # timers
        self.timers = {
            'opponent delay': Timer(600, func = self.opponent_attack)
        }

        # groups
        self.battle_sprites = BattleSprites()
        self.player_sprites = pygame.sprite.Group()
        self.opponent_sprites = pygame.sprite.Group()

        # control
        self.current_pokemon = None
        self.selection_mode = None
        self.selection_side = 'player'
        self.selected_attack = None
        self.indexes = {
            'general': 0,
            'monster': 0,
            'attacks': 0,
            'switch': 0,
            'target': 0
        }

        self.setup()

    def setup(self):
        for entity, pokemon in self.pokemon_data.items():
            for index, pokemon in {k: v for k, v in pokemon.items() if k <= 2}.items():
                self.create_pokemon(pokemon, index, index, entity)

            # remove opponent pokemon data
            for i in range(len(self.opponent_sprites)):
                del self.pokemon_data['opponent'][i]

    def create_pokemon(self, pokemon, index, pos_index, entity):
        frames = self.pokemon_frames['pokemon'][pokemon.name]
        outline_frames = self.pokemon_frames['outlines'][pokemon.name]
        if entity == 'player':
            pos = list(BATTLE_POSITIONS['left'].values())[pos_index]
            groups = (self.battle_sprites, self.player_sprites)
            frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in
                      frames.items()}
            outline_frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in
                      outline_frames.items()}
        else:
            pos = list(BATTLE_POSITIONS['right'].values())[pos_index]
            groups = (self.battle_sprites, self.opponent_sprites)

        pokemon_sprite = PokemonSprite(pos, frames, groups, pokemon, index, pos_index, entity, self.apply_attack, self.create_pokemon)
        PokemonOutlineSprite(pokemon_sprite, self.battle_sprites, outline_frames)

        #ui
        name_pos = pokemon_sprite.rect.midleft + vector(16,-70) if entity == 'player' else pokemon_sprite.rect.midright + vector(-40, -70)
        name_sprite = PokemonNamesprite(name_pos, pokemon_sprite, self.battle_sprites, self.fonts['regular'])
        level_pos = name_sprite.rect.bottomleft if entity == 'player' else name_sprite.rect.bottomright
        PokemonLevelSprite(entity, level_pos, pokemon_sprite, self.battle_sprites, self.fonts['small'])
        PokemonStatsSprite(pokemon_sprite.rect.midright + vector(0, 50) if entity == 'player' else pokemon_sprite.rect.midleft + vector(0, 50),
                           pokemon_sprite,(110, 40), self.battle_sprites, self.fonts['small'])

    def input(self):
        if self.selection_mode and self.current_pokemon:
            keys = pygame.key.get_pressed()

            match self.selection_mode:
                case 'general': limiter = len(BATTLE_CHOICES['full'])
                case 'attacks': limiter = len(self.current_pokemon.pokemon.get_abilities(all = False))
                case 'switch' : limiter = len(self.available_pokemon)
                case 'target' : limiter = len(self.opponent_sprites) if self.selection_side == 'opponent' else len(self.player_sprites)

            if keys[pygame.K_DOWN] and not self.prev_keys[pygame.K_DOWN]:
                self.indexes[self.selection_mode] = (self.indexes[self.selection_mode] + 1) % limiter

            if keys[pygame.K_UP] and not self.prev_keys[pygame.K_UP]:
                self.indexes[self.selection_mode] = (self.indexes[self.selection_mode] - 1) % limiter

            if keys[pygame.K_SPACE] and not self.prev_keys[pygame.K_SPACE]:

                if self.selection_mode == 'target':
                    sprite_group = self.opponent_sprites if self.selection_side == 'opponent' else self.player_sprites
                    sprites = {sprite.pos_index: sprite for sprite in sprite_group}
                    pokemon_sprite = sprites[list(sprites.keys())[self.indexes['target']]]

                    if self.selected_attack:
                        self.current_pokemon.activate_attack(pokemon_sprite, self.selected_attack)
                        self.selected_attack, self.current_pokemon, self.selection_mode = None, None, None
                    else:
                        pass

                if self.selection_mode == 'attacks':
                    self.selection_mode = 'target'
                    self.selected_attack = self.current_pokemon.pokemon.get_abilities(all = False)[self.indexes['attacks']]
                    self.selection_side = ATTACK_DATA[self.selected_attack]['target']

                if self.selection_mode == 'general':
                    if self.indexes['general'] == 0:
                        self.selection_mode = 'attacks'

                    if self.indexes['general'] == 1:
                        self.update_all_pokemon('resume')
                        self.current_pokemon, self.selection_mode = None, None
                        self.indexes['general'] = 0

                    if self.indexes['general'] == 2:
                        self.selection_mode = 'switch'

                    if self.indexes['general'] == 3:
                        print('catch')
                self.indexes = {k: 0 for k in self.indexes}

            if keys[pygame.K_ESCAPE] and not self.prev_keys[pygame.K_ESCAPE]:
                if self.selection_mode in ('attacks', 'switch', 'target'):
                    self.selection_mode = 'general'

            self.prev_keys = keys

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    #battle system
    def check_active(self):
        for pokemon_sprite in self.player_sprites.sprites() + self.opponent_sprites.sprites():
            if pokemon_sprite.pokemon.initiative >= 100:
                self.update_all_pokemon('pause')
                pokemon_sprite.pokemon.initiative = 0
                pokemon_sprite.set_highlight(True)
                self.current_pokemon = pokemon_sprite
                if self.player_sprites in pokemon_sprite.groups():
                    self.selection_mode = 'general'
                else:
                    self.timers['opponent delay'].activate()

    def update_all_pokemon(self, option):
        for pokemon_sprite in self.player_sprites.sprites() + self.opponent_sprites.sprites():
            pokemon_sprite.pokemon.paused = True if option == 'pause' else False

    def apply_attack(self, target_sprite, attack, amount):
        AttackSprite(target_sprite.rect.center, self.pokemon_frames['attacks'][ATTACK_DATA[attack]['animation']], self.battle_sprites)
        # play animation

        # get correct attack damage amount (defense, element)
        attack_element = ATTACK_DATA[attack]['element']
        target_element = target_sprite.pokemon.element

        # double attack
        if attack_element == 'fire' and target_element == 'plant' or \
                attack_element == 'water' and target_element == 'fire' or \
                attack_element == 'plant' and target_element == 'water':
            amount *= 2

        # halve attack
        if attack_element == 'fire' and target_element == 'water' or \
                attack_element == 'water' and target_element == 'plant' or \
                attack_element == 'plant' and target_element == 'fire':
            amount *= 0.5

        target_defense = 1 - target_sprite.pokemon.get_stat('defense') / 2000
        target_defense = max(0, min(1, target_defense))

        # update the monster health
        target_sprite.pokemon.health -= amount * target_defense
        self.check_death()

        # resume
        self.update_all_pokemon('resume')

    def check_death(self):
        for pokemon_sprite in self.opponent_sprites.sprites() + self.player_sprites.sprites():
            if pokemon_sprite.pokemon.health <= 0:
                if self.player_sprites in pokemon_sprite.groups():
                    active_pokemon = [(pokemon_sprite.index, pokemon_sprite.pokemon) for pokemon_sprite in self.player_sprites.sprites()]
                    available_pokemon = [(index, pokemon) for index, pokemon in self.pokemon_data['player'].items() if pokemon.health > 0 and (index, pokemon) not in active_pokemon]
                    if available_pokemon:
                        new_pokemon_data = [(pokemon, index, pokemon_sprite.pos_index, 'player') for index, pokemon in available_pokemon][0]
                    else:
                        new_pokemon_data = None
                else:
                    new_pokemon_data = (list(self.pokemon_data['opponent'].values())[0], pokemon_sprite.index,
                                        pokemon_sprite.pos_index, 'opponent') if self.pokemon_data['opponent'] else None
                    if self.pokemon_data['opponent']:
                        del self.pokemon_data['opponent'][min(self.pokemon_data['opponent'])]
                    # xp
                    xp_amount = pokemon_sprite.pokemon.level * 100 / len(self.player_sprites)
                    for player_sprite in self.player_sprites:
                        player_sprite.pokemon.update_xp(xp_amount)

                pokemon_sprite.delayed_kill(new_pokemon_data)

    def opponent_attack(self):
        ability = choice(self.current_pokemon.pokemon.get_abilities())
        side = ATTACK_DATA[ability]['target']
        if side == 'player':
            random_target = choice(self.opponent_sprites.sprites())
        else:
            random_target = choice(self.player_sprites.sprites())
        self.current_pokemon.activate_attack(random_target, ability)

    def draw_ui(self):
        if self.current_pokemon:
            if self.selection_mode == 'general':
                self.draw_general()
            if self.selection_mode == 'attacks':
                self.draw_attacks()
            if self.selection_mode == 'switch':
                self.draw_switch()

    def draw_general(self):
        for index, (option, data_dict) in enumerate(BATTLE_CHOICES['full'].items()):
            if index == self.indexes['general']:
                surf = self.pokemon_frames['ui'][f"{data_dict['icon']}_highlight"]
            else:
                surf = pygame.transform.grayscale(self.pokemon_frames['ui'][data_dict['icon']])
            rect = surf.get_rect(center = self.current_pokemon.rect.midright + data_dict['pos'])
            self.display_surface.blit(surf, rect)

    def draw_attacks(self):
        abilities = self.current_pokemon.pokemon.get_abilities(all = False)
        width, height = 100, 150
        visible_attacks = 4
        item_height = height / visible_attacks
        v_offset = 0 if self.indexes['attacks'] < visible_attacks else -(self.indexes['attacks'] - visible_attacks + 1) * item_height

        #bg
        bg_rect = pygame.Rect((0,0), (width, height))
        bg_rect.midleft = self.current_pokemon.rect.midright + vector(10, 0)
        pygame.draw.rect(self.display_surface, COLORS['white'], bg_rect, 0 ,5)

        for index, ability in enumerate(abilities):
            selected = index == self.indexes['attacks']

            # text
            if selected:
                element = ATTACK_DATA[ability]['element']
                text_color = COLORS[element] if element != 'normal' else COLORS['black']
            else:
                text_color = COLORS['light']
            text_surf = self.fonts['regular'].render(ability, False, text_color)

            # rect
            text_rect = text_surf.get_rect(center=bg_rect.midtop + vector(0, item_height / 2 + index * item_height + v_offset))
            text_bg_rect = pygame.Rect((0, 0), (width, item_height))
            text_bg_rect.center = text_rect.center

            # draw
            if bg_rect.collidepoint(text_rect.center):
                if selected:
                    if text_bg_rect.collidepoint(bg_rect.topleft):
                        pygame.draw.rect(self.display_surface, COLORS['dark white'], text_bg_rect, 0, 0, 5, 5)
                    elif text_bg_rect.collidepoint(bg_rect.midbottom + vector(0, -1)):
                        pygame.draw.rect(self.display_surface, COLORS['dark white'], text_bg_rect, 0, 0, 0, 0, 5, 5)
                    else:
                        pygame.draw.rect(self.display_surface, COLORS['dark white'], text_bg_rect)

                self.display_surface.blit(text_surf, text_rect)

    def draw_switch(self):
        # data
        width, height = 200, 215
        visible_pokemon = 4
        item_height = height / visible_pokemon
        v_offset = 0 if self.indexes['switch'] < visible_pokemon else -(self.indexes['switch'] - visible_pokemon + 1) * item_height
        bg_rect = pygame.Rect((0, 0), (width, height))
        bg_rect.midleft = self.current_pokemon.rect.midright + vector(10, 0)
        pygame.draw.rect(self.display_surface, COLORS['white'], bg_rect, 0, 5)

        # pokemon
        active_pokemon = [(pokemon_sprite.index, pokemon_sprite.pokemon) for pokemon_sprite in self.player_sprites]
        self.available_pokemon = {index: pokemon for index, pokemon in self.pokemon_data['player'].items()
                                  if (index, pokemon) not in active_pokemon and pokemon.health > 0}

        for index, pokemon in enumerate(self.available_pokemon.values()):
            selected = index == self.indexes['switch']
            item_bg_rect = pygame.Rect((0, 0), (width, item_height))
            item_bg_rect.midleft = (bg_rect.left, bg_rect.top + item_height / 2 + index * item_height + v_offset)

            icon_surf = self.pokemon_frames['icons'][pokemon.name]
            icon_rect = icon_surf.get_rect(midleft = bg_rect.topleft + vector(10, item_height / 2 + index * item_height + v_offset))
            text_surf = self.fonts['regular'].render(f'{pokemon.name} ({pokemon.level})', False, COLORS['red'] if selected else COLORS['black'])
            text_rect = text_surf.get_rect(topleft=(bg_rect.left + 90, icon_rect.top))

            # selection bg
            if selected:
                if item_bg_rect.collidepoint(bg_rect.topleft):
                    pygame.draw.rect(self.display_surface, COLORS['dark white'], item_bg_rect, 0, 0, 5, 5)
                elif item_bg_rect.collidepoint(bg_rect.midbottom + vector(0, -1)):
                    pygame.draw.rect(self.display_surface, COLORS['dark white'], item_bg_rect, 0, 0, 0, 0, 5, 5)
                else:
                    pygame.draw.rect(self.display_surface, COLORS['dark white'], item_bg_rect)

            if bg_rect.collidepoint(item_bg_rect.center):
                for surf, rect in ((icon_surf, icon_rect), (text_surf, text_rect)):
                    self.display_surface.blit(surf, rect)
                health_rect = pygame.Rect((text_rect.bottomleft + vector(0, 4)), (100, 4))
                energy_rect = pygame.Rect((health_rect.bottomleft + vector(0, 2)), (80, 4))
                draw_bar(self.display_surface, health_rect, pokemon.health, pokemon.get_stat('max_health'), COLORS['red'], COLORS['black'])
                draw_bar(self.display_surface, energy_rect, pokemon.energy, pokemon.get_stat('max_energy'), COLORS['blue'], COLORS['black'])

    def update(self, dt):
        #updates
        self.input()
        self.update_timers()
        self.battle_sprites.update(dt)
        self.check_active()

        #draw
        self.display_surface.blit(self.bg_surf, (0, 0))
        self.battle_sprites.draw(self.current_pokemon, self.selection_side, self.selection_mode, self.indexes['target'],
                                 self.player_sprites, self.opponent_sprites)
        self.draw_ui()