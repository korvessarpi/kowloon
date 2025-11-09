# evennia_extensions/object_extensions/admin.py

from django.contrib import admin

# --- Try to import Evennia's ObjectDB model from likely locations ---
ObjectDB = None
try:
    from evennia.objects.models import ObjectDB as _ObjectDB  # newer/common path
    ObjectDB = _ObjectDB
except Exception:
    try:
        from evennia.typeclasses.models import ObjectDB as _ObjectDB  # older path
        ObjectDB = _ObjectDB
    except Exception:
        ObjectDB = None  # Fallback: no ObjectDB available; we'll skip registering it

# --- Try to import Evennia's ObjectDBAdmin; fall back to a minimal ModelAdmin ---
_base_admin_cls = admin.ModelAdmin
try:
    from evennia.objects.admin import ObjectDBAdmin as _ObjectDBAdmin
    _base_admin_cls = _ObjectDBAdmin
except Exception:
    # Evennia moved/removed admin internals; we'll extend a minimal admin instead.
    _base_admin_cls = admin.ModelAdmin

# --- Your project models/inlines ---
from evennia_extensions.object_extensions.models import (
    Dimensions,
    Permanence,
    DisplayNames,
    Descriptions,
)
from evennia_extensions.character_extensions.models import (
    CharacterSheet,
    CharacterMessengerSettings,
    CharacterCombatSettings,
    CharacterTitle,
    HeldKey,
)
from evennia_extensions.room_extensions.models import RoomDescriptions, RoomDetail

from web.character.models import Clue
from world.traits.models import CharacterTraitValue, Trait
from world.crafting.models import (
    CraftingRecord,
    AdornedMaterial,
    TranslatedDescription,
    WeaponOverride,
    ArmorOverride,
    PlaceSpotsOverride,
    MaskedDescription,
)

# -------------------------
# Inline/admin definitions
# -------------------------

class DimensionsAdmin(admin.ModelAdmin):
    list_display = ("pk", "size", "weight", "capacity", "quantity")
    search_fields = ("pk", "objectdb__db_key")
    raw_id_fields = ("objectdb",)


class PermanenceAdmin(admin.ModelAdmin):
    list_display = ("pk", "put_time", "deleted_time")
    search_fields = ("pk", "objectdb__db_key")
    raw_id_fields = ("objectdb", "pre_offgrid_location")


class SecretsInline(admin.StackedInline):
    model = Clue
    extra = 0
    raw_id_fields = ("tangible_object", "author")
    filter_horizontal = ("search_tags",)
    show_change_link = True


