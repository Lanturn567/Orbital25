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

    #battle system
    def check_active(self):
        for pokemon_sprite in self.player_sprites.sprites() + self.opponent_sprites.sprites():
            if pokemon_sprite.pokemon.initiative >= 100:
                self.update_all_pokemon('pause')
                pokemon_sprite.pokemon.initiative = 0
                pokemon_sprite.set_highlight(True)
                self.current_pokemon = pokemon_sprite

    def update_all_pokemon(self, option):
        for pokemon_sprite in self.player_sprites.sprites() + self.opponent_sprites.sprites():
            pokemon_sprite.pokemon.paused = True if option == 'pause' else False

    def update(self, dt):
        #updates
        self.battle_sprites.update(dt)
        self.check_active()

        #draw
        self.display_surface.blit(self.bg_surf, (0, 0))
        self.battle_sprites.draw(self.current_pokemon)