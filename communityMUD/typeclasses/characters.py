"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """
    
    def at_object_creation(self):
        """
        Called when the character is first created.
        """
        # Initialize basic attributes
        self.db.race = None
        self.db.char_class = None
        self.db.chargen_complete = False
        
        # Basic stats placeholder
        self.db.stats = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }
        
        # Skills placeholder
        self.db.skills = {}
        
        # Equipment slots
        self.db.equipment = {
            "head": None,
            "neck": None,
            "shoulders": None,
            "chest": None,
            "back": None,
            "arms": None,
            "hands": None,
            "waist": None,
            "legs": None,
            "feet": None,
            "main_hand": None,
            "off_hand": None
        }
        
        # Inventory capacity
        self.db.max_inventory = 20
        
        # Set default locks
        """ 
            1. get:false()
            Action: Picking up/obtaining the object.

            Restriction: false() means no one can take this object.

            Effect: The object is permanently immovable.

            2. call:false()
            Action: "Calling" the object (using it as a command).

            Restriction: false() blocks all usage as a command.

            Effect: Prevents players from executing this object like a script.

            3. puppet:id(%i) or perm(Developer) or pperm(Developer)
            Action: "Puppeting" (controlling the object, typically a Character).

            Restrictions:

            id(%i): Only the account/character with the same database ID as this object (self.id).

            perm(Developer): Accounts with the Developer permission.

            pperm(Developer): Characters with the Developer permission.

            Effect: Owner, Developers, or Dev-authorized characters can control this object.

            4. delete:id(%i) or perm(Admin)
            Action: Deleting the object.

            Restrictions:

            id(%i): Owner (matching self.id).

            perm(Admin): Accounts with Admin privileges.

            Effect: Only the owner or Admins can permanently delete the object.
        """
        self.locks.add("get:false();call:false();puppet:id(%i) or perm(Developer) or pperm(Developer);delete:id(%i) or perm(Admin)" % (self.id, self.id))
        
    def get_display_name(self, looker=None, **kwargs):
        """
        Displays the name of the character with race and class info
        if available.
        """
        name = self.key
        
        if self.db.chargen_complete and self.db.race and self.db.char_class:
            return f"{name} the {self.db.race} {self.db.char_class}"
        
        return name
