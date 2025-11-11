# Nakeds System for Kowloon MUD

This system allows players to set detailed descriptions for specific body parts that appear when someone looks at them. These descriptions can be covered by clothing.

## Player Commands

### @nakeds
- `@nakeds` - List all your naked descriptions  
- `@naked <bodypart> is <description>` - Set description for a body part
- `@naked <bodypart>` - View description for a specific body part  
- `@naked/del <bodypart>` - Delete description for a body part
- `@naked/list` - Show all available body parts

### Available Body Parts
- **Eyes**: leye, reye (left eye, right eye)
- **Ears**: lear, rear (left ear, right ear)  
- **Head/Face**: head, face, neck
- **Arms**: lshoulder, rshoulder, larm, rarm, lhand, rhand
- **Torso**: chest, back, abdomen, groin
- **Legs**: lthigh, rthigh, lshin, rshin, lfoot, rfoot

## Staff Commands (Builders+)

### @coverage
Set which body parts are covered by clothing/armor:
- `@coverage <item>` - View current coverage for an item
- `@coverage <item>=<bodypart>,<bodypart>,...` - Set coverage for an item  
- `@coverage/del <item>` - Remove all coverage from an item

### @nakeds (Admin version)
Manage naked descriptions for any character:
- `@nakeds <character>` - View all nakeds for a character
- `@nakeds <character>/<bodypart>` - View specific bodypart for character
- `@nakeds/del <character>/<bodypart>` - Delete a naked description
- `@nakeds/clear <character>` - Clear all naked descriptions

## How It Works

1. **Player sets naked descriptions**: Players use `@naked <bodypart> is <description>` to describe body parts
2. **Descriptions appear when looked at**: When someone looks at the character, visible naked descriptions are shown from head to toe
3. **Clothing covers parts**: When wearing items with coverage, those body parts become hidden
4. **Pronoun substitution**: Use %P (Her/His/Their), %p (her/his/their), %s (she/he/they), %o (her/him/them) in descriptions

## Examples

### Setting Descriptions
```
@naked face is %P face is weathered but kind, with laugh lines around %p eyes.
@naked chest is %P chest is broad and muscled from years of training.  
@naked lhand is %P left hand bears a distinctive scar across the knuckles.
```

### Setting Coverage (Staff)
```
@coverage shirt=chest,abdomen,back
@coverage helmet=head,face  
@coverage gloves=lhand,rhand
@coverage pants=groin,lthigh,rthigh
```

### Result
When someone looks at a character:
- If naked: All descriptions show from head to toe
- If wearing shirt: chest, abdomen, back descriptions are hidden
- If wearing gloves: lhand, rhand descriptions are hidden
- Uncovered parts still show their descriptions

## Design Notes

- **Main @describe should be light**: Basic info like height, build, obvious features
- **@nakeds for details**: Specific body part details that can be covered
- **Don't tell people how to feel**: Describe what they see, let them decide how to react
- **Use pronoun substitution**: So descriptions adapt to gender changes
- **Coverage is additive**: Multiple items can cover the same parts

## Integration

The system integrates with:
- **Character appearance**: Naked descriptions appear in `look <character>`
- **Clothing system**: Uses existing wearable slot system
- **Pronoun system**: Works with gender and appearance commands
- **Tailoring system**: Ready for future clothing coverage features