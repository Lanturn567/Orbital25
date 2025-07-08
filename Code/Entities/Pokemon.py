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
        self.energy = self.base_stats['max_energy'] * self.level
        self.initiative = 0
        self.abilities = POKEMON_DATA[name]['abilities']
        self.defending = False

        # experience
        self.xp = 0
        self.level_up = self.level * 150

        self.can_run = False
        self.run_counter = 0

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

    def reduce_energy(self, attack):
        self.energy -= ATTACK_DATA[attack]['cost']

    def get_base_damage(self, attack):
        return self.get_stat('attack') * ATTACK_DATA[attack]['amount']

    def heal(self):
        self.health = self.base_stats['max_health'] * self.level
        self.energy = self.base_stats['max_energy'] * self.level


    def update_xp(self, amount):
        if self.level_up - self.xp > amount:
            self.xp += amount
        else:
            self.level += 1
            self.xp = amount - (self.level_up - self.xp)
            self.level_up = self.level * 150

    def update(self, dt):
        if not self.paused:
            self.initiative += 10 * self.get_stat('speed') * dt

    def start_running(self, turns_to_run=2):
        self.can_run = True
        self.run_counter = 0
        self.turns_to_run = turns_to_run

    def update_run_counter(self):
        if self.can_run:
            self.run_counter += 1
            return self.run_counter >= self.turns_to_run
        return False

    def cancel_run(self):
        self.can_run = False
        self.run_counter = 0

