import json
import os
import sys
import importlib
from collections import defaultdict
import platform
from Code.Entities.Pokemon import Pokemon

# Cross-platform save directory handling
def get_save_directory():
    """
    Returns the appropriate save directory for the current platform.
    """
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        if platform.system() == "Windows":
            return os.path.join(os.getenv('APPDATA'), 'PokemonGame', 'Saves')
        elif platform.system() == "Darwin":  # macOS
            return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'PokemonGame', 'Saves')
        else:  # Linux and other platforms
            return os.path.join(os.path.expanduser('~'), '.local', 'share', 'PokemonGame', 'Saves')
    else:
        # Running in development mode
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "../Data/Saves")

SAVE_DIR = get_save_directory()

# Ensure the save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

save = {
    "events": {
        "Mom": False,
        "Dawn": False,
        "Prof": True,
        "Daniel": False,
        "Found": False,
        "RivalTown": False,
        "GymOne": False,
        "SeenElder": False,
        "Snorlax": False,
        "DawnCity": False,
        "GymTwo": False,
        "RivalMount": False,
        "BeatDLKLPeak": False,
        "FirstTimeInGym": False,
        "SeenSister": False,
        "GymThree": False,
        "BeatChampion": False,
        "EndgameDawn": False,
    },
    "pokemon": [{"name" : "Daniel", "level" : 5}],  # list of poke objects
    "items": defaultdict(int),  # dict (string map to int)
    "stage": "LevelOne",  # string
    "pos": "default",  # default last pos
    "name": "",  # string
    "muted": True,
    "pokedex": defaultdict(int),  # list of unique ids of pokemon seen
    "trainer_states": {}
}

class Save:
    def __init__(self, name, data=None):
        # Deep copy the default template
        from copy import deepcopy
        base = deepcopy(save)

        if data:
            # Merge loaded data into base template
            for key, value in data.items():
                if key in ['items', 'pokedex']:
                    base[key].update(value)
                elif key == 'events':
                    base['events'].update(value)
                else:
                    base[key] = value

        base["name"] = name
        self.data = base

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

    def getStage(self):
        stage_name = self.data["stage"]
        try:
            if stage_name == "LevelOne" or stage_name == "LevelTwo":
                module = importlib.import_module(f"Code.{stage_name}Stage.{stage_name}")
            else:
                module = importlib.import_module(f"Code.Stages.{stage_name}.{stage_name}")
            return getattr(module, stage_name)
        except ImportError as e:
            print(f"Error loading stage {stage_name}: {e}")
            raise

    def updateStage(self, val):
        self.data["stage"] = val

    def updatePos(self, val):
        self.data["pos"] = val

    def getPos(self):
        return self.data["pos"]

    def updateItems(self, item):
        self.data["items"][item] += 1

    def getPokemon(self):
        player_pokemon = {}
        for idx, pokemon_data in enumerate(self.data["pokemon"]):
            name = pokemon_data["name"]
            level = pokemon_data["level"]
            poke = Pokemon(name, level)

            # Restore optional fields
            if "health" in pokemon_data:
                poke.health = pokemon_data["health"]
            if "energy" in pokemon_data:
                poke.energy = pokemon_data["energy"]
            if "xp" in pokemon_data:
                poke.xp = pokemon_data["xp"]

            player_pokemon[idx] = poke
        return player_pokemon

    def updatePokemon(self, poke):
        self.data["pokemon"].append(poke)

    def removePokemon(self):
        self.data["pokemon"].remove(self.data["pokemon"][0])

    def isTrainerDefeated(self, trainer_name):
        return self.data["trainer_states"].get(trainer_name, False)

    def defeatTrainer(self, trainer_name):
        self.data["trainer_states"][trainer_name] = True

    def getMuted(self):
        return self.data["muted"]

    def updateMuted(self):
        self.data["muted"] = not self.data["muted"]

    def setMute(self, boo):
        self.data["muted"] = boo

    def updateEvent(self, key):
        if key not in self.data["events"]:
            print("Event not in data!")
        self.data["events"][key] = True

    # Event check methods (unchanged from original)
    def seenMom(self): return self.data["events"]["Mom"]
    def seenDawn(self): return self.data["events"]["Dawn"]
    def seenProf(self): return self.data["events"]["Prof"]
    def homeTest(self):
        if self.seenMom() and self.seenProf(): return 2
        elif self.seenMom(): return 1
        else: return 0
    def gotDaniel(self): return self.data["events"]["Daniel"]
    def getFound(self): return self.data["events"]["Found"]
    def beatGymOne(self): return self.data["events"]["GymOne"]
    def foughtRivalAtTown(self): return self.data["events"]["RivalTown"]
    def seenElder(self): return self.data["events"]["SeenElder"]
    def wokeSnorlax(self): return self.data["events"]["Snorlax"]
    def foughtDawnAtCity(self): return self.data["events"]["DawnCity"]
    def beatGymTwo(self): return self.data["events"]["GymTwo"]
    def foughtRivalAtMount(self): return self.data["events"]["RivalMount"]
    def beatDLKLAtPeak(self): return self.data["events"]["BeatDLKLPeak"]
    def beenInGym(self): return self.data["events"]["FirstTimeInGym"]
    def seenRaysenSister(self): return self.data["events"]["SeenSister"]
    def beatGymThree(self): return self.data["events"]["GymThree"]
    def beatChampion(self): return self.data["events"]["BeatChampion"]
    def beatEndgameDawn(self): return self.data["events"]["EndgameDawn"]

class SaveSystem:
    @staticmethod
    def write(save):
        """Save game data to file with error handling."""
        try:
            save_path = os.path.join(SAVE_DIR, f"{save.data['name']}.txt")
            temp_path = f"{save_path}.tmp"

            # Write to temporary file first
            with open(temp_path, "w") as file:
                json.dump(save.data, file)

            # On Windows, we need to remove the original file first if it exists
            if os.path.exists(save_path):
                os.remove(save_path)

            # Rename temp file to final name
            os.rename(temp_path, save_path)

        except Exception as e:
            print(f"Error saving game: {e}")
            # Try to clean up temp file if it exists
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            raise

    @staticmethod
    def read(name):
        """Load game data from file with error handling."""
        try:
            save_path = os.path.join(SAVE_DIR, f"{name}.txt")

            if not os.path.exists(save_path):
                raise FileNotFoundError(f"Save file '{name}' not found")

            with open(save_path, "r") as file:
                data = json.load(file)

                # Restore defaultdicts
                data["items"] = defaultdict(int, data.get("items", {}))
                data["pokedex"] = defaultdict(int, data.get("pokedex", {}))

                return Save(name, data)

        except json.JSONDecodeError as e:
            print(f"Error parsing save file: {e}")
            raise
        except Exception as e:
            print(f"Error loading save file: {e}")
            raise

    @staticmethod
    def list_saves():
        """List all available save files."""
        try:
            saves = []
            for filename in os.listdir(SAVE_DIR):
                if filename.endswith(".txt"):
                    name = filename[:-4]  # Remove .txt extension
                    saves.append(name)
            return saves
        except Exception as e:
            print(f"Error listing saves: {e}")
            return []