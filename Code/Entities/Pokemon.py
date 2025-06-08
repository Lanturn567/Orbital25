from Code.game_data import *
import random

class Pokemon:
    def __init__(self, name, level):
        self.name, self.level = name, level
        self.paused = False

        # stats
        self.element = POKEMON_DATA[name]['stats']['element']
        self.base_stats = POKEMON_DATA[name]['stats']
        self.health = self.base_stats['max_health'] * self.level
        self.health -= random.randint(0, 200)
        self.energy = self.base_stats['max_energy'] * self.level
        self.energy -= random.randint(0, 200)
        self.initiative = 0
        self.abilities = POKEMON_DATA[name]['abilities']

        # experience
        self.xp = 1500
        self.level_up = self.level * 150

    def __repr__(self):
        return f'pokemon: {self.name}, lvl: {self.level}'

    def get_stat(self, stat):
        return self.base_stats[stat] * self.level

    def get_stats(self):
        return {
            'health': self.get_stat('max_health'),
            'energy': self.get_stat('max_energy'),
            'attack': self.get_stat('attack'),
            'defense': self.get_stat('defense'),
            'speed': self.get_stat('speed'),
            'recovery': self.get_stat('recovery'),
        }


    def get_abilities(self, all = True):
        if all:
            return [ability for lvl, ability in self.abilities.items() if self.level >= lvl]
        else:
            return [ability for lvl, ability in self.abilities.items() if self.level >= lvl and ATTACK_DATA[ability]['cost'] < self.energy]

    def get_info(self):
        return (
            (self.health, self.get_stat('max_health')),
            (self.energy, self.get_stat('max_energy')),
            (self.initiative, 100)
        )

    def update(self, dt):
        if not self.paused:
            self.initiative += self.get_stat('speed') * dt
