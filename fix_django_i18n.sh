#!/usr/bin/env bash
set -euo pipefail

# Run from the project root (folder that contains web/ world/ evennia_extensions/)
ROOT_CHECK_OK=0
for d in web world evennia_extensions; do
  [[ -d "$d" ]] || ROOT_CHECK_OK=1
done
if [[ "$ROOT_CHECK_OK" -ne 0 ]]; then
  echo "⚠️  Please run this script from your project root (where web/, world/, evennia_extensions/ exist)."
  exit 1
fi

echo "🔎 Scanning for translation imports..."

# Helper: replace an exact import line with a multi-line try/except block (idempotent-ish).
replace_import_line() {
  local pattern="$1"
  local replacement="$2"
  # Only run sed if the pattern exists
  if grep -RIl --include="*.py" "$pattern" web world evennia_extensions >/dev/null 2>&1; then
    echo "🛠  Replacing: $pattern"
    # Use | as sed delimiter to avoid escaping slashes.
    grep -RIl --include="*.py" "$pattern" web world evennia_extensions \
      | while read -r file; do
          # Skip files already converted (simple guard)
          if grep -q "from django.utils.translation import gettext" "$file"; then
            # Might already be converted; still apply sed to catch exact line.
            true
          fi
          sed -i.bak "s|^$pattern\$|$replacement|" "$file"
          echo "   - updated $file"
        done
  fi
}

# 1) from django.utils.translation import ugettext as _
replace_import_line \
  "from django.utils.translation import ugettext as _" \
  $'try:\n    from django.utils.translation import gettext as _\nexcept ImportError:\n    from django.utils.translation import ugettext as _  # type: ignore'

# 2) from django.utils.translation import ugettext_lazy as _
replace_import_line \
  "from django.utils.translation import ugettext_lazy as _" \
  $'try:\n    from django.utils.translation import gettext_lazy as _\nexcept ImportError:\n    from django.utils.translation import ugettext_lazy as _  # type: ignore'

# 3) from django.utils.translation import ugettext_lazy as _, ugettext
replace_import_line \
  "from django.utils.translation import ugettext_lazy as _, ugettext" \
  $'try:\n    from django.utils.translation import gettext_lazy as _, gettext as ugettext\nexcept ImportError:\n    from django.utils.translation import ugettext_lazy as _, ugettext  # type: ignore'

# 4) Rare: from django.utils.translation import ugettext (no alias)
replace_import_line \
  "from django.utils.translation import ugettext" \
  $'try:\n    from django.utils.translation import gettext as ugettext\nexcept ImportError:\n    from django.utils.translation import ugettext as ugettext  # type: ignore'

# 5) Ensure models-specific direct calls keep working without changing code:
# If files call ugettext("...") but don't import ugettext explicitly, we won't
# guess imports here. The shim above (case 3 or 4) keeps the ugettext name alive.
# If you WANT to convert callsites, uncomment the two blocks below.

# --- OPTIONAL: Convert function calls ugettext(...) -> gettext(...) ---
# echo "🔁 (optional) Converting ugettext(…) calls to gettext(…) calls"
# grep -RIl --include="*.py" "ugettext(" web world evennia_extensions \
#   | while read -r file; do
#       sed -i.bak 's/ugettext(/gettext(/g' "$file"
#       # Ensure 'from django.utils.translation import gettext' is present if needed:
#       if ! grep -Eq '^from django\.utils\.translation import .*gettext' "$file"; then
#         # Add an import line near the top if the file imports translation utils at all
#         if grep -Eq '^from django\.utils\.translation import' "$file"; then
#           sed -i.bak '1,20{/^from django\.utils\.translation import/!b; a from django.utils.translation import gettext
# }' "$file"
#         fi
#       fi
#       echo "   - updated $file"
#     done

echo "✅ Done. Backups *.bak were created next to modified files."
echo "🔁 You can review changes with: git status && git diff"
echo "🚀 Next: re-run your command: evennia migrate --settings=production_settings"

