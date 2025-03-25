"""
Classes

This module contains base character class definitions for character creation.
Classes define a character's skills, abilities, and gameplay style.

"""

from evennia import DefaultScript
from evennia.utils.create import create_script


class ClassScript(DefaultScript):
    """
    Base script for tracking character class data.
    
    This script attaches to a character to define their class
    and provide class-specific functionality.
    """
    # Class attribute for script key
    script_key = "class_script"
    
    def at_script_creation(self):
        """
        Setup the script
        """
        self.key = self.script_key
        self.desc = "Stores character class information"
        self.persistent = True
        
        # Base class attributes
        self.db.name = "Unknown"
        self.db.desc = "No description available."
        
        # Class modifiers - to be applied to character
        self.db.stat_mods = {}
        self.db.skills = {}
        self.db.abilities = []
        self.db.starting_equipment = []
    
    def apply_class(self, character):
        """
        Apply class attributes to a character.
        
        Args:
            character (Character): The character to apply class attributes to
        """
        if not character:
            return
            
        # Store class info on character
        character.db.char_class = self.db.name
        
        # Apply any class-specific modifiers here
        # Apply skills to character
        character.db.skills = self.db.skills
        
        # Apply other class attributes as needed
        # For now, we're just storing the name and skills
        
        
class WarriorClass(ClassScript):
    """
    Warrior class implementation.
    """
    # Set the script key as class attribute
    script_key = "warrior_class"
    
    def at_script_creation(self):
        """
        Setup the warrior class
        """
        super().at_script_creation()
        
        # Key is now set from the class attribute in the parent class
        self.db.name = "Warrior"
        self.db.desc = "Warriors are skilled fighters who rely on strength and weapon mastery in combat."
        
        # Warrior class modifiers
        self.db.stat_mods = {
            # No particular stat bonuses yet
            # This would be set later when we implement stats
        }
        
        # Skills don't do anything yet - placeholder for later
        self.db.skills = {
            # Basic warrior skills
            "combat": 1,
            "survival": 1
        }
        
        self.db.starting_equipment = [
            "sword", 
            "shield", 
            "leather armor"
        ]
        

# Function to get all available classes
def get_available_classes():
    """
    Returns a list of all available character classes.
    
    Returns:
        list: List of class names
    """
    # Feels like there should be a better way to do this
    return ["Warrior"]  # For now just warriors
    

def apply_class(character, class_name):
    """
    Apply a class to a character.
    
    Args:
        character (Character): The character to apply class to
        class_name (str): The name of the class to apply
        
    Returns:
        str or True: True if successful, error message string if failed
    """
        
    class_map = {
        "warrior": WarriorClass,  # Case-insensitive matching via class_name.lower()
    }
    
    # Get the class from the mapping
    class_class = class_map.get(class_name.lower())
    
    if not class_class:
        available_classes = ", ".join(class_map.keys())
        return f"Class '{class_name}' not found. Available classes: {available_classes}"
        
    # Get all class script keys directly from class attributes
    class_keys = [cc.script_key for cc in class_map.values()]
    
    # Remove only scripts that exactly match our known class scripts
    for script in character.scripts.all():
        if script.key in class_keys:
            script.delete()
    
    # Create new class script using creation function
    class_script = create_script(class_class, obj=character)
    
    # Apply class attributes
    class_script.apply_class(character)
    
    return True 