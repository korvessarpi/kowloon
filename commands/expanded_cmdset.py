"""
Expanded Command Set for Superuser
This bypasses Evennia framework import issues by implementing commands directly.
"""

try:
    from evennia.commands.command import Command
except ImportError:
    # Fallback if Command import fails
    class Command:
        def __init__(self):
            self.key = ""
            self.locks = "cmd:all()"
            self.help_category = "General"
        def func(self):
            self.caller.msg("Command unavailable.")

try:
    from evennia import CmdSet
except ImportError:
    class CmdSet:
        def __init__(self):
            pass
        def add(self, cmd):
            pass

class CmdWho(Command):
    """
    List connected players
    Usage: who
    """
    key = "who"
    aliases = ["w", "@who"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        from evennia.objects.models import ObjectDB
        from evennia.accounts.models import AccountDB
        
        connected_accounts = []
        for account in AccountDB.objects.filter(db_is_connected=True):
            connected_accounts.append(account)
        
        if not connected_accounts:
            self.caller.msg("No one is connected.")
            return
        
        self.caller.msg(f"|wConnected Players ({len(connected_accounts)}):|n")
        for account in connected_accounts:
            char_name = "None"
            if account.puppet:
                char_name = account.puppet.key
            self.caller.msg(f" {account.key} ({char_name})")

class CmdGo(Command):
    """
    Move through exits
    Usage: go <direction/exit>
    """
    key = "go"
    aliases = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", 
              "up", "down", "n", "s", "e", "w", "ne", "nw", "se", "sw", "u", "d"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args:
            direction = self.cmdstring.lower()
        else:
            direction = self.args.strip().lower()
        
        # Look for exit
        for exit_obj in self.caller.location.exits:
            if direction in [exit_obj.key.lower()] + [alias.lower() for alias in exit_obj.aliases.all()]:
                exit_obj.at_traverse(self.caller, exit_obj.destination)
                return
        
        self.caller.msg(f"You can't go '{direction}' from here.")

class CmdGet(Command):
    """
    Pick up objects
    Usage: get <object>
    """
    key = "get"
    aliases = ["take", "pick"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args:
            self.caller.msg("Get what?")
            return
        
        obj = self.caller.search(self.args.strip(), location=self.caller.location)
        if not obj:
            return
        
        if obj == self.caller:
            self.caller.msg("You can't pick yourself up.")
            return
        
        if not obj.access(self.caller, 'get'):
            self.caller.msg(f"You can't pick up {obj.key}.")
            return
        
        obj.move_to(self.caller, quiet=True)
        self.caller.msg(f"You pick up {obj.key}.")
        self.caller.location.msg_contents(f"{self.caller.key} picks up {obj.key}.", exclude=self.caller)

class CmdDrop(Command):
    """
    Drop objects
    Usage: drop <object>
    """
    key = "drop"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args:
            self.caller.msg("Drop what?")
            return
        
        obj = self.caller.search(self.args.strip(), location=self.caller)
        if not obj:
            return
        
        obj.move_to(self.caller.location, quiet=True)
        self.caller.msg(f"You drop {obj.key}.")
        self.caller.location.msg_contents(f"{self.caller.key} drops {obj.key}.", exclude=self.caller)

class CmdInventory(Command):
    """
    Show inventory
    Usage: inventory
    """
    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        items = self.caller.contents
        if not items:
            self.caller.msg("You are not carrying anything.")
            return
        
        self.caller.msg("|wYou are carrying:|n")
        for item in items:
            self.caller.msg(f" {item.key}")

class CmdSay(Command):
    """
    Speak to others in the room
    Usage: say <message>
    """
    key = "say"
    aliases = ["'", '"']
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        if not self.args:
            self.caller.msg("Say what?")
            return
        
        message = self.args.strip()
        self.caller.msg(f'You say, "{message}"')
        self.caller.location.msg_contents(
            f'{self.caller.key} says, "{message}"',
            exclude=self.caller
        )

class CmdTeleport(Command):
    """
    Teleport to a location (Staff only)
    Usage: @tel <location or player>
    """
    key = "@tel"
    aliases = ["@teleport"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.args:
            self.caller.msg("Teleport where?")
            return
        
        # Try to find target
        target = self.caller.search(self.args.strip(), global_search=True)
        if not target:
            return
        
        # If it's a character, go to their location
        if hasattr(target, 'location') and target.location:
            destination = target.location
        else:
            destination = target
        
        old_location = self.caller.location
        self.caller.move_to(destination, quiet=True)
        self.caller.msg(f"You teleport to {destination.key}.")
        if old_location:
            old_location.msg_contents(f"{self.caller.key} disappears.", exclude=self.caller)
        destination.msg_contents(f"{self.caller.key} appears.", exclude=self.caller)

class CmdCreate(Command):
    """
    Create new objects (Staff only)
    Usage: @create <name>
    """
    key = "@create"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.args:
            self.caller.msg("Create what?")
            return
        
        from evennia import create_object
        
        name = self.args.strip()
        new_obj = create_object("typeclasses.objects.Object", key=name, location=self.caller.location)
        self.caller.msg(f"You create {new_obj.key} (#{new_obj.id}).")

class CmdDestroy(Command):
    """
    Destroy objects (Staff only)
    Usage: @destroy <object>
    """
    key = "@destroy"
    aliases = ["@del"]
    locks = "cmd:perm(Admin)"
    help_category = "Building"

    def func(self):
        if not self.args:
            self.caller.msg("Destroy what?")
            return
        
        target = self.caller.search(self.args.strip(), global_search=True)
        if not target:
            return
        
        if target == self.caller:
            self.caller.msg("You cannot destroy yourself.")
            return
        
        name = target.key
        target.delete()
        self.caller.msg(f"You destroy {name}.")

class CmdDig(Command):
    """
    Create new rooms and exits (Staff only)
    Usage: @dig <roomname> = <exit>, <return exit>
    """
    key = "@dig"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: @dig <roomname> = <exit>, <return exit>")
            return
        
        from evennia import create_object
        
        if "=" not in self.args:
            # Just create a room
            room_name = self.args.strip()
            new_room = create_object("typeclasses.rooms.Room", key=room_name)
            self.caller.msg(f"Created room '{room_name}' (#{new_room.id}).")
            return
        
        room_name, exits = self.args.split("=", 1)
        room_name = room_name.strip()
        
        # Create the room
        new_room = create_object("typeclasses.rooms.Room", key=room_name)
        
        # Create exits
        if exits.strip():
            exit_parts = [e.strip() for e in exits.split(",")]
            if len(exit_parts) >= 1:
                # Create exit from here to new room
                exit_there = create_object("typeclasses.exits.Exit", 
                                         key=exit_parts[0], 
                                         location=self.caller.location)
                exit_there.destination = new_room
                
            if len(exit_parts) >= 2:
                # Create return exit
                exit_back = create_object("typeclasses.exits.Exit",
                                        key=exit_parts[1],
                                        location=new_room)
                exit_back.destination = self.caller.location
        
        self.caller.msg(f"Created room '{room_name}' with exits.")

class CmdBoot(Command):
    """
    Disconnect a player (Staff only)
    Usage: @boot <player>
    """
    key = "@boot"
    locks = "cmd:perm(Admin)"
    help_category = "Administration"

    def func(self):
        if not self.args:
            self.caller.msg("Boot whom?")
            return
        
        from evennia.accounts.models import AccountDB
        
        target = AccountDB.objects.filter(username__icontains=self.args.strip()).first()
        if not target:
            self.caller.msg("Player not found.")
            return
        
        if target.is_superuser and not self.caller.account.is_superuser:
            self.caller.msg("You cannot boot a superuser.")
            return
        
        target.disconnect_session_from_account()
        self.caller.msg(f"You boot {target.username}.")

class CmdStats(Command):
    """
    Show server statistics
    Usage: @stats
    """
    key = "@stats"
    locks = "cmd:perm(Developer)"
    help_category = "Administration"

    def func(self):
        from evennia.accounts.models import AccountDB
        from evennia.objects.models import ObjectDB
        from django.contrib.sessions.models import Session
        
        total_accounts = AccountDB.objects.count()
        connected_accounts = AccountDB.objects.filter(db_is_connected=True).count()
        total_objects = ObjectDB.objects.count()
        active_sessions = Session.objects.count()
        
        self.caller.msg("|wServer Statistics:|n")
        self.caller.msg(f"Total Accounts: {total_accounts}")
        self.caller.msg(f"Connected: {connected_accounts}")
        self.caller.msg(f"Total Objects: {total_objects}")
        self.caller.msg(f"Active Sessions: {active_sessions}")

class ExpandedCmdSet(CmdSet):
    """
    Expanded command set with essential MUD commands
    """
    key = "ExpandedCmdSet"
    priority = 102  # Higher than minimal set

    def at_cmdset_creation(self):
        """Add all the expanded commands"""
        # Import our minimal commands too
        from commands.minimal_cmdset import (CmdMinimalHelp, CmdMinimalLook, 
                                           CmdMinimalSay, CmdMinimalPy, 
                                           CmdExamine, CmdCmdSets, CmdReload, CmdShutdown)
        
        # Add minimal commands
        self.add(CmdMinimalHelp())
        self.add(CmdMinimalLook())
        self.add(CmdMinimalSay()) 
        self.add(CmdMinimalPy())
        self.add(CmdExamine())
        self.add(CmdCmdSets())
        self.add(CmdReload())
        self.add(CmdShutdown())
        
        # Add expanded commands
        self.add(CmdWho())
        self.add(CmdGo())
        self.add(CmdGet())
        self.add(CmdDrop())
        self.add(CmdInventory())
        self.add(CmdSay())  # Enhanced version
        self.add(CmdTeleport())
        self.add(CmdCreate())
        self.add(CmdDestroy())
        self.add(CmdDig())
        self.add(CmdBoot())
        self.add(CmdStats())