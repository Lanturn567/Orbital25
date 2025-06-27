import json
import os
import importlib
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

save = {
    "events": {"Mom" : False,
               "Dawn": False,
               "Prof" : False,
               "Daniel" : False,
               "Found" : False,
               "RivalTown" : False,
               "GymOne" : False,
               "SeenElder" : False,
               "Snorlax" : False,
               "DawnCity": False,
               "GymTwo" : False,
               "RivalMount" : False,
               "BeatDLKLPeak" : False,
               "FirstTimeInGym": False,
               "SeenSister" : False,
               "GymThree" : False,
               "BeatChampion" : False,
               "EndgameDawn" : False,
               },
    "pokemon": [], #list of poke objects
    #to change item to dict if item does not store quantity.
    "items": defaultdict(int), #dict (string map to int)
    "stage": "LevelOne", #string
    "pos": "default", #default last pos
    "name": "", #string
    "muted": True,
    "pokedex": defaultdict(int), # list of unique ids of pokemon seen
}

class Save:
    def __init__(self, name, data=save):
        self.data = data
        self.data["name"] = name

    def getBadges(self):
        if self.data["events"]["BeatChampion"]:
            return "All! :D"
        count = 0
        if self.data["events"]["GymOne"]:
            count += 1
        if self.data["events"]["GymTwo"]:
            count += 1
        if self.data["events"]["GymThree"]:
            count += 1
        return count

    def getSeen(self):
        return len(self.data["pokedex"])

    def getName(self):
        return self.data["name"]

    def getStageName(self):
        return self.data["stage"]

    #Note: Folder names must be capped, stage_name also capped
    def getStage(self):
        stage_name = self.data["stage"]
        if stage_name == "LevelOne" or stage_name == "LevelTwo":
            module = importlib.import_module(f"Code.{stage_name}Stage.{stage_name}")
        else:
            module = importlib.import_module(f"Code.Stages.{stage_name}.{stage_name}")
        return getattr(module, stage_name)  # e.g., Forest

    #val must be a string: stage name
    def updateStage(self, val):
        self.data["stage"] = val

    #val must be a string: start pos
    def updatePos(self, val):
        self.data["pos"] = val

    def getPos(self):
        return self.data["pos"]

    #item must be a string (name of item)
    def updateItems(self, item):
        self.data["items"][item] += 1

    #item must be a Pokemon object
    def updatePokemon(self, poke):
        self.data["pokemon"].append(poke)

    def getMuted(self):
        return self.data["muted"]

    def updateMuted(self):
        self.data["muted"] = not self.data["muted"]

    def setMute(self, boo):
        self.data["muted"] = boo

    #key is a string depicting event
    def updateEvent(self, key):
        if key not in self.data["events"]:
            print("Event not in data!")
        self.data["events"][key] = True

    def seenMom(self):
        return self.data["events"]["Mom"]

    def seenDawn(self):
        return self.data["events"]["Dawn"]

    def seenProf(self):
        return self.data["events"]["Prof"]

    def homeTest(self):
        if self.seenMom() and self.seenProf():
            return 2
        elif self.seenMom():
            return 1
        else:
            return 0

    def gotDaniel(self):
        return self.data["events"]["Daniel"]

    def getFound(self):
        return self.data["events"]["Found"]

    def beatGymOne(self):
        return self.data["events"]["GymOne"]

    def foughtRivalAtTown(self):
        return self.data["events"]["RivalTown"]

    def seenElder(self):
        return self.data["events"]["SeenElder"]

    def wokeSnorlax(self):
        return self.data["events"]["Snorlax"]

    def foughtDawnAtCity(self):
        return self.data["events"]["DawnCity"]

    def beatGymTwo(self):
        return self.data["events"]["GymTwo"]

    def foughtRivalAtMount(self):
        return self.data["events"]["RivalMount"]

    def beatDLKLAtPeak(self):
        return self.data["events"]["BeatDLKLPeak"]

    def beenInGym(self):
        return self.data["events"]["FirstTimeInGym"]

    def seenRaysenSister(self):
        return self.data["events"]["SeenSister"]

    def beatGymThree(self):
        return self.data["events"]["GymThree"]

    def beatChampion(self):
        return self.data["events"]["BeatChampion"]

    def beatEndgameDawn(self):
        return self.data["events"]["EndgameDawn"]

#Before: Let player choose name of save file aka Character
#New game: Make new save, write, pass save into stage.
#Load game: Read save, run stage.

class SaveSystem:

    @staticmethod
    def write(save):
        with open(os.path.join(BASE_DIR, "../Data/Saves/" + save.data["name"] + ".txt"), "w") as file:
            json.dump(save.data, file)

    @staticmethod
    def read(name):
        with open(os.path.join(BASE_DIR, "../Data/Saves/" + name + ".txt"), "r") as file:
            data = json.load(file)
            save = Save(name, data)
        return save