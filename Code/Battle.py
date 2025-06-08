import pygame
from Code.game_data import *
from Code.settings import *
from Code.sprites import PokemonSprite, PokemonNamesprite, PokemonLevelSprite, PokemonStatsSprite, BattleSprites, PokemonOutlineSprite

class Battle:
    def __init__(self, player_pokemon, opponent_pokemon, pokemon_frames, bg_surf, fonts):
        # general
        self.display_surface = pygame.display.get_surface()
        self.bg_surf = bg_surf
        self.pokemon_frames = pokemon_frames
        self.fonts = fonts
        self.pokemon_data = {'player': player_pokemon, 'opponent': opponent_pokemon}

        # groups
        self.battle_sprites = BattleSprites()
        self.player_sprites = pygame.sprite.Group()
        self.opponent_sprites = pygame.sprite.Group()

        # control
        self.current_pokemon = None
        self.selection_mode = None
        self.selection_side = 'player'
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

        pokemon_sprite = PokemonSprite(pos, frames, groups, pokemon, index, pos_index, entity)
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

            if keys[pygame.K_DOWN] and not self.prev_keys[pygame.K_DOWN]:
                self.indexes[self.selection_mode] = (self.indexes[self.selection_mode] + 1) % limiter
            if keys[pygame.K_UP] and not self.prev_keys[pygame.K_UP]:
                self.indexes[self.selection_mode] = (self.indexes[self.selection_mode] - 1) % limiter
            if keys[pygame.K_SPACE] and not self.prev_keys[pygame.K_SPACE]:
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

            self.prev_keys = keys

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

    def update_all_pokemon(self, option):
        for pokemon_sprite in self.player_sprites.sprites() + self.opponent_sprites.sprites():
            pokemon_sprite.pokemon.paused = True if option == 'pause' else False

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
        pass

    def update(self, dt):
        #updates
        self.input()
        self.battle_sprites.update(dt)
        self.check_active()

        #draw
        self.display_surface.blit(self.bg_surf, (0, 0))
        self.battle_sprites.draw(self.current_pokemon)
        self.draw_ui()