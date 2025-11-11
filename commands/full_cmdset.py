"""
Full Command Set with Nakeds Integration
This uses the standard Evennia cmdsets and adds custom commands.
"""

from evennia.commands.default import cmdset_character
from evennia import CmdSet

class FullCharacterCmdSet(cmdset_character.CharacterCmdSet):
    """
    Full Evennia character cmdset with nakeds integration
    """
    key = "FullCharacter"
    
    def at_cmdset_creation(self):
        """
        Add the full Evennia command set plus nakeds
        """
        # Get the default Evennia character commands (including help)
        super().at_cmdset_creation()
        
        # Add nakeds commands
        try:
            from commands.base_commands.nakeds import CmdNakeds
            from commands.base_commands.nakeds_admin import CmdNakedsAdmin, CmdNakedsToggle, CmdNakedsEdit
            
            self.add(CmdNakeds())
            self.add(CmdNakedsAdmin())
            self.add(CmdNakedsToggle())
            self.add(CmdNakedsEdit())
        except ImportError as e:
            print(f"Could not import nakeds commands: {e}")
        
        # Add other custom commands if they exist
        try:
            from commands.base_commands.general import CmdOOCSay, CmdDirections
            self.add(CmdOOCSay())
            self.add(CmdDirections())
        except ImportError:
            pass