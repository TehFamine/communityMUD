"""
Character Generation System

This module handles character generation after account creation.

The workflow is:
1. Choose your character's name
2. Enter email (optional)
3. Select race (Human for now)
4. Select class (Warrior for now)
5. Confirm choices or restart

"""

import re
import traceback
from django.conf import settings
from evennia import EvMenu
from evennia.utils import dedent
from evennia.objects.models import ObjectDB
from typeclasses.races import apply_race, get_available_races
from typeclasses.classes import apply_class, get_available_classes


def node_welcome(caller, raw_text, **kwargs):
    """
    Welcome screen for character generation
    """
    text = dedent("""
    |gWelcome to Character Creation!|n
    
    You will now create your character by following these steps:
    1. Choose your character's name
    2. Enter your email (optional)
    3. Choose your race
    4. Choose your character class
    5. Review and confirm your choices
    
    Press |wenter|n to begin.
    """)
    
    options = {
        "key": "_default",
        "goto": "node_name"
    }
    
    return text, options


def node_name(caller, raw_text, **kwargs):
    """
    Character name selection screen
    """
    def _check_input(caller, raw_string, **kwargs):
        if not raw_string.strip():
            caller.msg("Please enter a name for your character.")
            return None
            
        name = raw_string.strip()
        
        # Basic name validation
        if len(name) < 2:
            caller.msg("Name must be at least 2 characters long.")
            return None
            
        if len(name) > 16:
            caller.msg("Name can be up to 16 characters long.")
            return None
            
        # Check if name contains only letters
        if not name.isalpha():
            caller.msg("Name can only contain letters (no numbers or punctuation).")
            return None
            
        # Get the current character
        character = caller.db._last_puppet
        
        # Check if name is already taken (case-insensitive), but exclude the current character
        if character:
            # Check for characters with this name that aren't the current one
            existing = ObjectDB.objects.filter(db_key__iexact=name).exclude(id=character.id)
            if existing:
                caller.msg(f"The name '{name}' is already taken. Please choose another name.")
                return None
        else:
            # If no character exists yet, check all objects
            existing = ObjectDB.objects.filter(db_key__iexact=name)
            if existing:
                caller.msg(f"The name '{name}' is already taken. Please choose another name.")
                return None
            
        # Save name to character for persistence with proper capitalization
        if character:
            # Capitalize first letter, lowercase the rest
            name = name.capitalize()
            character.key = name
            character.ndb._chargen_name = name
            
        return "node_email", kwargs
    
    text = dedent("""
    |gChoose Your Character's Name|n
    
    Please enter a name for your character.
    The name should be:
    - 2-16 characters long
    - Only contain letters (no numbers or punctuation)
    - Be unique in the game (case-insensitive)
    
    Current name: {current_name}
    
    Enter your choice:
    """).format(current_name=caller.db._last_puppet.key if caller.db._last_puppet else "None")
    
    options = {
        "key": "_default",
        "goto": _check_input
    }
    
    return text, options


def node_email(caller, raw_text, **kwargs):
    """
    Asks for email (optional)
    """
    def _check_input(caller, raw_string, **kwargs):
        if not raw_string.strip():
            caller.msg("Email skipped. You can set it later if desired.")
            
            # Save empty email to character for consistency
            character = caller.db._last_puppet
            if character:
                character.ndb._chargen_email = ""
                # Set empty email on account as well
                caller.email = ""
                caller.save()
                
            return "node_race", {"email": ""}
            
        email = raw_string.strip()
        
        # Simple email validation
        if "@" not in email or "." not in email:
            caller.msg("That doesn't look like a valid email address. Try again or press enter to skip.")
            return None
            
        # Save email to both character and account
        character = caller.db._last_puppet
        if character:
            character.ndb._chargen_email = email
            # Set email on account
            caller.email = email
            caller.save()
            
        return "node_race", {"email": email}
    
    text = dedent("""
    |gEmail Address|n
    
    Please enter your email address. This is optional but recommended 
    for account recovery.
    
    Press |wenter|n without typing anything to skip this step.
    """)
    
    options = {
        "key": "_default",
        "goto": _check_input
    }
    
    return text, options


