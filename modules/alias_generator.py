"""
Alias Generator Module
Produces a set of plausible username permutations from a person's full name.
"""

import itertools


def generate_aliases(name):
    """
    Generate username aliases from a full name.

    Args:
        name (str): Full name, e.g. "John Smith".

    Returns:
        list[str]: De-duplicated list of alias strings.
    """
    if not name or not name.strip():
        return []

    parts = name.strip().lower().split()
    if len(parts) == 0:
        return []

    aliases = set()

    if len(parts) == 1:
        # Single name — limited permutations
        word = parts[0]
        aliases.update([
            word,
            f"{word}1",
            f"{word}123",
            f"{word}_",
            f"_{word}",
            f"the{word}",
            f"{word}official",
        ])
        return sorted(aliases)

    first = parts[0]
    last = parts[-1]
    middle_parts = parts[1:-1] if len(parts) > 2 else []
    fi = first[0]   # first initial
    li = last[0]    # last initial

    # ── Core permutations ──────────────────────────────────
    aliases.update([
        # No separator
        f"{first}{last}",
        f"{last}{first}",
        # Dot separator
        f"{first}.{last}",
        f"{last}.{first}",
        # Underscore separator
        f"{first}_{last}",
        f"{last}_{first}",
        # Hyphen separator
        f"{first}-{last}",
        f"{last}-{first}",
        # Initials
        f"{fi}{last}",
        f"{first}{li}",
        f"{fi}.{last}",
        f"{first}.{li}",
        f"{fi}_{last}",
        f"{fi}{li}",
        f"{last}{fi}",
        # Common numeric suffixes
        f"{first}{last}1",
        f"{first}{last}123",
        f"{first}{last}01",
        f"{first}{last}99",
        f"{first}_{last}90",
        f"{fi}{last}1",
    ])

    # ── Middle name permutations ───────────────────────────
    if middle_parts:
        mi = middle_parts[0][0]
        middle = middle_parts[0]
        aliases.update([
            f"{first}{mi}{last}",
            f"{first}.{mi}.{last}",
            f"{first}_{mi}_{last}",
            f"{fi}{mi}{li}",
            f"{first}{middle}{last}",
        ])

    return sorted(aliases)
