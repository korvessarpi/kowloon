"""

CmdSet for Guests - will be a limited version of player
commandset, with unique commands for the tutorial.
"""

from evennia.commands.cmdset import CmdSet
try:
    from evennia.commands.default import comms
except Exception:
    # Import Command base class for proper mock commands
    from evennia.commands.command import Command
    # Create a fallback comms module with stub commands
    class MockComms:
        class CmdAddCom(Command):
            key = '@addcom'
            help_category = 'Comms'
            locks = 'cmd:false()'
            def func(self):
                self.caller.msg('(@addcom is unavailable in this build.)')
        class CmdDelCom(Command):
            key = '@delcom'
            help_category = 'Comms'
            locks = 'cmd:false()'
            def func(self):
                self.caller.msg('(@delcom is unavailable in this build.)')
        class CmdAllCom(Command):
            key = '@allcom'
            help_category = 'Comms'
            locks = 'cmd:false()'
            def func(self):
                self.caller.msg('(@allcom is unavailable in this build.)')
        class CmdChannels(Command):
            key = '@channels'
            help_category = 'Comms'
            locks = 'cmd:false()'
            def func(self):
                self.caller.msg('(@channels is unavailable in this build.)')
        class CmdCWho(Command):
            key = '@cwho'
            help_category = 'Comms'
            locks = 'cmd:false()'
            def func(self):
                self.caller.msg('(@cwho is unavailable in this build.)')
    comms = MockComms()
from evennia.commands.default import account
import sys
import traceback
from commands.base_commands import help


class GuestCmdSet(CmdSet):
    """
    Implements the guest command set.
    """

    key = "DefaultGuest"
    # priority = -5

    def at_cmdset_creation(self):
        """Populates the cmdset"""

        # Player-specific commands
        try:
            self.add(account.CmdOOCLook())
            from commands.base_commands import overrides

            self.add(overrides.CmdWho())
            self.add(account.CmdQuit())
            self.add(account.CmdColorTest())
            self.add(account.CmdOption())
            # Help command
            self.add(help.CmdHelp())
            # Comm commands
            self.add(comms.CmdAddCom())
            self.add(comms.CmdDelCom())
            self.add(comms.CmdAllCom())
            self.add(comms.CmdChannels())
            self.add(comms.CmdCWho())
            from commands.base_commands import general

            self.add(general.CmdPage())
            from commands.base_commands import roster

            self.add(roster.CmdRosterList())
            self.add(roster.CmdAdminRoster())
            self.add(roster.CmdSheet())
            self.add(roster.CmdRelationship())
            from commands.base_commands import guest

            self.add(guest.CmdGuestLook())
            self.add(guest.CmdGuestCharCreate())
            self.add(guest.CmdGuestPrompt())
            self.add(guest.CmdGuestAddInput())
            from world.dominion import general_dominion_commands as domcommands

            self.add(domcommands.CmdFamily())
            from commands.base_commands import bboards

            self.add(bboards.CmdBBReadOrPost())
            self.add(bboards.CmdBBSub())
            from commands.base_commands import staff_commands

            self.add(staff_commands.CmdAskStaff())
            self.add(staff_commands.CmdListStaff())
            from commands.base_commands import social

            self.add(social.CmdWhere())
            self.add(social.CmdFinger())
            self.add(social.CmdCensus())
            from web.helpdesk import lore_commands

            self.add(lore_commands.CmdLoreSearch())
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)
            print("Error encountered in loading Guest commandset: %s" % err)
