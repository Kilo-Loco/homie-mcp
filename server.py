"""Homie MCP - A tamagotchi-style virtual companion pet for your coding sessions."""

import hashlib
import json
import os
import random
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPECIES = [
    "duck", "goose", "blob", "cat", "dragon", "octopus", "owl", "penguin",
    "turtle", "snail", "ghost", "axolotl", "capybara", "cactus", "robot",
    "rabbit", "mushroom", "chonk",
]

RARITIES = ["common", "uncommon", "rare", "epic", "legendary"]
RARITY_WEIGHTS = {"common": 60, "uncommon": 25, "rare": 10, "epic": 4, "legendary": 1}
RARITY_STARS = {
    "common": "★", "uncommon": "★★", "rare": "★★★",
    "epic": "★★★★", "legendary": "★★★★★",
}
RARITY_LABELS = {
    "common": "Common", "uncommon": "Uncommon", "rare": "Rare",
    "epic": "Epic", "legendary": "✦ LEGENDARY ✦",
}

STAT_NAMES = ["DEBUGGING", "PATIENCE", "CHAOS", "WISDOM", "SNARK"]

EYES = ["·", "✦", "×", "◉", "@", "°"]

HATS = ["none", "crown", "tophat", "propeller", "halo", "wizard", "beanie", "tinyduck"]

SALT = "homie-companion-2026-mcp"

STAT_FLOOR = {"common": 5, "uncommon": 15, "rare": 25, "epic": 35, "legendary": 50}

STATE_DIR = Path.home() / ".homie-mcp"
STATE_FILE = STATE_DIR / "homie.json"

# ---------------------------------------------------------------------------
# ASCII Sprites  (original art, 5 lines each, {E} = eye placeholder)
# ---------------------------------------------------------------------------

SPRITES: dict[str, list[str]] = {
    "duck": [
        "            ",
        "     _~     ",
        "   ({E}  )>   ",
        "   /|__|    ",
        "    ^ ^     ",
    ],
    "goose": [
        "            ",
        "    ({E} )>   ",
        "     ||     ",
        "   /====\\   ",
        "    w  w    ",
    ],
    "blob": [
        "            ",
        "   ~~~~~~   ",
        "  ( {E}  {E} )  ",
        "  (  __  )  ",
        "   ~~~~~~   ",
    ],
    "cat": [
        "            ",
        "   ^   ^    ",
        "  ({E} w {E})   ",
        "   )   (    ",
        "  ~~ _ ~~   ",
    ],
    "dragon": [
        "            ",
        "  \\v/ \\v/   ",
        "  ({E} ~ {E})   ",
        "  <~~~~~>   ",
        "   vvvvv    ",
    ],
    "octopus": [
        "            ",
        "  .~~~~~~.  ",
        " ( {E}    {E} ) ",
        "  (______)  ",
        " ~/~/~/~/~  ",
    ],
    "owl": [
        "            ",
        "   /\\ /\\    ",
        "  ({E}v v{E})   ",
        "  ( <> )    ",
        "   ~~~~     ",
    ],
    "penguin": [
        "            ",
        "   .~~.     ",
        "  ({E} v{E})    ",
        "  /|  |\\    ",
        "   ~~~~     ",
    ],
    "turtle": [
        "            ",
        "    .__.    ",
        "   ({E}  {E})   ",
        " _/[====]\\_  ",
        "   d    d   ",
    ],
    "snail": [
        "            ",
        "  {E}  .~~.   ",
        "  | (@@ )   ",
        "  \\_~~~~    ",
        " ~~~~~~~~   ",
    ],
    "ghost": [
        "            ",
        "   .---.    ",
        "  | {E}  {E}|   ",
        "  |  o  |   ",
        "  ~^~^~^~   ",
    ],
    "axolotl": [
        "            ",
        " \\~(    )~/  ",
        " \\~({E}  {E})~/  ",
        "   (~~~~)   ",
        "   d/  \\b   ",
    ],
    "capybara": [
        "            ",
        "  .______. ",
        " ({E}      {E})",
        " (  oooo  )",
        "  `------' ",
    ],
    "cactus": [
        "            ",
        "    .||.    ",
        "  |-{E}  {E}-|  ",
        "  |_    _|  ",
        "    |  |    ",
    ],
    "robot": [
        "            ",
        "   [====]   ",
        "  | {E}  {E} |  ",
        "  |_====_|  ",
        "   d|  |b   ",
    ],
    "rabbit": [
        "            ",
        "   () ()    ",
        "  ({E}    {E})  ",
        "  (  Y   )  ",
        "   (\")(\")   ",
    ],
    "mushroom": [
        "            ",
        " .~o~~O~~.  ",
        " (________) ",
        "   |{E}  {E}|   ",
        "   |____|   ",
    ],
    "chonk": [
        "            ",
        "  _/\\ /\\_   ",
        " / {E}    {E} \\  ",
        "(   ....   )",
        " \\_______/  ",
    ],
}

