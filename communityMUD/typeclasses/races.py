"""
Races

This module contains base race classes for character creation.
Races define inherent character traits and abilities.

"""

from evennia import DefaultScript
from evennia.utils.create import create_script


class RaceScript(DefaultScript):
    """
    Base script for tracking race data.
    
    This script attaches to a character to define their race
    and provide race-specific functionality.
    """
    # Class attribute for script key
    script_key = "race_script"
    
    def at_script_creation(self):
        """
        Setup the script
        """
        self.key = self.script_key
        self.desc = "Stores race information"
        self.persistent = True
        
        # Base race attributes
        self.db.name = "Unknown"
        self.db.desc = "No description available."
        
        # Race modifiers - to be applied to character
        self.db.stat_mods = {}
        self.db.skills = {}
        self.db.languages = []
        self.db.abilities = []
    
    def apply_race(self, character):
        """
        Apply race attributes to a character.
        
        Args:
            character (Character): The character to apply race attributes to
        """
        if not character:
            return
            
        # Store race info on character
        character.db.race = self.db.name
        
        # Apply any race-specific stat modifiers here
        # For now, we're just storing the name
        
        
class HumanRace(RaceScript):
    """
    Human race implementation.
    """
    # Set the script key as class attribute
    script_key = "human_race"
    
    def at_script_creation(self):
        """
        Setup the human race
        """
        super().at_script_creation()
        
        # Key is now set from the class attribute in the parent class
        self.db.name = "Human"
        self.db.desc = "Humans are the most common race, known for their adaptability and versatility."
        
        # Human race modifiers
        # These would modify base attributes when applied
        self.db.stat_mods = {
            # No particular stat bonuses/penalties for humans
            # They're the baseline race
        }
        
        self.db.languages = ["common"]
        

# Function to get all available races
def get_available_races():
    """
    Returns a list of all available races.
    
    Returns:
        list: List of race class names
    """
    return ["Human"]  # For now just humans
    

def apply_race(character, race_name):
    """
    Apply a race to a character.
    
    Args:
        character (Character): The character to apply the race to
        race_name (str): The name of the race to apply
        
    Returns:
        str or True: True if successful, error message string if failed
    """
    race_map = {
        "human": HumanRace,  # Case-insensitive matching via race_name.lower()
    }
    
    # Get the race class from the mapping
    race_class = race_map.get(race_name.lower())
    
    if not race_class:
        available_races = ", ".join(race_map.keys())
        return f"Race '{race_name}' not found. Available races: {available_races}"
        
    # Get all race script keys directly from class attributes
    race_keys = [rc.script_key for rc in race_map.values()]
    
    # Remove only scripts that exactly match our known race scripts
    for script in character.scripts.all():
        if script.key in race_keys:
            script.delete()
    
    # Create new race script using the correct creation function
    race_script = create_script(race_class, obj=character)
    
    # Apply race attributes
    race_script.apply_race(character)
    
    return True 