def node_race(caller, raw_text, **kwargs):
    """
    Race selection screen
    """

    # Get email from character if it's not in kwargs
    character = caller.db._last_puppet
    email_from_kwargs = kwargs.get('email', None)
    email_from_char = character.ndb._chargen_email if (character and hasattr(character.ndb, '_chargen_email')) else None
    
    # If email is not in kwargs but is stored on character, restore it
    if email_from_kwargs is None and email_from_char is not None:
        kwargs['email'] = email_from_char

    
    def _check_input(caller, raw_string, **kwargs):
        if not raw_string.strip():
            caller.msg("Please select a race by number.")
            return None
            
        choice = raw_string.strip()

        
        try:
            index = int(choice) - 1
            if 0 <= index < len(available_races):
                selected_race = available_races[index]

                
                # Save race directly to character for persistence
                character = caller.db._last_puppet
                if character:
                    character.ndb._chargen_race = selected_race

                
                # Create a new dict with all existing kwargs plus the race
                new_kwargs = dict(kwargs)
                new_kwargs['race'] = selected_race
                
                # Ensure email is in the kwargs
                if 'email' not in new_kwargs and email_from_char is not None:
                    new_kwargs['email'] = email_from_char
                

                return "node_class", new_kwargs
            else:
                caller.msg("Invalid selection. Please enter a number from the list.")
                return None
        except ValueError:
            # Try by name
            choice = choice.title()
            if choice in available_races:

                
                # Save race directly to character for persistence
                character = caller.db._last_puppet
                if character:
                    character.ndb._chargen_race = choice

                
                # Create a new dict with all existing kwargs plus the race
                new_kwargs = dict(kwargs)
                new_kwargs['race'] = choice
                
                # Ensure email is in the kwargs
                if 'email' not in new_kwargs and email_from_char is not None:
                    new_kwargs['email'] = email_from_char
                

                return "node_class", new_kwargs
            else:
                caller.msg("Invalid race. Please select from the list.")
                return None
    
    available_races = get_available_races()
    race_list = "\n".join([f"{i+1}. {race}" for i, race in enumerate(available_races)])
    
    text = dedent(f"""
    |gChoose Your Race|n
    
    Select your character's race:
    
    {race_list}
    
    Enter the number or name of your choice:
    """)
    
    options = {
        "key": "_default",
        "goto": _check_input
    }
    
    return text, options


def node_class(caller, raw_text, **kwargs):
    """
    Class selection screen
    """
    
    # Get race and email from character if not in kwargs
    character = caller.db._last_puppet
    race_from_kwargs = kwargs.get('race', None)
    race_from_char = character.ndb._chargen_race if (character and hasattr(character.ndb, '_chargen_race')) else None
    
    email_from_kwargs = kwargs.get('email', None)
    email_from_char = character.ndb._chargen_email if (character and hasattr(character.ndb, '_chargen_email')) else None
    
    # If values are not in kwargs but stored on character, restore them
    if not race_from_kwargs and race_from_char:
        kwargs['race'] = race_from_char

        
    if email_from_kwargs is None and email_from_char is not None:
        kwargs['email'] = email_from_char

    
    def _check_input(caller, raw_string, **kwargs):
        if not raw_string.strip():
            caller.msg("Please select a class by number.")
            return None
            
        choice = raw_string.strip()

        
        try:
            index = int(choice) - 1
            if 0 <= index < len(available_classes):
                selected_class = available_classes[index]

                
                # Save class directly to character for persistence
                character = caller.db._last_puppet
                if character:
                    character.ndb._chargen_class = selected_class
                
                # Create a new dict with all existing kwargs plus the class
                new_kwargs = dict(kwargs)
                new_kwargs['char_class'] = selected_class
                
                # Ensure email and race are in the kwargs
                if 'email' not in new_kwargs and email_from_char is not None:
                    new_kwargs['email'] = email_from_char
                
                if 'race' not in new_kwargs and race_from_char:
                    new_kwargs['race'] = race_from_char
                

                return "node_confirm", new_kwargs
            else:
                caller.msg("Invalid selection. Please enter a number from the list.")
                return None
        except ValueError:
            # Try by name
            choice = choice.title()
            if choice in available_classes:

                
                # Save class directly to character for persistence
                character = caller.db._last_puppet
                if character:
                    character.ndb._chargen_class = choice
                
                # Create a new dict with all existing kwargs plus the class
                new_kwargs = dict(kwargs)
                new_kwargs['char_class'] = choice
                
                # Ensure email and race are in the kwargs
                if 'email' not in new_kwargs and email_from_char is not None:
                    new_kwargs['email'] = email_from_char
                
                if 'race' not in new_kwargs and race_from_char:
                    new_kwargs['race'] = race_from_char
                

                return "node_confirm", new_kwargs
            else:
                caller.msg("Invalid class. Please select from the list.")
                return None
    
    available_classes = get_available_classes()
    class_list = "\n".join([f"{i+1}. {cls}" for i, cls in enumerate(available_classes)])
    
    text = dedent(f"""
    |gChoose Your Class|n
    
    Select your character's class:
    
    {class_list}
    
    Enter the number or name of your choice:
    """)
    
    options = {
        "key": "_default",
        "goto": _check_input
    }
    
    return text, options