class CharacterTraitValueInline(admin.TabularInline):
    model = CharacterTraitValue
    extra = 0
    ordering = ("trait__trait_type", "trait__name")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "trait":
            kwargs["queryset"] = Trait.objects.order_by("name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CharacterSheetInline(admin.StackedInline):
    model = CharacterSheet
    extra = 0


class CharacterCombatSettingsInline(admin.StackedInline):
    model = CharacterCombatSettings
    extra = 0
    fk_name = "objectdb"
    raw_id_fields = ("guarding", "objectdb")


class CharacterMessengerSettingsInline(admin.StackedInline):
    model = CharacterMessengerSettings
    extra = 0
    fk_name = "objectdb"
    raw_id_fields = ("custom_messenger", "discreet_messenger", "objectdb")


class CharacterTitlesInline(admin.TabularInline):
    model = CharacterTitle
    extra = 0
    raw_id_fields = ("character",)


class CharacterHeldKeysInline(admin.TabularInline):
    model = HeldKey
    extra = 0
    raw_id_fields = ("character", "keyed_object")
    fk_name = "character"


class KeyedCharactersInline(CharacterHeldKeysInline):
    fk_name = "keyed_object"


class RoomDescriptionsInline(admin.TabularInline):
    model = RoomDescriptions
    extra = 0
    raw_id_fields = ("room", "mood_set_by")
    fk_name = "room"


class PermanenceInline(admin.TabularInline):
    model = Permanence
    extra = 0
    fk_name = "objectdb"
    raw_id_fields = ("objectdb", "pre_offgrid_location")


class DimensionsInline(admin.TabularInline):
    model = Dimensions
    extra = 0
    raw_id_fields = ("objectdb",)


class CraftingRecordInline(admin.TabularInline):
    model = CraftingRecord
    extra = 0
    raw_id_fields = ("crafted_by", "recipe", "objectdb")
    fk_name = "objectdb"


class TranslatedDescriptionInline(admin.StackedInline):
    model = TranslatedDescription
    extra = 0
    raw_id_fields = ("objectdb",)


class AdornedMaterialInline(admin.StackedInline):
    model = AdornedMaterial
    extra = 0
    raw_id_fields = ("type", "objectdb")


class MaskedDescriptionInline(admin.TabularInline):
    model = MaskedDescription
    extra = 0
    raw_id_fields = ("objectdb",)


class PlaceSpotsOverrideInline(admin.TabularInline):
    model = PlaceSpotsOverride
    extra = 0
    raw_id_fields = ("objectdb",)


class ArmorOverrideInline(admin.TabularInline):
    model = ArmorOverride
    extra = 0
    raw_id_fields = ("objectdb",)


class WeaponOverrideInline(admin.TabularInline):
    model = WeaponOverride
    extra = 0
    raw_id_fields = ("objectdb",)


class DisplayNamesInline(admin.TabularInline):
    model = DisplayNames
    extra = 0


class DescriptionsInline(admin.TabularInline):
    model = Descriptions
    extra = 0


class RoomDetailInline(admin.TabularInline):
    model = RoomDetail
    extra = 0
    raw_id_fields = ("room",)


# -------------------------
# ObjectDB admin
# -------------------------

class ArxObjectDBAdmin(_base_admin_cls):
    """
    Extend Evennia's ObjectDBAdmin when available; otherwise inherit from ModelAdmin.
    We only rely on very stable pieces (id/str) and compose inlines dynamically.
    """
    search_fields = ["=id", "db_key"]

    # Start from the base class' inlines (if any), then append local inlines.
    base_inlines = getattr(_base_admin_cls, "inlines", []) or []
    inlines = list(base_inlines) + [
        DisplayNamesInline,
        DescriptionsInline,
        DimensionsInline,
        PermanenceInline,
        SecretsInline,
    ]

    character_inlines = [
        CharacterTraitValueInline,
        CharacterSheetInline,
        CharacterMessengerSettingsInline,
        CharacterCombatSettingsInline,
        CharacterHeldKeysInline,
    ]
    crafted_inlines = [
        CraftingRecordInline,
        AdornedMaterialInline,
        TranslatedDescriptionInline,
    ]
    mask_inlines = [MaskedDescriptionInline]
    place_inlines = [PlaceSpotsOverrideInline]
    wearable_inlines = [ArmorOverrideInline]
    wieldable_inlines = [WeaponOverrideInline]
    container_inlines = [KeyedCharactersInline]
    room_inlines = [RoomDescriptionsInline, KeyedCharactersInline, RoomDetailInline]

    def get_inline_instances(self, request, obj=None):
        """
        Add inlines dynamically based on the object's actual typeclasses.
        Import typeclasses lazily and defensively so missing modules don't crash admin.
        """
        # Lazy, defensive imports
        Character = CraftedObject = Mask = Place = Wearable = Wieldable = Container = ArxRoom = None
        try:
            from typeclasses.characters import Character as _Character
            Character = _Character
        except Exception:
            pass
        try:
            from typeclasses.objects import Object as _CraftedObject
            CraftedObject = _CraftedObject
        except Exception:
            pass
        try:
            from typeclasses.disguises.disguises import Mask as _Mask
            Mask = _Mask
        except Exception:
            pass
        try:
            from typeclasses.places.places import Place as _Place
            Place = _Place
        except Exception:
            pass
        try:
            from typeclasses.wearable.wearable import Wearable as _Wearable
            Wearable = _Wearable
        except Exception:
            pass
        try:
            from typeclasses.wearable.wieldable import Wieldable as _Wieldable
            Wieldable = _Wieldable
        except Exception:
            pass
        try:
            from typeclasses.containers.container import Container as _Container
            Container = _Container
        except Exception:
            pass
        try:
            from typeclasses.rooms import ArxRoom as _ArxRoom
            ArxRoom = _ArxRoom
        except Exception:
            pass

        def _isinstance_safe(o, cls):
            return cls is not None and isinstance(o, cls)

        if obj:
            final_inlines = list(self.inlines)
            if _isinstance_safe(obj, Character):
                final_inlines += self.character_inlines
            if _isinstance_safe(obj, CraftedObject):
                final_inlines += self.crafted_inlines
            if _isinstance_safe(obj, Mask):
                final_inlines += self.mask_inlines
            if _isinstance_safe(obj, Place):
                final_inlines += self.place_inlines
            if _isinstance_safe(obj, Wearable):
                final_inlines += self.wearable_inlines
            if _isinstance_safe(obj, Wieldable):
                final_inlines += self.wieldable_inlines
            if _isinstance_safe(obj, Container):
                final_inlines += self.container_inlines
            if _isinstance_safe(obj, ArxRoom):
                final_inlines += self.room_inlines
            return [inline(self.model, self.admin_site) for inline in final_inlines]
        return []

# -------------------------
# Registration
# -------------------------

admin.site.register(Dimensions, DimensionsAdmin)
admin.site.register(Permanence, PermanenceAdmin)

if ObjectDB:
    # If Django already registered ObjectDB (e.g., by Evennia), try to replace it.
    try:
        admin.site.unregister(ObjectDB)
    except Exception:
        pass
    try:
        admin.site.register(ObjectDB, ArxObjectDBAdmin)
    except Exception:
        # As a last resort, register with a minimal admin to avoid crashing admin discovery.
        class _MinimalObjectDBAdmin(admin.ModelAdmin):
            list_display = ("id", "__str__")
        try:
            admin.site.register(ObjectDB, _MinimalObjectDBAdmin)
        except Exception:
            # Final fallback: don't register ObjectDB at all.
            pass

