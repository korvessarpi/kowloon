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
        self.caller.msg("@py <code> - Execute Python (if permitted)")


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