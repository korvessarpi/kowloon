"""
Base settings that we'll inherit from (Arx-style game dir).
"""

import os  # ensure os is available for paths/env

# Pull in Evennia defaults first.
from evennia.settings_default import *  # noqa

# ---------------------------------------------------------------------------
# Color markup imports (Evennia 5)
# ---------------------------------------------------------------------------
# Evennia 5 moved/renamed parts of contrib; this import works on current docs.
# Fallback is kept for older trees just in case.
try:
    from evennia.contrib.base_systems.color_markups import color_markups  # Evennia 5
except Exception:  # older paths fallback
    from evennia.contrib.base_systems.color_markups import (  # type: ignore
        color_markups,
    )

# If you previously did "+ color_markups.MUX..." etc, keep using explicit assignments.
COLOR_ANSI_EXTRA_MAP = (
    color_markups.CURLY_COLOR_ANSI_EXTRA_MAP
    + color_markups.MUX_COLOR_ANSI_EXTRA_MAP
)
COLOR_XTERM256_EXTRA_FG = (
    color_markups.CURLY_COLOR_XTERM256_EXTRA_FG
    + color_markups.MUX_COLOR_XTERM256_EXTRA_FG
)
COLOR_XTERM256_EXTRA_BG = (
    color_markups.CURLY_COLOR_XTERM256_EXTRA_BG
    + color_markups.MUX_COLOR_XTERM256_EXTRA_BG
)
COLOR_XTERM256_EXTRA_GFG = (
    color_markups.CURLY_COLOR_XTERM256_EXTRA_GFG
    + color_markups.MUX_COLOR_XTERM256_EXTRA_GFG
)
COLOR_XTERM256_EXTRA_GBG = (
    color_markups.CURLY_COLOR_XTERM256_EXTRA_GBG
    + color_markups.MUX_COLOR_XTERM256_EXTRA_GBG
)
COLOR_ANSI_XTERM256_BRIGHT_BG_EXTRA_MAP = (
    color_markups.CURLY_COLOR_ANSI_XTERM256_BRIGHT_BG_EXTRA_MAP
    + color_markups.MUX_COLOR_ANSI_XTERM256_BRIGHT_BG_EXTRA_MAP
)

# ---------------------------------------------------------------------------
# Permissions / channels / paths
# ---------------------------------------------------------------------------

PERMISSION_HIERARCHY = [
    "Guest",  # only used if GUEST_ENABLED=True
    "Player",
    "Helper",
    "Builders",
    "Builder",
    "Wizards",
    "Wizard",
    "Admin",
    "Immortals",
    "Immortal",
    "Developer",
    "Owner",
]

# Required channel names used below
PUBLIC_CHANNEL_NAME = "Public"
GUEST_CHANNEL_NAME = "Guest"
STAFF_INFO_CHANNEL_NAME = "staffinfo"
PLAYER_HELPER_CHANNEL_NAME = "Guides"

# ---------------------------------------------------------------------------
# Core typeclasses and command classes
# ---------------------------------------------------------------------------

BASE_ROOM_TYPECLASS = "typeclasses.rooms.ArxRoom"
BASE_SCRIPT_TYPECLASS = "typeclasses.scripts.scripts.Script"
BASE_GUEST_TYPECLASS = "typeclasses.guest.Guest"

# Place new connections/objects here if not otherwise specified (set to your room dbref)
# DEFAULT_HOME = "#13"

MULTISESSION_MODE = 1
COMMAND_DEFAULT_MSG_ALL_SESSIONS = True

# Accept leading "/" or " " as default arg start
COMMAND_DEFAULT_ARG_REGEX = r"^[ /]+.*$|$"

# Insert a few extra handy ANSI mappings
ADDITIONAL_ANSI_MAPPINGS = [
    (r"%r", "\r\n"),
]

LOCKWARNING_LOG_FILE = ""

# ---------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------

