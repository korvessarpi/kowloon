"""
Commands for the @nakeds system - detailed body part descriptions that can be covered by clothing.
"""

from commands.base import ArxCommand
from evennia.utils.ansi import ANSIString


# Define body parts and their short names
BODY_PARTS = {
    "leye": "left eye",
    "reye": "right eye", 
    "lear": "left ear",
    "rear": "right ear",
    "head": "head",
    "face": "face",
    "neck": "neck",
    "lshoulder": "left shoulder",
    "rshoulder": "right shoulder", 
    "larm": "left arm",
    "rarm": "right arm",
    "lhand": "left hand",
    "rhand": "right hand",
    "back": "back",
    "chest": "chest",
    "abdomen": "abdomen",
    "groin": "groin",
    "lthigh": "left thigh",
    "rthigh": "right thigh",
    "lshin": "left shin",
    "rshin": "right shin",
    "lfoot": "left foot",
    "rfoot": "right foot"
}

# Order for display (head to toe)
BODY_ORDER = [
    "head", "face", "leye", "reye", "lear", "rear", "neck",
    "lshoulder", "rshoulder", "chest", "back", "larm", "rarm", 
    "lhand", "rhand", "abdomen", "groin", "lthigh", "rthigh",
    "lshin", "rshin", "lfoot", "rfoot"
]


