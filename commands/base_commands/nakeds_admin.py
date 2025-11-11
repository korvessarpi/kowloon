"""
Admin commands for setting clothing coverage for the nakeds system.
"""

from commands.base import ArxCommand
from commands.base_commands.nakeds import BODY_PARTS


class CmdSetCoverage(ArxCommand):
    """
    Set body part coverage for clothing and armor items.

    Usage:
        @coverage <item>                    - View current coverage for an item
        @coverage <item>=<bodypart>,<bodypart>,...  - Set coverage for an item
        @coverage/del <item>                - Remove all coverage from an item

    This command allows builders and admins to set which body parts
    are covered by clothing and armor items. When a character wears
    an item, their naked descriptions for covered body parts will
    be hidden from view.

    Available body parts: {body_parts}

    Examples:
        @coverage shirt=chest,abdomen,back
        @coverage helmet=head,face
        @coverage gloves=lhand,rhand
        @coverage/del pants
    """.format(body_parts=", ".join(BODY_PARTS.keys()))

    key = "@coverage"
    locks = "cmd:perm(builders)"
    help_category = "Building"

    def func(self):
        """Execute the coverage command."""
        if not self.args:
            self.msg("Usage: @coverage <item>[=<bodyparts>]")
            return

        # Handle deletion switch
        if "del" in self.switches or "delete" in self.switches:
            self.delete_coverage()
            return

        # Parse arguments
        if "=" in self.args:
            item_name, coverage_str = self.args.split("=", 1)
            item_name = item_name.strip()
            coverage_str = coverage_str.strip()
        else:
            item_name = self.args.strip()
            coverage_str = None

        # Find the item
        item = self.caller.search(item_name)
        if not item:
            return

        # Check if it's wearable
        if not hasattr(item, 'is_worn'):
            self.msg("That item is not wearable.")
            return

        # If no coverage specified, show current coverage
        if not coverage_str:
            self.show_coverage(item)
            return

        # Set coverage
        self.set_coverage(item, coverage_str)

    def show_coverage(self, item):
        """Show the current coverage for an item."""
        coverage = getattr(item.db, 'coverage', None)
        
        if not coverage:
            self.msg(f"{item.name} has no body part coverage set.")
            return

        if isinstance(coverage, (list, tuple)):
            coverage_list = list(coverage)
        else:
            coverage_list = [coverage]

        # Convert short names to long names for display
        long_names = []
        for part in coverage_list:
            if part in BODY_PARTS:
                long_names.append(f"{BODY_PARTS[part]} ({part})")
            else:
                long_names.append(part)

        self.msg(f"{item.name} covers: {', '.join(long_names)}")

    def set_coverage(self, item, coverage_str):
        """Set the coverage for an item."""
        # Parse the coverage string
        parts = [part.strip().lower() for part in coverage_str.split(",")]
        
        # Validate body parts
        invalid_parts = []
        valid_parts = []
        
        for part in parts:
            if part in BODY_PARTS:
                valid_parts.append(part)
            else:
                invalid_parts.append(part)

        if invalid_parts:
            self.msg(f"Invalid body parts: {', '.join(invalid_parts)}")
            self.msg(f"Valid parts: {', '.join(BODY_PARTS.keys())}")
            return

        # Set the coverage
        item.db.coverage = valid_parts
        
        # Show confirmation
        long_names = [f"{BODY_PARTS[part]} ({part})" for part in valid_parts]
        self.msg(f"Set {item.name} to cover: {', '.join(long_names)}")

    def delete_coverage(self):
        """Delete coverage from an item."""
        if not self.args:
            self.msg("Usage: @coverage/del <item>")
            return

        item = self.caller.search(self.args.strip())
        if not item:
            return

        if not hasattr(item, 'is_worn'):
            self.msg("That item is not wearable.")
            return

        if hasattr(item.db, 'coverage'):
            del item.db.coverage
            self.msg(f"Removed all coverage from {item.name}.")
        else:
            self.msg(f"{item.name} has no coverage to remove.")


