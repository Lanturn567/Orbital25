class Move:

    def __init__(self, type, dmg, acc, name, special, hasEffect, ):
        self.type = type #type
        self.dmg = dmg #damage
        self.acc = acc #accuracy
        self.hasEffect = hasEffect #bool has effect
        self.name = name
        self.special = special #spcial move

    #Subclasses implement MoveSubclass void :: effect(Pokemon) if has Effect

    def effect(self, pokemon):
        pass