DEFAULT_CHANNELS = [
    {
        "key": PUBLIC_CHANNEL_NAME,
        "aliases": "pub",
        "desc": "Public discussion",
        "locks": "control: perm(Wizards);listen:all();send:all()",
    },
    {
        "key": "MUDinfo",
        "aliases": "",
        "desc": "Connection log",
        "locks": "control:perm(Immortals);listen:perm(Wizards);send:false()",
    },
    {
        "key": GUEST_CHANNEL_NAME,
        "aliases": "",
        "desc": "Guest channel",
        "locks": "control:perm(Immortals);listen:all();send:all()",
    },
    {
        "key": "Staff",
        "aliases": "",
        "desc": "Staff channel",
        "locks": "control:perm(Immortals);listen:perm(Builder);send:perm(Builder)",
    },
    {
        "key": STAFF_INFO_CHANNEL_NAME,
        "aliases": "",
        "desc": "Messages for staff",
        "locks": "control:perm(Immortals);listen:perm(Builder);send:perm(Builder)",
    },
    {
        "key": PLAYER_HELPER_CHANNEL_NAME,
        "aliases": "",
        "desc": "Channel for player volunteers",
        "locks": "control:perm(Immortals);listen:perm(helper);send:perm(helper)",
    },
]

# ---------------------------------------------------------------------------
# Database (SQLite by default)
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        # Use SQLite unless you switch to Postgres/MySQL in production_settings.py
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(GAME_DIR, "server", "evennia.db3"),
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
        "OPTIONS": {"timeout": 25},
    }
}

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "web.character.context_processors.consts"
]
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# ---------------------------------------------------------------------------
# Installed apps (Arx additions)
# ---------------------------------------------------------------------------

INSTALLED_APPS += (
    "world.dominion",
    "world.msgs",
    "world.conditions.apps.ConditionsConfig",
    "world.fashion.apps.FashionConfig",
    "world.petitions.apps.PetitionsConfig",
    "web.character",
    "web.news",
    "web.helpdesk",
    "web.help_topics",
    "cloudinary",
    "django.contrib.humanize",
    "bootstrapform",
    "crispy_forms",
    "world.weather",
    "world.templates.apps.TemplateConfig",
    "world.exploration",
    "web.admintools",
    "world.magic",
    "world.quests.apps.QuestsConfig",
    "world.stat_checks.apps.StatChecksConfig",
    "world.prayer.apps.PrayerConfig",
    "world.traits.apps.TraitsConfig",
    "evennia_extensions.object_extensions.apps.ObjectExtensionsConfig",
    "world.game_constants.apps.GameConstantsConfig",
    "world.crafting.apps.CraftingConfig",
    "evennia_extensions.character_extensions.apps.CharacterExtensionsConfig",
    "evennia_extensions.room_extensions.apps.RoomExtensionsConfig",
)

CRISPY_TEMPLATE_PACK = "bootstrap3"
DATA_UPLOAD_MAX_NUMBER_FIELDS = 3000

# ---------------------------------------------------------------------------
# Game time / magic / helpdesk (left mostly as-is)
# ---------------------------------------------------------------------------

MAGIC_CONDITION_MODULES = ("world.magic.conditionals",)

# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------

BATTLE_LOG = os.path.join(LOG_DIR, "battle.log")
DOMINION_LOG = os.path.join(LOG_DIR, "dominion.log")
LOG_FORMAT = "%(asctime)s: %(message)s"
DATE_FORMAT = "%m/%d/%Y %I:%M:%S"

# ---------------------------------------------------------------------------
# Admin/Email defaults (prevent NameError; configurable via env or prod settings)
# ---------------------------------------------------------------------------
ADMIN_NAME = os.getenv("ADMIN_NAME", "")  # e.g. "Game Admin"
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")  # e.g. "admin@example.com"
SEND_ADMIN_EMAILS = os.getenv("SEND_ADMIN_EMAILS", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# ---------------------------------------------------------------------------
# Email / Cloudinary (keys live in production_settings.py or env)
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"

# Admin emails (disabled unless all present)
if ADMIN_NAME and ADMIN_EMAIL and SEND_ADMIN_EMAILS:
    ADMINS = [(ADMIN_NAME, ADMIN_EMAIL)]
else:
    ADMINS = []
MANAGERS = ADMINS

# ---------------------------------------------------------------------------
# Auth / Middleware
# ---------------------------------------------------------------------------

# Evennia’s default password validators can be strict with legacy data
AUTH_PASSWORD_VALIDATORS = []

# Keep middleware lean; XViewMiddleware is tied to admindocs and not needed here.
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    "web.middleware.auth.SharedLoginMiddleware",
]