class CmdNakedsAdmin(ArxCommand):
    """
    Admin command to view and manage naked descriptions for any character.

    Usage:
        @nakeds <character>                    - View all nakeds for a character
        @nakeds <character>/<bodypart>         - View specific bodypart for character  
        @nakeds/del <character>/<bodypart>     - Delete a naked description
        @nakeds/clear <character>              - Clear all naked descriptions

    This command allows staff to view and manage naked descriptions
    for any character for moderation purposes.

    Examples:
        @nakeds testchar
        @nakeds testchar/face
        @nakeds/del testchar/chest
        @nakeds/clear testchar
    """

    key = "@nakeds"
    locks = "cmd:perm(builders)"
    help_category = "Admin"

    def func(self):
        """Execute the admin nakeds command."""
        if not self.args:
            self.msg("Usage: @nakeds <character>[/<bodypart>]")
            return

        # Handle switches
        if "clear" in self.switches:
            self.clear_nakeds()
            return
        elif "del" in self.switches or "delete" in self.switches:
            self.delete_naked()
            return

        # Parse character and bodypart
        if "/" in self.args:
            char_name, bodypart = self.args.split("/", 1)
            char_name = char_name.strip()
            bodypart = bodypart.strip().lower()
        else:
            char_name = self.args.strip()
            bodypart = None

        # Find the character
        character = self.caller.search(char_name, global_search=True)
        if not character:
            return

        if not hasattr(character, 'db'):
            self.msg("That is not a character.")
            return

        # Show nakeds
        if bodypart:
            self.show_character_naked(character, bodypart)
        else:
            self.show_character_nakeds(character)

    def show_character_nakeds(self, character):
        """Show all naked descriptions for a character."""
        nakeds = character.db.nakeds or {}
        
        if not nakeds:
            self.msg(f"{character.name} has no naked descriptions set.")
            return

        from commands.base_commands.nakeds import BODY_ORDER, BODY_PARTS
        
        msg = "{w}=== Naked Descriptions for %s ==={n}\n" % character.name
        
        for part in BODY_ORDER:
            if part in nakeds:
                long_name = BODY_PARTS[part]
                desc = nakeds[part]
                msg += "{c%s{n} ({y%s{n}): %s\n" % (long_name.title(), part, desc)
        
        self.msg(msg)

    def show_character_naked(self, character, bodypart):
        """Show a specific naked description for a character."""
        nakeds = character.db.nakeds or {}
        
        if bodypart not in BODY_PARTS:
            self.msg(f"Unknown body part '{bodypart}'. Valid parts: {', '.join(BODY_PARTS.keys())}")
            return

        if bodypart not in nakeds:
            long_name = BODY_PARTS[bodypart]
            self.msg(f"{character.name} has no description set for {long_name}.")
            return

        long_name = BODY_PARTS[bodypart]
        desc = nakeds[bodypart]
        self.msg(f"{character.name}'s {long_name}: {desc}")

    def delete_naked(self):
        """Delete a naked description."""
        if "/" not in self.args:
            self.msg("Usage: @nakeds/del <character>/<bodypart>")
            return

        char_name, bodypart = self.args.split("/", 1)
        char_name = char_name.strip()
        bodypart = bodypart.strip().lower()

        character = self.caller.search(char_name, global_search=True)
        if not character:
            return

        if not hasattr(character, 'db'):
            self.msg("That is not a character.")
            return

        nakeds = character.db.nakeds or {}
        
        if bodypart not in BODY_PARTS:
            self.msg(f"Unknown body part '{bodypart}'. Valid parts: {', '.join(BODY_PARTS.keys())}")
            return

        if bodypart not in nakeds:
            long_name = BODY_PARTS[bodypart]
            self.msg(f"{character.name} has no description for {long_name}.")
            return

        del nakeds[bodypart]
        character.db.nakeds = nakeds
        
        long_name = BODY_PARTS[bodypart]
        self.msg(f"Deleted {character.name}'s {long_name} description.")

    def clear_nakeds(self):
        """Clear all naked descriptions for a character."""
        if not self.args:
            self.msg("Usage: @nakeds/clear <character>")
            return

        character = self.caller.search(self.args.strip(), global_search=True)
        if not character:
            return

        if not hasattr(character, 'db'):
            self.msg("That is not a character.")
            return

        nakeds = character.db.nakeds or {}
        count = len(nakeds)
        
        character.db.nakeds = {}
        self.msg(f"Cleared {count} naked descriptions from {character.name}.")


# Make commands available for import
__all__ = ["CmdSetCoverage", "CmdNakedsAdmin"]