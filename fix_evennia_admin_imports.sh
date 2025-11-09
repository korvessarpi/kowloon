#!/usr/bin/env bash
set -euo pipefail

# Run from the project root (must contain web/, world/, evennia_extensions/)
for d in web world evennia_extensions; do
  [[ -d "$d" ]] || { echo "Run from your project root (needs web/, world/, evennia_extensions/)."; exit 1; }
done

echo "🔎 Updating Evennia admin import paths ..."

# 1) TagInline → evennia.web.admin.tags
grep -RIl --include="*.py" "from evennia.typeclasses.admin import TagInline" web world evennia_extensions \
  | while read -r f; do
      sed -i.bak 's|from evennia\.typeclasses\.admin import TagInline|from evennia.web.admin.tags import TagInline|' "$f"
      echo "   • $f : TagInline → evennia.web.admin.tags"
    done

# 2) AttributeInline → evennia.web.admin.attributes
grep -RIl --include="*.py" "from evennia.typeclasses.admin import AttributeInline" web world evennia_extensions \
  | while read -r f; do
      sed -i.bak 's|from evennia\.typeclasses\.admin import AttributeInline|from evennia.web.admin.attributes import AttributeInline|' "$f"
      echo "   • $f : AttributeInline → evennia.web.admin.attributes"
    done

# 3) Combined imports on one line
grep -RIl --include="*.py" "from evennia.typeclasses.admin import TagInline, AttributeInline" web world evennia_extensions \
  | while read -r f; do
      cp "$f" "$f.bak"
      awk '
        {
          gsub("from evennia.typeclasses.admin import TagInline, AttributeInline",
               "from evennia.web.admin.tags import TagInline\nfrom evennia.web.admin.attributes import AttributeInline");
          print
        }
      ' "$f.bak" > "$f"
      echo "   • $f : split TagInline/AttributeInline into correct imports"
    done

# 4) Help admin module moved: evennia.help.admin → evennia.web.admin.help
grep -RIl --include="*.py" "from evennia.help.admin import" web world evennia_extensions \
  | while read -r f; do
      sed -i.bak 's|from evennia\.help\.admin import |from evennia.web.admin.help import |' "$f"
      echo "   • $f : evennia.help.admin → evennia.web.admin.help"
    done

echo "✅ Done. Backups saved as *.bak next to edited files."