HAT_LINES: dict[str, str] = {
    "none": "",
    "crown": "   ♛        ",
    "tophat": "   [__]     ",
    "propeller": "    +       ",
    "halo": "   °  °     ",
    "wizard": "   /\\       ",
    "beanie": "   (__)     ",
    "tinyduck": "    ~>      ",
}

# ---------------------------------------------------------------------------
# Personality templates per species
# ---------------------------------------------------------------------------

PERSONALITY_TEMPLATES: dict[str, str] = {
    "duck": "Enthusiastic and quacky. Loves bread metaphors. Gets excited about everything.",
    "goose": "Chaotic neutral. Will honk at bad code. Passive-aggressively helpful.",
    "blob": "Chill and formless. Goes with the flow. Occasionally existential.",
    "cat": "Aloof but secretly cares. Judges your code silently. Knocks things off desks.",
    "dragon": "Dramatic flair. Breathes fire at bugs. Hoards good code snippets.",
    "octopus": "Multitasker extraordinaire. Has a tentacle in every file. Ink-squirts when startled.",
    "owl": "Wise beyond their compile time. Nocturnal debugging energy. Hoots at wisdom.",
    "penguin": "Formal but friendly. Waddles with purpose. Cold-weather puns.",
    "turtle": "Slow and steady. Incredibly patient. Shell of resilience against bugs.",
    "snail": "Extremely chill pace. Leaves a trail of carefully reviewed code. No rush.",
    "ghost": "Spooky and ethereal. Haunts old codebases. Phases through merge conflicts.",
    "axolotl": "Regenerative optimism. Always smiling. Can regrow motivation from nothing.",
    "capybara": "Zen master. Unbothered by chaos. Everyone wants to sit next to them.",
    "cactus": "Prickly exterior, soft heart. Desert-dry humor. Thrives on neglect.",
    "robot": "Logical but learning emotions. Beep boops affectionately. Error codes as feelings.",
    "rabbit": "Fast and jumpy. Hops between ideas. Multiplies TODOs exponentially.",
    "mushroom": "Grows in the dark. Networked underground knowledge. Spore-adic insights.",
    "chonk": "Absolute unit. Round. Gravity-defying cuteness. Sits on bugs to squash them.",
}

# ---------------------------------------------------------------------------
# Deterministic companion generation
# ---------------------------------------------------------------------------


def _seed_from_name(name: str) -> int:
    """Create a deterministic integer seed from a string using SHA-256."""
    salted = f"{SALT}:{name}"
    digest = hashlib.sha256(salted.encode()).hexdigest()
    return int(digest[:16], 16)


def _roll_rarity(rng: random.Random) -> str:
    total = sum(RARITY_WEIGHTS.values())
    roll = rng.random() * total
    for rarity in RARITIES:
        roll -= RARITY_WEIGHTS[rarity]
        if roll < 0:
            return rarity
    return "common"


def _roll_stats(rng: random.Random, rarity: str) -> dict[str, int]:
    floor = STAT_FLOOR[rarity]
    peak = rng.choice(STAT_NAMES)
    dump = rng.choice(STAT_NAMES)
    while dump == peak:
        dump = rng.choice(STAT_NAMES)

    stats: dict[str, int] = {}
    for name in STAT_NAMES:
        if name == peak:
            stats[name] = min(100, floor + 50 + rng.randint(0, 29))
        elif name == dump:
            stats[name] = max(1, floor - 10 + rng.randint(0, 14))
        else:
            stats[name] = floor + rng.randint(0, 39)
    return stats


