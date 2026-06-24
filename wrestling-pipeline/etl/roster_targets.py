from __future__ import annotations

import os
from pathlib import Path

try:
    from .name_utils import slugify_name
except ImportError:
    from name_utils import slugify_name


CURATED_ROSTER = [
    "Stone Cold Steve Austin",
    "The Rock",
    "Hulk Hogan",
    "The Undertaker",
    "John Cena",
    "Shawn Michaels",
    "Bret Hart",
    "Triple H",
    "Randy Savage",
    "Ric Flair",
    "Andre the Giant",
    "Randy Orton",
    "Kurt Angle",
    "Rey Mysterio",
    "Roman Reigns",
    "Eddie Guerrero",
    "Brock Lesnar",
    "Mick Foley",
    "Chris Jericho",
    "Edge",
    "CM Punk",
    "Daniel Bryan",
    "Bruno Sammartino",
    "Roddy Piper",
    "Ultimate Warrior",
    "Batista",
    "Seth Rollins",
    "Jeff Hardy",
    "Kane",
    "Becky Lynch",
    "Charlotte Flair",
    "Trish Stratus",
    "Lita",
    "Chyna",
    "Booker T",
    "Big Show",
    "Kevin Nash",
    "Yokozuna",
    "Razor Ramon",
    "Mr. Perfect",
    "Owen Hart",
    "Jake Roberts",
    "Superstar Billy Graham",
    "Ricky Steamboat",
    "Sgt. Slaughter",
    "Ted DiBiase",
    "Rob Van Dam",
    "AJ Styles",
    "Jimmy Snuka",
    "Kevin Owens",
    "Buddy Rogers",
    "Ivan Koloff",
    "Pedro Morales",
    "Stan Stasiak",
    "Bob Backlund",
    "Cody Rhodes",
    "The Iron Sheik",
]

ROSTER_ALIASES = {
    "stone cold steve austin": {"steve austin", '"stone cold" steve austin'},
    "bret hart": {'bret "the hitman" hart'},
    "randy savage": {'randy "macho man" savage', "macho man randy savage"},
    "andre the giant": {"andré the giant", "andre the giant", "andre the giant "},
    "roddy piper": {'"rowdy" roddy piper', "rowdy roddy piper"},
    "ultimate warrior": {"warrior"},
    "booker t": {"booker t."},
    "kevin nash": {"diesel"},
    "razor ramon": {"scott hall"},
    "daniel bryan": {"bryan danielson"},
    "mr perfect": {"curt hennig"},
    "jake roberts": {'jake "the snake" roberts'},
    "superstar billy graham": {'"superstar" billy graham', "billy graham"},
    "ricky steamboat": {'ricky "the dragon" steamboat'},
    "jimmy snuka": {'jimmy "superfly" snuka', "superfly snuka"},
    "big show": {"the big show", "paul wight"},
    "mick foley": {"mankind", "cactus jack", "dude love"},
    "the rock": {"dwayne johnson"},
    "aj styles": {"a j styles"},
}

BLACKLISTED_SLUGS = {
    "kevin theophile catherine",
    "andre andre",
}


def _default_target_file() -> str:
    return str(Path(__file__).resolve().parent / "target_wrestlers.txt")


def load_target_slugs(target_file: str | None = None) -> set[str]:
    names: list[str] = []
    path = target_file or _default_target_file()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            names.extend(line.strip() for line in handle if line.strip())
    if not names:
        names.extend(CURATED_ROSTER)

    slugs = {slugify_name(name) for name in names if slugify_name(name)}
    expanded = set(slugs)
    for canonical_slug, aliases in ROSTER_ALIASES.items():
        if canonical_slug in slugs:
            expanded.add(canonical_slug)
            expanded.update(slugify_name(alias) for alias in aliases if slugify_name(alias))
    expanded.difference_update(BLACKLISTED_SLUGS)
    return expanded


def is_target_name(value, target_slugs: set[str] | None = None) -> bool:
    slug = slugify_name(value)
    if not slug or slug in BLACKLISTED_SLUGS:
        return False
    return slug in (target_slugs or load_target_slugs())