class CmdNakeds(ArxCommand):
    """
    View and manage detailed body part descriptions.

    Usage:
        @nakeds                    - List all your naked descriptions
        @naked <bodypart>          - View description for a specific body part
        @naked <bodypart> is <desc> - Set description for a body part
        @naked/del <bodypart>      - Delete description for a body part
        @naked/list                - Show all available body parts

    The @nakeds system allows you to set detailed descriptions for specific
    body parts of your character. These descriptions appear when someone looks
    at you, arranged from head to toe. When you wear clothing that covers
    specific body parts, those descriptions become hidden.

    Body parts available: {body_parts}

    Examples:
        @naked reye is %P right eye is a piercing blue, like ice on a winter lake.
        @naked chest is %P chest is broad and muscled from years of training.
        @naked/del face

    NOTE: Use pronoun substitution (%P, %p, %s, %o) in your descriptions so they
    adjust properly if you change your apparent gender with the 'appear' command.

    NOTE: Your main @describe should be kept light - height, weight, build, 
    ethnicity, and obvious features. Use @nakeds for detailed descriptions
    that can be covered by clothing.
    """.format(body_parts=", ".join(BODY_PARTS.keys()))

    key = "@nakeds"
    aliases = ["@naked", "+nakeds", "+naked"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        """Execute the nakeds command."""
        caller = self.caller
        
        # Initialize nakeds storage if it doesn't exist
        if not caller.attributes.has("nakeds"):
            caller.db.nakeds = {}
        
        args = self.args.strip()
        
        # Handle switches
        if "del" in self.switches or "delete" in self.switches:
            self.delete_naked_desc(args)
            return
        elif "list" in self.switches:
            self.list_body_parts()
            return
        
        # No arguments - show all nakeds
        if not args:
            self.show_all_nakeds()
            return
        
        # Check for setting description
        if " is " in args:
            self.set_naked_desc(args)
            return
        
        # Show specific body part
        self.show_naked_desc(args)

    def show_all_nakeds(self):
        """Display all naked descriptions in head-to-toe order."""
        caller = self.caller
        nakeds = caller.db.nakeds or {}
        
        if not nakeds:
            self.msg("You have no naked descriptions set. Use '@naked <bodypart> is <description>' to set them.")
            return
        
        msg = "{w=== Your Naked Descriptions ==={n\n"
        msg += "Descriptions are shown in the order they appear when someone looks at you:\n\n"
        
        count = 0
        for part in BODY_ORDER:
            if part in nakeds:
                long_name = BODY_PARTS[part]
                desc = nakeds[part]
                # Process pronoun substitution for display
                desc = caller.process_pronoun_substitution(desc)
                msg += "{c%s{n ({y%s{n): %s\n" % (long_name.title(), part, desc)
                count += 1
        
        if count == 0:
            msg += "No descriptions found.\n"
        
        msg += "\nUse '@naked <bodypart> is <description>' to add or modify descriptions."
        msg += "\nUse '@naked/del <bodypart>' to delete a description."
        msg += "\nUse '@naked/list' to see all available body parts."
        
        self.msg(msg)

    def show_naked_desc(self, bodypart):
        """Show the description for a specific body part."""
        caller = self.caller
        nakeds = caller.db.nakeds or {}
        
        # Normalize body part name
        bodypart = bodypart.lower().strip()
        
        if bodypart not in BODY_PARTS:
            self.msg("Unknown body part '%s'. Use '@naked/list' to see available parts." % bodypart)
            return
        
        if bodypart not in nakeds:
            long_name = BODY_PARTS[bodypart]
            self.msg("You have no description set for your %s." % long_name)
            return
        
        long_name = BODY_PARTS[bodypart]
        desc = nakeds[bodypart]
        # Process pronoun substitution for display
        desc = caller.process_pronoun_substitution(desc)
        
        self.msg("{c%s{n ({y%s{n): %s" % (long_name.title(), bodypart, desc))

    def set_naked_desc(self, args):
        """Set the description for a body part."""
        caller = self.caller
        
        try:
            bodypart, desc = args.split(" is ", 1)
            bodypart = bodypart.lower().strip()
            desc = desc.strip()
        except ValueError:
            self.msg("Usage: @naked <bodypart> is <description>")
            return
        
        if bodypart not in BODY_PARTS:
            self.msg("Unknown body part '%s'. Use '@naked/list' to see available parts." % bodypart)
            return
        
        if not desc:
            self.msg("You must provide a description.")
            return
        
        # Initialize if needed
        if not caller.attributes.has("nakeds"):
            caller.db.nakeds = {}
        
        nakeds = caller.db.nakeds
        nakeds[bodypart] = desc
        caller.db.nakeds = nakeds
        
        long_name = BODY_PARTS[bodypart]
        self.msg("Set description for your %s: %s" % (long_name, desc))

    def delete_naked_desc(self, bodypart):
        """Delete the description for a body part."""
        caller = self.caller
        nakeds = caller.db.nakeds or {}
        
        bodypart = bodypart.lower().strip()
        
        if bodypart not in BODY_PARTS:
            self.msg("Unknown body part '%s'. Use '@naked/list' to see available parts." % bodypart)
            return
        
        if bodypart not in nakeds:
            long_name = BODY_PARTS[bodypart]
            self.msg("You have no description set for your %s." % long_name)
            return
        
        del nakeds[bodypart]
        caller.db.nakeds = nakeds
        
        long_name = BODY_PARTS[bodypart]
        self.msg("Deleted description for your %s." % long_name)

    def list_body_parts(self):
        """List all available body parts."""
        msg = "{w=== Available Body Parts ==={n\n"
        msg += "Short name (full name):\n\n"
        
        for short, long_name in BODY_PARTS.items():
            msg += "{y%s{n (%s)\n" % (short, long_name)
        
        msg += "\nUse '@naked <bodypart> is <description>' to set descriptions."
        self.msg(msg)


class CmdNakedsHelper:
    """
    Helper class with utility methods for the nakeds system.
    """
    
    @staticmethod
    def get_visible_nakeds(character, observer):
        """
        Get the naked descriptions that are visible (not covered by clothing).
        
        Args:
            character: The character being observed
            observer: The character doing the observing
            
        Returns:
            dict: Dictionary of visible body part descriptions
        """
        nakeds = character.db.nakeds or {}
        if not nakeds:
            return {}
        
        visible_nakeds = {}
        covered_parts = CmdNakedsHelper.get_covered_body_parts(character)
        
        for bodypart, desc in nakeds.items():
            if bodypart not in covered_parts:
                visible_nakeds[bodypart] = desc
        
        return visible_nakeds
    
    @staticmethod
    def get_covered_body_parts(character):
        """
        Get a set of body parts that are covered by worn clothing.
        
        Args:
            character: The character wearing clothing
            
        Returns:
            set: Set of body part names that are covered
        """
        covered_parts = set()
        
        # Get all worn items
        worn_items = character.worn
        
        for item in worn_items:
            # Check if the item has coverage data
            coverage = getattr(item.db, 'coverage', None)
            if coverage:
                if isinstance(coverage, (list, tuple)):
                    covered_parts.update(coverage)
                elif isinstance(coverage, str):
                    covered_parts.add(coverage)
        
        return covered_parts
    
    @staticmethod
    def format_nakeds_display(character, observer):
        """
        Format the naked descriptions for display in character appearance.
        
        Args:
            character: The character being observed
            observer: The character doing the observing
            
        Returns:
            str: Formatted string of visible naked descriptions
        """
        visible_nakeds = CmdNakedsHelper.get_visible_nakeds(character, observer)
        
        if not visible_nakeds:
            return ""
        
        # Sort by display order
        ordered_nakeds = []
        for part in BODY_ORDER:
            if part in visible_nakeds:
                desc = visible_nakeds[part]
                # Process pronoun substitution
                desc = character.process_pronoun_substitution(desc)
                ordered_nakeds.append(desc)
        
        if ordered_nakeds:
            return "\n" + "\n".join(ordered_nakeds)
        
        return ""


# Make the helper available for import
__all__ = ["CmdNakeds", "CmdNakedsHelper", "BODY_PARTS", "BODY_ORDER"]