def node_confirm(caller, raw_text, **kwargs):
    """
    Confirmation screen
    """
    
    # Get race, class, and email from character if not in kwargs
    character = caller.db._last_puppet
    race_from_kwargs = kwargs.get('race', None)
    race_from_char = character.ndb._chargen_race if (character and hasattr(character.ndb, '_chargen_race')) else None
    
    class_from_kwargs = kwargs.get('char_class', None)
    class_from_char = character.ndb._chargen_class if (character and hasattr(character.ndb, '_chargen_class')) else None
    
    email_from_kwargs = kwargs.get('email', None)
    email_from_char = character.ndb._chargen_email if (character and hasattr(character.ndb, '_chargen_email')) else None
    
    # If values are not in kwargs but are stored on character, restore them
    if not race_from_kwargs and race_from_char:
        kwargs['race'] = race_from_char

        
    if not class_from_kwargs and class_from_char:
        kwargs['char_class'] = class_from_char

        
    if email_from_kwargs is None and email_from_char is not None:
        kwargs['email'] = email_from_char

    
    def _check_input(caller, raw_string, **kwargs):
        choice = raw_string.strip().lower()
        
        if choice in ("y", "yes"):
            return "node_apply_character", kwargs
        elif choice in ("n", "no"):
            caller.msg("Let's start over.")
            return "node_name", {}
        else:
            caller.msg("Please enter 'y' or 'n'.")
            return None
    
    email = kwargs.get("email", "")
    race = kwargs.get("race", "Unknown")
    char_class = kwargs.get("char_class", "Unknown")
    
    # Ensure these values are properly formatted
    # Capitalize first letter if it's not already
    if race and isinstance(race, str):
        race = race.capitalize()
    
    if char_class and isinstance(char_class, str):
        char_class = char_class.capitalize()
    
    # Display email info
    if email:
        email_display = f"Email: {email}"
    else:
        email_display = "Email: (skipped)"
    
    text = dedent(f"""
    |gConfirm Your Character|n
    
    Please review your character choices:
    
    {email_display}
    Race: {race}
    Class: {char_class}
    
    Is this correct? (y/n)
    """)
    
    options = {
        "key": "_default",
        "goto": _check_input
    }
    
    return text, options


def node_apply_character(caller, raw_text, **kwargs):
    """
    Apply character choices and complete chargen
    """
    account = caller
    character = account.db._last_puppet
    
    if not character:
        # This should not happen normally, but just in case
        caller.msg("Error: Character not found. Please contact an administrator.")
        return None
    
    # Capitalize character name
    character.key = character.key.capitalize()
    
    # Save email if provided
    email = kwargs.get("email", "")
    if email:
        account.email = email
        account.save()
        caller.msg(f"Email set to: {email}")
    
    # Apply race
    race = kwargs.get("race", "Human")
    success = apply_race(character, race)
    if not success:
        caller.msg(f"Warning: Failed to apply race '{race}'. Using default.")
        character.db.race = "Human"  # Fallback
    
    # Apply class
    char_class = kwargs.get("char_class", "Warrior")
    success = apply_class(character, char_class)
    if not success:
        caller.msg(f"Warning: Failed to apply class '{char_class}'. Using default.")
        character.db.char_class = "Warrior"  # Fallback
    
    # Mark character as having completed chargen
    character.db.chargen_complete = True
    
    # Verify the character has the correct attributes
    
    text = dedent(f"""
    |gCharacter Creation Complete!|n
    
    Congratulations! Your character has been created.
    
    Name: {character.key}
    Race: {character.db.race}
    Class: {character.db.char_class}
    
    You are now entering the world...
    """)
    
    # No options - this is the end of chargen
    return text, None


def create_default_character(account):
    """
    Create a default character for an account with basic permissions
    
    Args:
        account (Account): The account to create a character for
        
    Returns:
        Object or None: The created character or None if creation failed
    """
    # Get character typeclass
    character_typeclass = settings.BASE_CHARACTER_TYPECLASS
    
    # Create a new character with the same name as the account
    try:
        # Use proper permission strings instead of raw settings
        default_perms = ["Accounts"]
        default_locks = "edit:id(%s) or perm(Admin);call:id(%s) or perm(Admin);delete:id(%s) or perm(Admin)" % (account.id, account.id, account.id)
        
        character = ObjectDB.objects.create_object(
            typeclass=character_typeclass, 
            key=account.key,  # This will be the default name until changed
            location=None,  # Will be set by the create_character hook
            home=None,
            permissions=default_perms,
            locks=default_locks,
            tags=[("chargen", "chargen")],
        )
        
        # Link the account to the character
        character.db.account = account
        account.db._last_puppet = character
        
        # Also add to account's playable characters
        if account.db._playable_characters is None:
            account.db._playable_characters = []
        
        if character not in account.db._playable_characters:
            account.db._playable_characters.append(character)
            
        return character
            
    except Exception as e:
        account.msg(f"Error creating character: {e}")
        traceback.print_exc()
        return None


def start_chargen(account):
    """
    Start the character generation process for a given account
    
    Args:
        account (Account): The account to start chargen for
    """
    # Get the account's character
    character = account.db._last_puppet
    
    if not character:
        # Create a character if one doesn't exist
        character = create_default_character(account)
        if not character:
            return
    
    # Check if character has already completed chargen
    if character.db.chargen_complete:
        account.msg("Character generation already completed.")
        return
        
    # Start the chargen menu
    EvMenu(
        account,
        {
            "node_welcome": node_welcome,
            "node_name": node_name,
            "node_email": node_email,
            "node_race": node_race,
            "node_class": node_class,
            "node_confirm": node_confirm,
            "node_apply_character": node_apply_character,
        },
        startnode="node_welcome",
        auto_quit=True,
    ) 