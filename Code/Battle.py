from Code.settings import *
from Code.sprites import PokemonSprite, PokemonNamesprite, PokemonLevelSprite, PokemonStatsSprite, BattleSprites

class Battle:
    def __init__(self, player_pokemon, opponent_pokemon, pokemon_frames, bg_surf, fonts):
        # general
        self.display_surface = pygame.display.get_surface()
        self.bg_surf = bg_surf
        self.pokemon_frames = pokemon_frames
        self.fonts = fonts
        self.monster_data = {'player': player_pokemon, 'opponent': opponent_pokemon}

        # groups
        self.battle_sprites = BattleSprites()
        self.player_sprites = pygame.sprite.Group()
        self.opponent_sprites = pygame.sprite.Group()

        self.setup()

    def setup(self):
        for entity, monster in self.monster_data.items():
            for index, monster in {k: v for k, v in monster.items() if k <= 2}.items():
                self.create_pokemon(monster, index, index, entity)

    def create_pokemon(self, pokemon, index, pos_index, entity):
        frames = self.pokemon_frames['pokemon'][pokemon.name]
        if entity == 'player':
            pos = list(BATTLE_POSITIONS['left'].values())[pos_index]
            groups = (self.battle_sprites, self.player_sprites)
            frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in
                      frames.items()}
        else:
            pos = list(BATTLE_POSITIONS['right'].values())[pos_index]
            groups = (self.battle_sprites, self.opponent_sprites)

        pokemon_sprite = PokemonSprite(pos, frames, groups, pokemon, index, pos_index, entity)

        #ui
        name_pos = pokemon_sprite.rect.midleft + vector(16,-70) if entity == 'player' else pokemon_sprite.rect.midright + vector(-40, -70)
        name_sprite = PokemonNamesprite(name_pos, pokemon_sprite, self.battle_sprites, self.fonts['regular'])
        level_pos = name_sprite.rect.bottomleft if entity == 'player' else name_sprite.rect.bottomright
        PokemonLevelSprite(entity, level_pos, pokemon_sprite, self.battle_sprites, self.fonts['small'])
        PokemonStatsSprite(pokemon_sprite.rect.midright + vector(0, 50) if entity == 'player' else pokemon_sprite.rect.midleft + vector(0, 50),
                           pokemon_sprite,(110, 40), self.battle_sprites, self.fonts['small'])

    def update(self, dt):
        self.display_surface.blit(self.bg_surf, (0, 0))
        self.battle_sprites.update(dt)
        self.battle_sprites.draw()