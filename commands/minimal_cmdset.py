"""
Minimal working cmdset to bypass Evennia import issues
"""
from evennia.commands.cmdset import CmdSet
from evennia.commands.command import Command


class CmdMinimalHelp(Command):
    """
    Basic help command
    """
    key = "help"
    aliases = ["?"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Execute the help command."""
        self.caller.msg("=== MINIMAL HELP ===")
        self.caller.msg("Available commands:")
        self.caller.msg("help - Show this help")
        self.caller.msg("look - Look around") 
        self.caller.msg("say <text> - Say something")
        self.caller.msg("examine [target] - Examine object (aliases: ex)")
        self.caller.msg("")
        self.caller.msg("=== ADMIN COMMANDS ===")
        self.caller.msg("@py <code> - Execute Python code")
        self.caller.msg("@cmdsets [target] - Show command sets")
        self.caller.msg("@reload - Reload server")
        self.caller.msg("@shutdown yes - Shutdown server")


class CmdMinimalLook(Command):
    """
    Basic look command
    """
    key = "look"
    aliases = ["l"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Execute the look command."""
        if self.caller.location:
            self.caller.msg(f"You are in: {self.caller.location.key}")
            self.caller.msg(self.caller.location.db.desc or "A nondescript location.")
            
            # Show other characters
            others = [obj for obj in self.caller.location.contents 
                     if obj != self.caller and obj.has_account]
            if others:
                self.caller.msg("Characters here: " + ", ".join(obj.key for obj in others))
        else:
            self.caller.msg("You are nowhere!")


class CmdMinimalSay(Command):
    """
    Basic say command
    """
    key = "say"
    aliases = ['"']
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Execute the say command."""
        if not self.args:
            self.caller.msg("Say what?")
            return
        
        message = f'{self.caller.key} says, "{self.args.strip()}"'
        self.caller.location.msg_contents(message, exclude=self.caller)
        self.caller.msg(f'You say, "{self.args.strip()}"')


class CmdMinimalPy(Command):
    """
    Basic @py command for debugging
    """
    key = "@py"
    locks = "cmd:perm(Developer)"
    help_category = "System"

    def func(self):
        """Execute Python code."""
        if not self.args:
            self.caller.msg("Execute what Python code?")
            return
        
        try:
            result = eval(self.args)
            self.caller.msg(f"Result: {result}")
        except Exception as e:
            self.caller.msg(f"Error: {e}")


class CmdExamine(Command):
    """
    Basic examine command
    """
    key = "examine"
    aliases = ["ex"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Examine an object."""
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        
        self.caller.msg(f"Name: {target.key}")
        self.caller.msg(f"Type: {target.__class__.__name__}")
        if hasattr(target, 'db') and hasattr(target.db, 'desc'):
            self.caller.msg(f"Desc: {target.db.desc or '(no description)'}")
        if hasattr(target, 'location'):
            self.caller.msg(f"Location: {target.location.key if target.location else 'None'}")


class CmdCmdSets(Command):
    """
    Show command sets on an object
    """
    key = "@cmdsets"
    locks = "cmd:perm(Developer)"
    help_category = "System"

    def func(self):
        """Show cmdsets."""
        target = self.caller
        if self.args:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        
        self.caller.msg(f"Command sets on {target.key}:")
        for cmdset in target.cmdset.all():
            self.caller.msg(f" - {cmdset}")


class CmdReload(Command):
    """
    Reload the server
    """
    key = "@reload"
    locks = "cmd:perm(Developer)"
    help_category = "System"

    def func(self):
        """Reload the server."""
        self.caller.msg("Reloading server...")
        try:
            from evennia.server.sessionhandler import SESSIONS
            # Try different possible reload methods
            if hasattr(SESSIONS, 'portal_reload_server'):
                SESSIONS.portal_reload_server()
            elif hasattr(SESSIONS, 'reload_server'):
                SESSIONS.reload_server()
            else:
                # Fallback - use the server reload mechanism
                from evennia.server.server import Server
                from evennia.utils import gametime
                self.caller.msg("Using fallback reload method...")
                # This will trigger a reload by restarting the server process
                import os
                os._exit(3)  # Exit code 3 typically means restart
        except Exception as e:
            self.caller.msg(f"Reload failed: {e}")
            self.caller.msg("Try using '@shutdown yes' and manually restarting the server.")


class CmdShutdown(Command):
    """
    Shutdown the server
    """
    key = "@shutdown"
    locks = "cmd:perm(Developer)"
    help_category = "System"

    def func(self):
        """Shutdown the server."""
        if not self.args or self.args.strip().lower() != 'yes':
            self.caller.msg("Type '@shutdown yes' to confirm server shutdown.")
            return
        
        self.caller.msg("Shutting down server...")
        from evennia import settings
        from twisted.internet import reactor
        reactor.callLater(1, reactor.stop)


class MinimalCmdSet(CmdSet):
    """
    A minimal command set that bypasses problematic Evennia imports
    """
    key = "MinimalCmdSet"
    priority = 100

    def at_cmdset_creation(self):
        """Populate the cmdset"""
        self.add(CmdMinimalHelp())
        self.add(CmdMinimalLook())
        self.add(CmdMinimalSay())
        self.add(CmdMinimalPy())
        self.add(CmdExamine())
        self.add(CmdCmdSets())
        self.add(CmdReload())
        self.add(CmdShutdown())