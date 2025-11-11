"""
Example clothing items with nakeds coverage for testing the system.
Run this in-game with '@py exec(open("world/nakeds_examples.py").read())'
"""

def create_example_clothing():
    """Create example clothing items with coverage."""
    from typeclasses.wearable.wearable import Wearable
    
    # Create a shirt
    shirt = Wearable.create("a cotton shirt", desc="A simple cotton shirt.")
    shirt.db.coverage = ["chest", "abdomen", "back"]
    shirt.item_data.slot = "chest"
    shirt.item_data.slot_limit = 1
    
    # Create pants  
    pants = Wearable.create("cotton pants", desc="A pair of comfortable cotton pants.")
    pants.db.coverage = ["groin", "lthigh", "rthigh"]
    pants.item_data.slot = "legs" 
    pants.item_data.slot_limit = 1
    
    # Create boots
    boots = Wearable.create("leather boots", desc="Sturdy leather boots.")
    boots.db.coverage = ["lfoot", "rfoot", "lshin", "rshin"]
    boots.item_data.slot = "feet"
    boots.item_data.slot_limit = 1
    
    # Create gloves
    gloves = Wearable.create("leather gloves", desc="Well-made leather gloves.")
    gloves.db.coverage = ["lhand", "rhand"]
    gloves.item_data.slot = "hands"
    gloves.item_data.slot_limit = 1
    
    # Create helmet
    helmet = Wearable.create("steel helmet", desc="A protective steel helmet.")
    helmet.db.coverage = ["head", "face"]
    helmet.item_data.slot = "head"
    helmet.item_data.slot_limit = 1
    
    print("Created example clothing items:")
    print(f"- {shirt.name} (covers: {shirt.db.coverage})")
    print(f"- {pants.name} (covers: {pants.db.coverage})")
    print(f"- {boots.name} (covers: {boots.db.coverage})")
    print(f"- {gloves.name} (covers: {gloves.db.coverage})")
    print(f"- {helmet.name} (covers: {helmet.db.coverage})")
    
    return [shirt, pants, boots, gloves, helmet]

def setup_test_character():
    """Set up a test character with example naked descriptions."""
    from evennia import search_object
    
    # Find the current character (assumes this is run by a player)
    char = caller if 'caller' in globals() else None
    if not char:
        print("No character found. Run this command in-game.")
        return
    
    # Set up example naked descriptions
    nakeds = {
        "face": "%P face is weathered but kind, with laugh lines around %p eyes.",
        "chest": "%P chest is broad and muscled from years of hard work.",
        "lhand": "%P left hand bears a distinctive scar across the knuckles.",
        "rhand": "%P right hand is calloused from weapon training.",
        "lfoot": "%P left foot has a small tattoo of a rose on the ankle.",
        "head": "%P head is crowned with thick, unruly hair.",
    }
    
    char.db.nakeds = nakeds
    
    print(f"Set up example naked descriptions for {char.name}:")
    for part, desc in nakeds.items():
        processed = char.process_pronoun_substitution(desc)
        print(f"- {part}: {processed}")

if __name__ == "__main__":
    create_example_clothing()
    setup_test_character()