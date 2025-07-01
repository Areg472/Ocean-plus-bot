# This file makes the commands directory a Python package
# It will be used to import all commands

# Import all commands to make them available when importing the package
from commands.hi import *
from commands.meme import *
from commands.date import *
from commands.got_a_life import *
from commands.quote import *
from commands.duck import *
from commands.question import *
from commands.dad_joke import *
from commands.translate import *
from commands.help import *
from commands.cat import *
from commands.eightball import *
from commands.mock import *
from commands.weather import *
from commands.text_to_morse import *
from commands.wikipedia import *
from commands.bonk import *
from commands.pet import *
from commands.jail import *
from commands.joke_overhead import *
from commands.github import *
from commands.mute import *
from commands.ban import *
from commands.oplusadmin import *
from commands.boardgame import *
from commands.spelling import *
from commands.gamble import *
from commands.generate_code import *

# Function to setup all commands
def setup_commands(bot):
    """
    Register all commands with the bot
    """
    # Each command module should have a setup function that registers the command
    from commands.hi import setup
    setup(bot)
    
    from commands.meme import setup
    setup(bot)
    
    from commands.date import setup
    setup(bot)
    
    from commands.got_a_life import setup
    setup(bot)
    
    from commands.quote import setup
    setup(bot)
    
    from commands.duck import setup
    setup(bot)
    
    from commands.question import setup
    setup(bot)
    
    from commands.dad_joke import setup
    setup(bot)
    
    from commands.translate import setup
    setup(bot)
    
    from commands.help import setup
    setup(bot)
    
    from commands.cat import setup
    setup(bot)
    
    from commands.eightball import setup
    setup(bot)
    
    from commands.mock import setup
    setup(bot)
    
    from commands.weather import setup
    setup(bot)
    
    from commands.text_to_morse import setup
    setup(bot)
    
    from commands.wikipedia import setup
    setup(bot)
    
    from commands.bonk import setup
    setup(bot)
    
    from commands.pet import setup
    setup(bot)
    
    from commands.jail import setup
    setup(bot)
    
    from commands.joke_overhead import setup
    setup(bot)
    
    from commands.github import setup
    setup(bot)
    
    from commands.mute import setup
    setup(bot)
    
    from commands.ban import setup
    setup(bot)
    
    from commands.oplusadmin import setup
    setup(bot)
    
    from commands.boardgame import setup
    setup(bot)
    
    from commands.spelling import setup
    setup(bot)
    
    from commands.gamble import setup
    setup(bot)
    
    from commands.generate_code import setup
    setup(bot)