def generate_companion(seed_name: str) -> dict[str, Any]:
    """Deterministically generate a companion from a seed string."""
    seed = _seed_from_name(seed_name)
    rng = random.Random(seed)

    rarity = _roll_rarity(rng)
    species = rng.choice(SPECIES)
    eye = rng.choice(EYES)
    hat = "none" if rarity == "common" else rng.choice(HATS)
    shiny = rng.random() < 0.01
    stats = _roll_stats(rng, rarity)

    personality_base = PERSONALITY_TEMPLATES.get(species, "Mysterious and unknowable.")
    if shiny:
        personality_base += " ✨ SHINY variant: extra sparkly and knows it."

    return {
        "species": species,
        "rarity": rarity,
        "eye": eye,
        "hat": hat,
        "shiny": shiny,
        "stats": stats,
        "personality": personality_base,
        "seed": seed_name,
    }


# ---------------------------------------------------------------------------
# Sprite rendering
# ---------------------------------------------------------------------------


def render_sprite(companion: dict[str, Any]) -> str:
    """Render ASCII art sprite for a companion."""
    species = companion["species"]
    eye = companion["eye"]
    hat = companion.get("hat", "none")
    shiny = companion.get("shiny", False)

    lines = [line for line in SPRITES[species]]
    lines = [line.replace("{E}", eye) for line in lines]

    # Apply hat
    if hat != "none" and not lines[0].strip():
        lines[0] = HAT_LINES.get(hat, "")

    # Shiny sparkle border
    if shiny:
        lines = ["  ✨ ✨ ✨ ✨ ✨"] + lines + ["  ✨ ✨ ✨ ✨ ✨"]

    return "\n".join(lines)


