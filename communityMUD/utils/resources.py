"""
Resource loading utilities

This module contains functions for loading various resources used by the game.
"""

import os
from evennia import settings


def get_text_resource(filename):
    """
    Load a text resource from the resources/text directory.
    
    Args:
        filename (str): The name of the file to load, without path
        
    Returns:
        str: The contents of the file, or an error message if not found
    """
    # Construct the full path to the resource file
    resource_path = os.path.join(
        settings.GAME_DIR, 
        "resources", 
        "text", 
        filename
    )
    
    try:
        with open(resource_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Could not find resource file '{filename}'"
    except Exception as e:
        return f"Error loading resource: {e}" 