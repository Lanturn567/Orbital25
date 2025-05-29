import random
import math

NO_EFFECT = 0
NOT_EFFECTIVE = 0.5
NORMAL = 1
SUPER_EFFECTIVE = 2
EXP_TO_NEXT_LEVEL = 1000
MAX_LEVEL = 100

class Pokemon:
    TYPES = {"normal" : 0,
             "fire" : 1,
             "water" : 2,
             "grass" : 3,
             "ground" : 4,
             "rock" : 5,
             "electric" : 6,
             "air" : 7,
             "bug" : 8,
             "dark" : 9,
             "psychic" : 10,
             "ghost" : 11,
             "fairy" : 12,
             "steel" : 13,
             "poison" : 14,
             "DLKL" : 15,
             }

    typeWeb = []
    initialized = False

    @classmethod
    def init_typings(cls):
        for i in range(16):
            curr = []
            for j in range(16):
                curr.append(NORMAL)
            cls.typeWeb.append(curr)

        cls.typeWeb[1][3] = SUPER_EFFECTIVE
        cls.typeWeb[1][8] = SUPER_EFFECTIVE
        cls.typeWeb[2][1] = SUPER_EFFECTIVE
        cls.typeWeb[2][5] = SUPER_EFFECTIVE
        cls.typeWeb[3][2] = SUPER_EFFECTIVE
        cls.typeWeb[3][5] = SUPER_EFFECTIVE
        cls.typeWeb[4][1] = SUPER_EFFECTIVE
        cls.typeWeb[4][5] = SUPER_EFFECTIVE
        cls.typeWeb[4][6] = SUPER_EFFECTIVE
        cls.typeWeb[4][13] = SUPER_EFFECTIVE
        cls.typeWeb[5][1] = SUPER_EFFECTIVE
        cls.typeWeb[5][7] = SUPER_EFFECTIVE
        cls.typeWeb[5][8] = SUPER_EFFECTIVE
        cls.typeWeb[6][2] = SUPER_EFFECTIVE
        cls.typeWeb[6][7] = SUPER_EFFECTIVE
        cls.typeWeb[7][3] = SUPER_EFFECTIVE
        cls.typeWeb[7][8] = SUPER_EFFECTIVE
        cls.typeWeb[8][3] = SUPER_EFFECTIVE
        cls.typeWeb[8][9] = SUPER_EFFECTIVE
        cls.typeWeb[8][10] = SUPER_EFFECTIVE
        cls.typeWeb[9][10] = SUPER_EFFECTIVE
        cls.typeWeb[10][14] = SUPER_EFFECTIVE
        cls.typeWeb[11][11] = SUPER_EFFECTIVE
        cls.typeWeb[11][9] = SUPER_EFFECTIVE
        cls.typeWeb[11][10] = SUPER_EFFECTIVE
        cls.typeWeb[12][9] = SUPER_EFFECTIVE
        cls.typeWeb[12][11] = SUPER_EFFECTIVE
        cls.typeWeb[13][14] = SUPER_EFFECTIVE
        cls.typeWeb[14][3] = SUPER_EFFECTIVE
        cls.typeWeb[14][12] = SUPER_EFFECTIVE

        for i in range(16):
            cls.typeWeb[15][i] = SUPER_EFFECTIVE

        for i in range(16):
            for j in range(16):
                if i != j and cls.typeWeb[i][j] == SUPER_EFFECTIVE:
                    cls.typeWeb[j][i] = NOT_EFFECTIVE

        cls.typeWeb[4][7] = NO_EFFECT
        cls.typeWeb[6][4] = NO_EFFECT
        cls.typeWeb[10][11] = NO_EFFECT
        cls.typeWeb[14][13] = NO_EFFECT

    def __init__(self, level, hp, atk, satk, spd, cr, cd, dfc, sdfc, name, moves, type):
        self.level = level
        self.maxHp = hp
        self.currentHp = hp
        self.atk = atk
        self.satk = satk #special atk
        self.spd = spd
        self.cr = cr #c rate
        self.cd = cd #crit damage
        self.dfc = dfc #defence
        self.sdfc = sdfc # special def
        self.name = name #nickname if None, use Species name
        self.moves = moves #list of Moves
        self.dead = False
        self.status = "" #poison, para, slp, freeze, burn, infat
        self.exp = 0
        self.type = type #max 1 type for now

    def attack(self, moveIndex, pokemon):
        if moveIndex < 0 or moveIndex >= len(self.moves):
            return

        if self.status == "sleep" or self.status == "freeze":
            return
        elif (self.status == "para" or self.status == "infatuated") and random.randint(0, 100) < 50:
            return

        move = self.moves[moveIndex]
        dmg = move.dmg if self.status != "burn" else move.dmg // 2

        if random.randint(0, 100) < move.acc:
            levelDiff = self.level - pokemon.level
            levelMulti = 1 + levelDiff * 0.10 if levelDiff > 0 else max(0, 1 - levelDiff * 0.1)
            critMulti = 1 if random.randint(0, 100) > self.cr else self.cd / 100
            atkMulti = math.sqrt(self.satk / pokemon.sdfc if move.special else self.atk / pokemon.dfc)
            typeMulti = checkType(move.type, pokemon)

            pokemon.damage(max(1, round(dmg * critMulti * levelMulti * atkMulti)))

            if move.hasEffect:
                move.effect(pokemon)


    def damage(self, dmg):
        self.currentHp = max(0, self.currentHp - dmg)
        self.dead = True if self.currentHp == 0 else False

    def heal(self, amount):
        if self.dead: #cannot heal if dead
            return
        self.currentHp = min(self.maxHp, self.currentHp + amount)

    def revive(self):
        self.dead = False
        self.currentHp = self.maxHp

    def rename(self, name):
        self.name = name

    def gainEXP(self, exp):
        if self.level == MAX_LEVEL:
            return
        levels = (self.exp + exp) // EXP_TO_NEXT_LEVEL
        self.exp = (self.exp + exp) % EXP_TO_NEXT_LEVEL
        self.level = min(self.level + levels, MAX_LEVEL)

    def checkType(self, moveType, pokemon):
        if not Pokemon.initialized:
            Pokemon.init_typings()
            Pokemon.initialized = True

        pokemon_type = Pokemon.TYPES.get(pokemon.type, 0)  # default to normal type
        move_type = Pokemon.TYPES.get(moveType, 0)

        if move_type >= len(Pokemon.typeWeb) or pokemon_type >= len(Pokemon.typeWeb):
            return NORMAL

        return Pokemon.typeWeb[move_type][pokemon_type]

    #at end of turn update status
    def status(self):
        if self.status == "poison":
            damage(self.maxHp // 10)
        elif self.status == "burn":
            damage(self.maxHp // 16)
        elif (self.status == "freeze" or self.status == "sleep") and random.randint(0, 100) < 30:
            self.status = ""
        elif self.status == "infatuated" and random.randint(0, 100) < 20:
            self.status = ""
        else:
            pass