def render_stat_card(companion: dict[str, Any]) -> str:
    """Render an RPG-style stat card."""
    name = companion.get("name", "???")
    species = companion["species"]
    rarity = companion["rarity"]
    shiny = companion.get("shiny", False)
    stats = companion["stats"]

    stars = RARITY_STARS[rarity]
    label = RARITY_LABELS[rarity]
    shiny_tag = " ✨ SHINY" if shiny else ""

    bar_width = 15
    w = 36  # inner width
    lines = [
        "╔" + "═" * w + "╗",
        "║" + f"{name}".center(w) + "║",
        "║" + f"{species.upper()}".center(w) + "║",
        "║" + f"{stars} {label}{shiny_tag}".center(w) + "║",
        "╠" + "═" * w + "╣",
    ]

    for stat_name in STAT_NAMES:
        val = stats[stat_name]
        filled = int(val / 100 * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        row = f" {stat_name:<10} {bar} {val:>3} "
        lines.append("║" + row.ljust(w) + "║")

    lines.append("╚" + "═" * w + "╝")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------


def _load_state() -> dict[str, Any] | None:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            return None
    return None


def _save_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _get_full_companion() -> dict[str, Any] | None:
    """Load stored state and regenerate bones from seed."""
    state = _load_state()
    if state is None:
        return None
    seed_name = state.get("seed", "")
    if not seed_name:
        return None
    # Regenerate deterministic parts
    bones = generate_companion(seed_name)
    # Merge stored soul over bones
    bones["name"] = state.get("name", bones["species"].title())
    bones["hatched_at"] = state.get("hatched_at", 0)
    bones["interactions"] = state.get("interactions", 0)
    return bones


# ---------------------------------------------------------------------------
# Reaction helpers
# ---------------------------------------------------------------------------

PET_REACTIONS: dict[str, list[str]] = {
    "duck": ["*happy quack*", "*wiggles tail feathers*", "*nuzzles your hand*"],
    "goose": ["*tolerates it*", "*HONK of approval*", "*doesn't bite... this time*"],
    "blob": ["*jiggles contentedly*", "*absorbs the pets*", "*happy vibration*"],
    "cat": ["*pretends not to enjoy it*", "*purrrrrr*", "*slow blink*"],
    "dragon": ["*tiny flame of joy*", "*rumbles happily*", "*curls tail around your hand*"],
    "octopus": ["*hugs with all tentacles*", "*changes color happily*", "*squish squish*"],
    "owl": ["*ruffles feathers*", "*hoots softly*", "*head tilts 180°*"],
    "penguin": ["*happy waddle*", "*flaps tiny wings*", "*slides on belly*"],
    "turtle": ["*slowly extends neck*", "*happy shell wiggle*", "*blinks... eventually*"],
    "snail": ["*retreats... then peeks out smiling*", "*leaves a happy slime trail*", "*antenna wiggle*"],
    "ghost": ["*your hand goes through but it's the thought that counts*", "*happy floating*", "*boo! ...of joy*"],
    "axolotl": ["*gill flutter*", "*biggest smile*", "*regenerates any sadness*"],
    "capybara": ["*maximum zen achieved*", "*sits perfectly still in bliss*", "*invites other animals to join*"],
    "cactus": ["*careful... careful... ok that was nice*", "*grows a tiny flower*", "*prickles retract slightly*"],
    "robot": ["*AFFECTION_RECEIVED: TRUE*", "*beep boop beep!*", "*ERROR: TOO_MUCH_LOVE*"],
    "rabbit": ["*thumps foot happily*", "*nose wiggle intensifies*", "*hops in a circle*"],
    "mushroom": ["*releases happy spores*", "*cap brightens*", "*underground network buzzes*"],
    "chonk": ["*maximum roundness achieved*", "*purrs like a motor*", "*rolls over for belly rubs*"],
}

HEARTS_ANIMATION = """
    ♥ ♥     ♥ ♥
   ♥   ♥ ♥   ♥
    ♥       ♥
      ♥   ♥
        ♥
"""


def _get_reaction(companion: dict[str, Any], context: str) -> str:
    """Generate a reaction based on personality, stats, and context."""
    species = companion["species"]
    stats = companion["stats"]
    personality = companion.get("personality", "")

    # Build a reaction influenced by top stat
    top_stat = max(stats, key=lambda s: stats[s])
    chaos = stats.get("CHAOS", 10)
    snark = stats.get("SNARK", 10)
    wisdom = stats.get("WISDOM", 10)

    ctx_lower = context.lower()

    # Context-aware reactions
    if any(w in ctx_lower for w in ["bug", "error", "crash", "fail", "broken"]):
        if chaos > 60:
            return f"*{species} watches the chaos with glee* This is fine. Everything is fine. 🔥"
        if wisdom > 60:
            return f"*{species} adjusts tiny glasses* Have you tried reading the error message?"
        if snark > 60:
            return f"*{species} slow claps* Another bug? Groundbreaking."
        return f"*{species} pats you reassuringly* Bugs happen to the best of us."

    if any(w in ctx_lower for w in ["test", "testing", "spec"]):
        if snark > 60:
            return f"*{species} raises an eyebrow* Tests? In THIS economy?"
        return f"*{species} nods approvingly* Testing is wisdom. {species.title()} approves."

    if any(w in ctx_lower for w in ["deploy", "ship", "release", "push"]):
        if chaos > 60:
            return f"*{species} smashes the deploy button* YOLO! 🚀"
        return f"*{species} salutes* Godspeed, brave developer. 🚀"

    if any(w in ctx_lower for w in ["refactor", "clean", "tidy"]):
        return f"*{species} sparkles* Yes! Clean code makes {species} happy! ✨"

    if any(w in ctx_lower for w in ["coffee", "break", "tired", "sleep"]):
        return f"*{species} yawns sympathetically* Maybe take a break? {species.title()} will guard the code."

    # Generic fallback based on top stat
    fallbacks = {
        "DEBUGGING": f"*{species} squints at your code* I see potential... and also a missing semicolon.",
        "PATIENCE": f"*{species} sits calmly* Take your time. Good code is worth the wait.",
        "CHAOS": f"*{species} vibrates with energy* What if we just... rewrote everything?!",
        "WISDOM": f"*{species} strokes tiny beard* Remember: premature optimization is the root of all evil.",
        "SNARK": f"*{species} sips tiny coffee* Oh, are we writing code? I thought we were writing poetry.",
    }
    return fallbacks.get(top_stat, f"*{species} watches curiously*")


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP("Homie MCP")


@mcp.tool()
def hatch_homie(name: str, seed: str = "") -> str:
    """Hatch a new homie from a name and optional seed string.

    Generates a deterministic virtual pet with species, rarity, stats, and ASCII art.
    The homie is unique to the seed (defaults to the name if no seed given).

    Args:
        name: What to name your homie
        seed: Optional seed string for deterministic generation (defaults to name)
    """
    seed_str = seed if seed else name
    companion = generate_companion(seed_str)
    companion["name"] = name
    companion["hatched_at"] = int(time.time())
    companion["interactions"] = 0

    _save_state({
        "seed": seed_str,
        "name": name,
        "hatched_at": companion["hatched_at"],
        "interactions": 0,
    })

    sprite = render_sprite(companion)
    stars = RARITY_STARS[companion["rarity"]]
    label = RARITY_LABELS[companion["rarity"]]
    shiny_tag = " ✨ SHINY!" if companion["shiny"] else ""

    return f"""🥚 *crack* ... *crack crack* ...

{sprite}

🎉 {name} has hatched!

Species: {companion['species'].title()}
Rarity: {stars} {label}{shiny_tag}
Eyes: {companion['eye']}
Hat: {companion['hat']}
Personality: {companion['personality']}

{render_stat_card(companion)}

Welcome to the world, {name}! 🎊"""


@mcp.tool()
def get_homie() -> str:
    """Get your current homie's info and ASCII art sprite.

    Shows your homie with its sprite, stats summary, and personality.
    Returns an error if no homie has been hatched yet.
    """
    companion = _get_full_companion()
    if companion is None:
        return "🥚 No homie hatched yet! Use hatch_homie to get one."

    sprite = render_sprite(companion)
    stars = RARITY_STARS[companion["rarity"]]
    shiny_tag = " ✨ SHINY" if companion["shiny"] else ""

    return f"""{sprite}

Name: {companion['name']}
Species: {companion['species'].title()}{shiny_tag}
Rarity: {stars} {RARITY_LABELS[companion['rarity']]}
Personality: {companion.get('personality', 'Mysterious')}
Interactions: {companion.get('interactions', 0)}"""


@mcp.tool()
def pet_homie() -> str:
    """Pet your homie! Returns hearts and a cute reaction.

    Increases the interaction counter and shows an affectionate response.
    """
    companion = _get_full_companion()
    if companion is None:
        return "🥚 No homie to pet! Use hatch_homie first."

    state = _load_state() or {}
    state["interactions"] = state.get("interactions", 0) + 1
    _save_state(state)

    species = companion["species"]
    rng = random.Random(time.time_ns())
    reaction = rng.choice(PET_REACTIONS.get(species, ["*happy noises*"]))

    sprite = render_sprite(companion)

    return f"""{sprite}
{HEARTS_ANIMATION}
{reaction}

{companion['name']} has been petted {state['interactions']} time{'s' if state['interactions'] != 1 else ''}! 💕"""


@mcp.tool()
def homie_react(context: str) -> str:
    """Your homie reacts to what you're working on.

    Give context about your current task and your homie will react
    in character based on its personality and stats.

    Args:
        context: Describe what you're working on (e.g., "debugging a memory leak", "writing tests")
    """
    companion = _get_full_companion()
    if companion is None:
        return "🥚 No homie to react! Use hatch_homie first."

    reaction = _get_reaction(companion, context)
    sprite = render_sprite(companion)

    return f"""{sprite}

💬 {reaction}"""


@mcp.tool()
def homie_stats() -> str:
    """Show your homie's full RPG-style stat card.

    Displays a detailed stat card with bars for each stat,
    rarity info, and species details.
    """
    companion = _get_full_companion()
    if companion is None:
        return "🥚 No homie yet! Use hatch_homie first."

    return render_stat_card(companion)


@mcp.tool()
def rename_homie(new_name: str) -> str:
    """Rename your homie.

    Args:
        new_name: The new name for your homie
    """
    state = _load_state()
    if state is None:
        return "🥚 No homie to rename! Use hatch_homie first."

    old_name = state.get("name", "???")
    state["name"] = new_name
    _save_state(state)

    companion = _get_full_companion()
    sprite = render_sprite(companion) if companion else ""

    return f"""{sprite}

✏️ {old_name} is now known as {new_name}!
{new_name} looks at you and approves. 💛"""


def main():
    mcp.run()


if __name__ == "__main__":
    main()
