"""
Custom Account commands

This module contains commands available to accounts (users) which
replace or extend the default Evennia account commands.
"""

from evennia.commands.command import Command
from evennia.commands.default.account import CmdCharCreate as DefaultCmdCharCreate
from typeclasses.chargen import start_chargen

class CmdCharCreate(DefaultCmdCharCreate):
    """
    create a new character

    Usage:
      charcreate <charname> [= desc]

    Create a new character, optionally giving it a description. 
    Character names will be automatically capitalized.
    After creation, you will be taken through the character 
    generation process.
    """

    key = "charcreate"
    locks = "cmd:pperm(Player)"
    help_category = "General"

    # this is used by the parent
    account_caller = True

    def func(self):
        """Create the new character with a capitalized name, then start chargen"""
        account = self.account
        if not self.args:
            self.msg("Usage: charcreate <charname> [= description]")
            return
        
        # Get the character name and capitalize it
        key = self.lhs.strip().capitalize()
        description = self.rhs or "This is a character."

        # Create the character using the account's method
        new_character, errors = self.account.create_character(
            key=key, description=description, ip=self.session.address
        )

        if errors:
            # Handle specific error cases
            for error in errors:
                if "maximum of" in error:
                    self.msg(f"|rError:|n {error}")
                elif "already exists" in error:
                    self.msg(f"|rError:|n A character with the name '{key}' already exists.")
                elif "invalid" in error.lower():
                    self.msg(f"|rError:|n The name '{key}' is invalid. Names can only contain letters.")
                else:
                    self.msg(f"|rError:|n {error}")
            return

        if not new_character:
            self.msg("|rError:|n Character creation failed. Please try a different name or contact an administrator if the problem persists.")
            return

        self.msg(
            f"|gSuccess:|n Created new character {new_character.key}. Starting character generation..."
        )
        
        # Start character generation for this new character
        start_chargen(account) 