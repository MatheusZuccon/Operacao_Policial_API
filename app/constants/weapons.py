from typing import Final

PISTOL: Final[str] = "pistola"
RIFLE: Final[str] = "fuzil"
CARBINE: Final[str] = "carabina"
SHOTGUN: Final[str] = "espingarda"
SUBMACHINE_GUN: Final[str] = "submetralhadora"
SNIPER_RIFLE: Final[str] = "rifle de precisão"
REVOLVER: Final[str] = "revólver"
MACHINE_GUN: Final[str] = "metralhadora"

VALID_WEAPONS: Final[list[str]] = [
    PISTOL,
    RIFLE,
    CARBINE,
    SHOTGUN,
    SUBMACHINE_GUN,
    SNIPER_RIFLE,
    REVOLVER,
    MACHINE_GUN,
]

# Only pistol is allowed for investigative operations
INVESTIGATIVE_ALLOWED_WEAPONS: Final[list[str]] = [PISTOL]
