"""
Character Commands

Commands related to character information and attributes.
"""

from evennia import Command
from evennia.utils import dedent


class CmdScore(Command):
    """
    Show character information and statistics
    
    Usage:
      score
    
    Displays your character's information including race, class,
    and basic attributes.
    """
    
    key = "score"
    aliases = ["sc", "stat", "stats"]
    lock = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        """
        Implement the command
        """
        caller = self.caller
        
        if not caller.db.chargen_complete:
            caller.msg("You have not completed character creation. Type 'look' to continue.")
            return
        
        # Get basic character information
        name = caller.name
        race = caller.db.race or "Unknown"
        char_class = caller.db.char_class or "Unknown"
        
        # Placeholder for stats in chargen, if we use these type of stats
        stats = caller.db.stats or {}
        strength = stats.get("strength", 1)
        dexterity = stats.get("dexterity", 1)
        constitution = stats.get("constitution", 1)
        intelligence = stats.get("intelligence", 1)
        wisdom = stats.get("wisdom", 1)
        charisma = stats.get("charisma", 1)
        
        # Get skills if any
        skills = caller.db.skills or {}
        skill_text = ""
        if skills:
            skill_list = [f"{skill}: {value}" for skill, value in skills.items()]
            skill_text = "Skills: " + ", ".join(skill_list)
        else:
            skill_text = "Skills: None"
        
        # Format the output
        text = dedent(f"""
        |y==============================================================|n
        |c{name}|n, the |g{race} {char_class}|n
        |y==============================================================|n
        
        |CStrength:|n      {strength}
        |CDexterity:|n     {dexterity}
        |CConstitution:|n  {constitution}
        |CIntelligence:|n  {intelligence}
        |CWisdom:|n        {wisdom}
        |CCharisma:|n      {charisma}
        
        {skill_text}
        
        |y==============================================================|n
        """)
        
        caller.msg(text)


class CmdCharacterInfo(Command):
    """
    Show detailed character information
    
    Usage:
      charinfo
    
    Displays detailed information about your character including
    creation details and other metadata.
    """
    
    key = "charinfo"
    aliases = ["char", "cinfo"]
    lock = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        """
        Implement the command
        """
        caller = self.caller
        
        # Get account information if available
        account = caller.account
        email = account.email if account else "Unknown"
        
        # Get character details
        race = caller.db.race or "Unknown"
        char_class = caller.db.char_class or "Unknown"
        chargen_complete = "Yes" if caller.db.chargen_complete else "No"
        
        # Get any race/class scripts
        race_script = None
        class_script = None
        
        for script in caller.scripts.all():
            if script.key.endswith("_race"):
                race_script = script
            elif script.key.endswith("_class"):
                class_script = script
        
        race_desc = race_script.db.desc if race_script else "No description available"
        class_desc = class_script.db.desc if class_script else "No description available"
        
        # Format the output
        text = dedent(f"""
        |y==============================================================|n
        |cCharacter Information for {caller.name}|n
        |y==============================================================|n
        
        |CAccount:|n       {account.name if account else "Not linked"}
        |CEmail:|n         {email}
        |CRace:|n          {race}
        |CClass:|n         {char_class}
        |CChargen:|n       {chargen_complete}
        
        |CRace Description:|n
        {race_desc}
        
        |CClass Description:|n
        {class_desc}
        
        |y==============================================================|n
        """)
        
        caller.msg(text) 